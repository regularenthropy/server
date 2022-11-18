# SPDX-License-Identifier: AGPL-3.0-or-later

'''
Frea Search is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Frea Search is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Frea Search. If not, see < http://www.gnu.org/licenses/ >.

(C) 2022  Frea Search, Ablaze
                   nexryai <gnomer@tuta.io>
'''

import falcon
import falcon.asgi
import uvicorn

import requests
import json
import yaml
import tldextract
import hashlib
import asyncio
from threading import Thread
import redis

import msg
from intelligence_engine import inteli_e


class chk:
    @staticmethod
    def is_in_untrusted_domain(root_domain, domain):
        if root_domain in untrusted_domains:
            return True
        elif domain in untrusted_domains:
            return True
        else:
            return False

    @staticmethod
    def is_in_detect_words(title):
        for chk_word in detect_words:
            if chk_word in title:
                return True
        return False

    @staticmethod
    def is_in_block_words(title):
        for chk_word in block_words:
            if chk_word in title:
                return True
        return False

    @staticmethod
    def chk_title(title, content, root_domain, domain):
        if chk.is_in_detect_words(title) and chk.is_in_untrusted_domain(root_domain, domain):
            # タイトルに検出ワードが含まれているかつ信頼できないドメインの場合
            dbglog(f"detected in title ({title}) and untrusted({domain})!!!")
            return True

        if chk.is_in_block_words(title):
            # タイトルにブロックワードが含まれている場合 
            dbglog(f"Block words in title ({title}) !!!")
            return True

        if content != "NO_DATA":
            if chk.is_in_detect_words(content) and chk.is_in_untrusted_domain(root_domain, domain):
                # 説明に検出ワードが含まれているかつ信頼できないドメインの場合
                dbglog(f"detected in content ({content}) and untrusted({domain})!!!")
                return True
        
            if chk.is_in_block_words(content):
                # 説明にブロックワードが含まれている場合
                dbglog(f"Block words in content ({content}) !!!")
                return True

    @staticmethod
    def chk_domain(root_domain, domain):
        if root_domain in block_domains:
            dbglog(f"Block domain in root_domain ({root_domain}) !!!")
            return True
        elif domain in block_domains:
            dbglog(f"Block domain in domain ({domain}) !!!")
            return True
        else:
            return False

    @staticmethod
    def chk_result(search_result):
        url = search_result["url"]
        domain = search_result["parsed_url"][1]
        title = search_result["title"]

        try:
            content = search_result["content"]
        except KeyError as e:
            content = "NO_DATA"
        extracted = tldextract.extract(url)

        root_domain = "{}.{}".format(extracted.domain, extracted.suffix)
    
        if chk.chk_domain(root_domain, domain):
            return True
        elif chk.chk_title(title, content, root_domain, domain):
            return True
        else:
            dbglog(f"Passed. \ntitle: {title}\ncontent: {content}\nroot_domain: {root_domain}\ndomain: {domain}")
            return False

class search:
    async def on_get(self, req, resp):
        try:
            params = req.params
            query = params["q"]
        except:
            result = {"error": "NO_QUERY"}
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(result, ensure_ascii=False)
            return
        
        try:
            pageno = params["pageno"]
        except:
            dbglog("Use default value (pageno)")
            pageno = 1

        try:
            category = params["category"]
        except:
            dbglog("Use default value (category)")
            category = "general"

        try:
            language = params["language"]
        except:
            dbglog("Use default value (language)")
            language = "ja-JP"

        dbglog(f"query={query}")
        dbglog("Load intelligence-engine")

        try:
            inteli_e_thread = Thread(target=run_inteli_e, args=(query, inteli_e_result))
            inteli_e_thread.start()
        except Exception as e:
            msg.fatal_error(f"Exception: {e}")

        # request to SearXNG
        dbglog("send request to SearXNG.")

        try:
            upstream_request = requests.get(f"http://searxng:8080/search?q={query}&language={language}&format=json&category_{category}=on&pageno={pageno}")
            result = upstream_request.json()
        except Exception as e:
            result = {"error": "UPSTREAM_ENGINE_ERROR"}
            resp.status = falcon.HTTP_500
            resp.body = json.dumps(result, ensure_ascii=False)
            msg.fatal_error(f"UPSTREAM_ENGINE_ERROR has occurred! \nexception: {str(e)}")
            return


        i = len(result["results"]) - 1
        dbglog(f"Len of results are {i}")

        while i >= 0:
            dbglog("======================")
            dbglog(f"Checking result[{i}]")

            if chk.chk_result(result["results"][i]):
                dbglog(f"Kill result[{i}]")
                del result["results"][i]
            else:
                dbglog(f"Do not kill result[{i}]")

            i -= 1

        dbglog("Wait for inteli_e")
        try:
            while inteli_e_thread.is_alive():
                pass
            dbglog(f"inteli_e result: {inteli_e_result[0]}")
        except Exception as e:
            msg.error(f"Exception: {e}")
        

        if inteli_e_result != None:
            dbglog("Overwrite answers[0] by inteli_e_result !")
            try:
                result["answers"].insert(0, inteli_e_result[0])
            except Exception as e:
                msg.error(f"Exception: {e}")
        else:
            dbglog("No info from inteli_e")

        resp.body = json.dumps(result, ensure_ascii=False)

        result_hash = hashlib.md5(str(result).encode()).hexdigest()
        dbglog(f"result_hash: {result_hash}")
        try:
            redis.set(f"archive.{result_hash}", str(result))
            redis.set(f"queue.{result_hash}", "unprocessed")
        except Exception as e:
            msg.fatal_error(f"Database error has occurred! \nexception: {str(e)}")
        else:
            dbglog("saved to DB")


# 構成をロード
debug_mode = True

try:
    with open(f"blocklists/main.yml", "r", encoding="utf8") as yml:
        load_block_domains = yaml.safe_load(yml)
        block_domains = load_block_domains["domains"]

    with open(f"blockwords/untrusted_domains.yml", "r", encoding="utf8") as yml:
        load_untrusted_domains = yaml.safe_load(yml)
        untrusted_domains = load_untrusted_domains["domains"]

    with open(f"blockwords/block_words.yml", "r", encoding="utf8") as yml:
        load_block_words = yaml.safe_load(yml)
        block_words = load_block_words["words"]

    with open(f"blockwords/detect_words.yml", "r", encoding="utf8") as yml:
        load_detect_words = yaml.safe_load(yml)
        detect_words = load_detect_words["words"]

except Exception as e:
    msg.error("faild to load lists")
    msg.fatal_error(str(e))
    sys.exit(1)

app = falcon.asgi.App()
app.add_route('/search', search())

def dbglog(message):
    if debug_mode:
        msg.dbg(message)

if __name__ != "__main__":
    msg.info("Starting....")

    inteli_e_result = []
    
    def run_inteli_e(query, inteli_e_result):
        inteli_e_result.append(inteli_e.main(query))
        dbglog(f"@run_inteli_e inteli_e_result={inteli_e_result[0]}")
        return

    try:
        redis = redis.Redis(host='db', port=6379, db=0)
        redis.set("test", "ok")
    except Exception as e:
        msg.fatal_error(f"Faild to connect DB! \nexception: {str(e)}")
    else:
        msg.info("DB ok!")


if __name__ == "__main__":
    dbglog("Debug mode!!!!")
    uvicorn.run("worker:app", host="0.0.0.0", port=8000, workers=5, log_level="info")
