import falcon
import requests
import json
import yaml
import tldextract

import msg


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
    def on_get(self, req, resp):
        try:
            params = req.params
            query = params["q"]
        except:
            result = {"error": "NO_QUERY"}
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(result, ensure_ascii=False)
            return

        try:
            dbglog("send request to SearXNG.")
            dbglog(f"query={query}")
            upstream_request = requests.get(f"http://localhost:8888/search?q={query}&format=json")
        except Exception as e:
            result = {"error": "UPSTREAM_ENGINE_ERROR"}
            resp.status = falcon.HTTP_500
            resp.body = json.dumps(result, ensure_ascii=False)
            msg.fetal_error(f"UPSTREAM_ENGINE_ERROR has occurred! \nexception: {str(e)}")
            return

        result = upstream_request.json()

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

        resp.body = json.dumps(result, ensure_ascii=False)


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
    msg.fetal_error(str(e))
    sys.exit(1)

app = falcon.API()
app.add_route('/search', search())

def dbglog(message):
    if debug_mode:
        msg.dbg(message)

if __name__ == "__main__":
    msg.info("Starting server....")
    dbglog("Debug mode!!!!")

    from wsgiref import simple_server
    httpd = simple_server.make_server("127.0.0.1", 8000, app)
    httpd.serve_forever()
