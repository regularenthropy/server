import os
import sys

import redis
import yaml

import msg

try:
    with open("blocklists/main.yml", "r", encoding="utf8") as yml:
        load_block_domains = yaml.safe_load(yml)
        block_domains = load_block_domains["domains"]

    with open("blockwords/untrusted_domains.yml", "r", encoding="utf8") as yml:
        load_untrusted_domains = yaml.safe_load(yml)
        untrusted_domains = load_untrusted_domains["domains"]

except Exception as e:
    msg.error("faild to load lists")
    msg.fatal_error(str(e))
    sys.exit(1)

# Config redis
try:
    redis = redis.Redis(host='127.0.0.1', port=6379, db=1)
except Exception as e:
    msg.fatal_error(f"Faild to connect DB! Exception: {str(e)}")
    sys.exit(1)
else:
    msg.dbg("Redis ok!")

msg.info(f"Loading {len(block_domains)} block_domains...")
for _block_domain in block_domains :
    redis.set(f"blocklists/domain/{_block_domain}", "all")

msg.info(f"Loading {len(untrusted_domains)} untrusted_domains...")
for _untrusted_domain in untrusted_domains :
    redis.set(f"blocklists/untrusted/{_untrusted_domain}", "all")

sys.exit(0)
