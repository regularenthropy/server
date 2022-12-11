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

import os
import sys
import requests
import json
import ast
import yaml
import tldextract
import hashlib
import asyncio
from threading import Thread
import dataset
import redis
from html import escape
import urllib.parse
import time

import msg
import inteli_e


encode_query = urllib.parse.quote

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
            msg.dbg(f"detected in title ({title}) and untrusted({domain})!!!")
            return True

        if chk.is_in_block_words(title):
            # タイトルにブロックワードが含まれている場合 
            msg.dbg(f"Block words in title ({title}) !!!")
            return True

        if content != "NO_DATA":
            if chk.is_in_detect_words(content) and chk.is_in_untrusted_domain(root_domain, domain):
                # 説明に検出ワードが含まれているかつ信頼できないドメインの場合
                msg.dbg(f"detected in content ({content}) and untrusted({domain})!!!")
                return True
        
            if chk.is_in_block_words(content):
                # 説明にブロックワードが含まれている場合
                msg.dbg(f"Block words in content ({content}) !!!")
                return True

    @staticmethod
    def chk_domain(root_domain, domain):
        if root_domain in block_domains:
            msg.dbg(f"Block domain in root_domain ({root_domain}) !!!")
            return True
        elif domain in block_domains:
            msg.dbg(f"Block domain in domain ({domain}) !!!")
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
            msg.dbg(f"Passed. \ntitle: {title}\ncontent: {content}\nroot_domain: {root_domain}\ndomain: {domain}")
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
            msg.dbg("Use default value (pageno)")
            pageno = 1

        try:
            category = params["category"]
        except:
            msg.dbg("Use default value (category)")
            category = "general"

        try:
            language = params["language"]
        except:
            msg.dbg("Use default value (language)")
            language = "ja-JP"

        msg.dbg(f"query={query}")

        query_encoded = encode_query(query)
        msg.dbg(f"query_encoded={query_encoded}")

        msg.dbg("Load intelligence-engine")

        try:
            inteli_e_result = []
            inteli_e_thread = Thread(target=run_inteli_e, args=(query, inteli_e_result))
            inteli_e_thread.start()
        except Exception as e:
            msg.fatal_error(f"Exception: {e}")

        # Check cache
        if redis.exists(f"cache.{query_encoded}"):
            msg.info("Use cache !")
            cache_used = True
            try:
                cache_str = redis.get(f"cache.{query_encoded}").decode("UTF-8")
                result = ast.literal_eval(cache_str)
            except Exception as e:
                result = {"error": "CACHE_ERROR"}
                resp.status = falcon.HTTP_500
                resp.body = json.dumps(result, ensure_ascii=False)
                msg.fatal_error(f"CACHE_ERROR has occurred! \nexception: {str(e)}")
                return
        else:
            # request to SearXNG
            msg.dbg("send request to SearXNG.")
            cache_used = False
            try:
                upstream_request = requests.get(f"http://127.0.0.1:8888/search?q={query_encoded}&language={language}&format=json&category_{category}=on&pageno={pageno}")
                result = upstream_request.json()
            except Exception as e:
                result = {"error": "UPSTREAM_ENGINE_ERROR"}
                resp.status = falcon.HTTP_500
                resp.body = json.dumps(result, ensure_ascii=False)
                msg.fatal_error(f"UPSTREAM_ENGINE_ERROR has occurred! \nexception: {str(e)}")
                return


        i = len(result["results"]) - 1
        msg.dbg(f"Len of results are {i}")

        while i >= 0:
            msg.dbg("======================")
            msg.dbg(f"Checking result[{i}]")

            if chk.chk_result(result["results"][i]):
                msg.dbg(f"Kill result[{i}]")
                del result["results"][i]
            else:
                msg.dbg(f"Do not kill result[{i}]")

            i -= 1

        msg.dbg("Wait for inteli_e")
        try:
            while inteli_e_thread.is_alive():
                pass
            msg.dbg(f"inteli_e result: {inteli_e_result[0]}")
        except Exception as e:
            msg.error(f"Exception: {e}")
        
        try:
            if result["answers"][0] != None:
                result["answers"][0] = {'type': 'answer', 'answer': result["answers"][0]}
        except Exception as e:
            msg.dbg("No origin answer")

        if inteli_e_result[0] != None:
            msg.dbg("Overwrite answers[0] by inteli_e_result !")
            try:
                result["answers"].insert(0, inteli_e_result[0])
            except Exception as e:
                msg.error(f"Exception: {e}")
        else:
            msg.dbg("No info from inteli_e")

        # Anti XSS
        try:
            if  params["no_escape"] != "false":
                escape_text = True
            else:
                escape_text = False
        except:
            escape_text = True

        try:
            if escape_text:
                escape_counts = 0
                
                for escape_result in result["results"]:
                    result["results"][escape_counts]["title"] = escape(escape_result["title"])
                    if "content" in escape_result:
                        result["results"][escape_counts]["content"] = escape(escape_result["content"])
                    
                    escape_counts += 1

        except Exception as e:
            msg.fatal_error(f"The escape of the results failed. The request failed for security reasons. \nException: {e}")
            result = {"error": "RESULT_ESCAPE_ERROR"}
        
        # Set number_of_results and time_stamp
        result["number_of_results"] = len(result["results"])

        # make response
        resp.body = json.dumps(result, ensure_ascii=False)

        # Make cache
        if len(result["unresponsive_engines"]) < 2 and not cache_used:
            msg.info("Make cache !")
            try:
                redis.set(f"cache.{query_encoded}", str(result))
                redis.expire(f"cache.{query_encoded}", 21600)
            except Exception as e:
                msg.fatal_error(f"Cache generation failed! \nexception: {str(e)}")
            else:
                msg.dbg("cache saved")

        # Archive result to DB
        if os.environ['FREA_ACTIVE_MODE'] == "true" and not cache_used :
            del result["query"]
            result_hash = hashlib.md5(str(result).encode()).hexdigest()
            msg.dbg(f"result_hash: {result_hash}")
            try:
                job_queue.insert(dict(hash=result_hash, result=str(result), archived=False, analyzed=0))
                db.commit()
            except Exception as e:
                db.rollback()
                msg.fatal_error(f"Database error has occurred! \nexception: {str(e)}")
            else:
                msg.dbg("saved to DB")


