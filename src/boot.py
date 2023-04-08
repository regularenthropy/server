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

(C) 2022-2023  Frea Search, Ablaze
                   nexryai <gnomer@tuta.io>
'''

import os
import sys

from pyfiglet import Figlet
import threading
import multiprocessing
import string
import secrets
import time
import requests
import redis

from modules import core
msg = core.log()


import service

news_service = service.newsService()

aa = Figlet(font="slant")
welcome_aa = aa.renderText("Frea Search")

print("Frea Search API Server ver.4.31 (codename: Day Cat)\n")
print(welcome_aa)
print("\n(c) 2022-2023 nexryai\nThis program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.\n\n")


# Config and check redis
msg.info("Checking redis...")

try:
    redis = redis.Redis(host=core.config.redis.host, port=6379, db=1)
    if not redis.exists("should_i_die"):
        redis.set("should_i_die", "false")
except Exception as e:
    msg.fatal_error(f"Faild to connect Redis! Exception: {str(e)}")
    sys.exit(1)
else:
    pass


# Set system secret key
msg.info("Generate a secret key...")
chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
os.environ['FREA_SECRET'] = ''.join(secrets.choice(chars) for i in range(20))


# Start API server
#search_server_thread = multiprocessing.Process(target=start_search_api_server)
#search_server_thread.start()

# Start news_monitor
news_monitor_thread = multiprocessing.Process(target=news_service.start())
news_monitor_thread.start()


msg.info("Starting job manager...")
#job_manager_thread = multiprocessing.Process(target=start_job_manager)
#job_manager_thread.start()

msg.info("Starting index manager...")
#index_manager_thread = multiprocessing.Process(target=start_index_manager)
#index_manager_thread.start()


time.sleep(60)

# Run blocklists_loader.py
_blocklists_loader_result = os.system("python3 -u modules/blocklists_loader.py")
if _blocklists_loader_result != 0:
    msg.fatal_error(f"Faild to load blocklists! \nExit code: {str(_blocklists_loader_result)}")
    sys.exit(1)


time.sleep(10)

msg.info("Starting error monitor...")    

def suicide():
    #FIXME: なんかもっと良い書き方あると思うけどどっかで失敗しても処理を続ける方法がこれしか分からん。
    
    try:
        search_server_thread.terminate()
    except:
        pass
    
    try:
        news_monitor_thread.terminate()
    except:
        pass
    
    try:
        job_manager_thread.terminate()
    except:
        pass
    
    try:
        index_manager_thread.terminate()
    except:
        pass


while True:
    try:
        should_i_die = redis.get("should_i_die").decode("UTF-8")
        if should_i_die != "false" :
            try:
                should_i_die_reporter = redis.get("should_i_die.reporter").decode("UTF-8")
            except:
                should_i_die_reporter = "unknown"

            msg.error(f"Monitoring error. A critical error was reported by another module ({should_i_die_reporter}).")
            suicide()
            sys.exit(1)

        # サーバーメトリクス
        try:
            total_search_req = int(redis.get("metrics.total_search_req"))
            archive_used = int(redis.get("metrics.archive_used"))
            cache_used = int(redis.get("metrics.cache_used"))
        
            archive_hit_probability = archive_used / total_search_req * 100
            cache_hit_probability = cache_used / total_search_req * 100
        
            msg.info(f"System metrics: total_search_req={str(total_search_req)} archive_hit_probability={archive_hit_probability}% cache_hit_probability={cache_hit_probability}%")
        except TypeError:
            pass

    except Exception as e:
        msg.error(f"Monitoring error. Failed to read value from Redis. Exit.  (Exception: {e})")
        suicide()
        sys.exit(1)
    
    time.sleep(30)
