import falcon
import requests
import json
import yaml

import msg

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
            upstream_request = requests.get(f"http://localhost:8888/search?q={query}&format=json")
        except Exception as e:
            result = {"error": "UPSTREAM_ENGINE_ERROR"}
            resp.status = falcon.HTTP_500
            resp.body = json.dumps(result, ensure_ascii=False)
            msg.fetal_error(f"UPSTREAM_ENGINE_ERROR has occurred! \nexception: {str(e)}")
            return

        result = upstream_request.json()
        resp.body = json.dumps(result, ensure_ascii=False)
        
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
    msg.error("[ERROR] faild to load lists")
    msg.fetal_error(str(e))
    sys.exit(1)

app = falcon.API()
app.add_route('/search', search())

if __name__ == "__main__":
    msg.info("Starting server....")
    from wsgiref import simple_server
    httpd = simple_server.make_server("127.0.0.1", 8000, app)
    httpd.serve_forever()