class status:
    async def on_get(self, req, resp):
        resp.body =  "{\"status\": \"OK\"}"


class fckputin:
    async def on_get(self, req, resp):
        resp.body =  "{\"message\": \"FCKPUTIN\"}"


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
app.add_route('/', status())
app.add_route('/search', search())
app.add_route('/health', status())
app.add_route('/wp-admin', fckputin())


if __name__ != "__main__":
    msg.info("Starting....")

    inteli_e_result = []
    
    def run_inteli_e(query, inteli_e_result):
        inteli_e_result.append(inteli_e.main(query))
        msg.dbg(f"@run_inteli_e inteli_e_result={inteli_e_result[0]}")
        return

    # Config redis
    try:
        redis = redis.Redis(host='127.0.0.1', port=6379, db=1)
    except Exception as e:
        msg.fatal_error(f"Faild to connect DB! \nexception: {str(e)}")
    else:
        msg.info("Redis ok!")


    # Load DB config from env
    if os.environ['FREA_ACTIVE_MODE'] == "true":
        msg.info("Loading DB config...")
        try:
            db_host = os.environ['POSTGRES_HOST']
            db_name = os.environ['POSTGRES_DB']
            db_user = os.environ['POSTGRES_USER']
            db_passwd = os.environ['POSTGRES_PASSWD']
        except KeyError as e:
            msg.fatal_error(f"Faild to load DB config! \nundefined environment variable: {str(e)}")
            sys.exit(1)

        # Connect to DB
        msg.info("Connecting to DB...")

        try:
            db = dataset.connect(f"postgresql://{db_user}:{db_passwd}@{db_host}/{db_name}")
            job_queue = db["queue"]
        except Exception as e:
            msg.fatal_error(f"Faild to connect DB! \nexception: {str(e)}")
            sys.exit(1)
        else:
            msg.info("DB connection is OK !")


if __name__ == "__main__":
    msg.dbg("Debug mode!!!!")
    uvicorn.run("worker:app", host="0.0.0.0", port=8889, workers=5, log_level="info")
