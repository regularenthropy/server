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

from modules import msg

import os
import sys
from pyfiglet import Figlet
import subprocess
import threading
import string
import secrets


aa = Figlet(font="slant")
welcome_aa = aa.renderText("Frea Search")

print("Frea Search API Server ver.4.12 (codename: Crystal Rain)\n")
print(welcome_aa)
print("\n(c) 2022 nexryai\nThis program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.\n\n")

try:
    debug_mode = os.environ['FREA_DEBUG_MODE']
except KeyError:
    msg.warn("FREA_DEBUG_MODE is undefined.")
    os.environ['FREA_DEBUG_MODE'] = "false"


try:
    use_active_mode = os.environ['POSTGRES_HOST']
except KeyError:
    msg.fatal_error("PostgreSQL is not configured.")
    sys.exit(1)
else:
    msg.info("PostgreSQL is configured.")
    os.environ['FREA_ACTIVE_MODE'] = "true"


# Set system secret key
msg.info("Generate a secret key...")
chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
os.environ['FREA_SECRET'] = ''.join(secrets.choice(chars) for i in range(20))


def start_nginx():
    msg.info("Starting nginx....")
    subprocess.call(["python3", "-u", "modules/nginx.py"])

def start_search_api_server():
    msg.info("Starting search API server workers....")
    subprocess.call(["python3", "-u", "modules/worker.py"])

def start_searxng():
    msg.info("Starting SearXNG....")
    subprocess.call(["python3", "-u", "modules/searx.py"])

def start_redis():
    msg.info("Starting redis....")
    subprocess.call(["python3", "-u", "modules/redis_server.py"])

def start_job_manager():
    subprocess.call(["python3", "-u", "modules/job_manager.py"])

def start_index_manager():
    subprocess.call(["python3", "-u", "modules/index_manager.py"])

def start_news_monitor():
    subprocess.call(["python3", "-u", "modules/news_monitor.py"])


# Start nginx
nginx_server_thread = threading.Thread(target=start_nginx)
nginx_server_thread.start()

# Start API server
search_server_thread = threading.Thread(target=start_search_api_server)
search_server_thread.start()

# Start searx
searx_server_thread = threading.Thread(target=start_searxng)
searx_server_thread.start()

# Start redis
redis_server_thread = threading.Thread(target=start_redis)
redis_server_thread.start()

# Start news_monitor
news_monitor_thread = threading.Thread(target=start_news_monitor)
news_monitor_thread.start()


if os.environ['FREA_ACTIVE_MODE'] == "true" :
    msg.info("Starting job manager...")
    job_manager_thread = threading.Thread(target=start_job_manager)
    job_manager_thread.start()
    
    msg.info("Starting index manager...")
    index_manager_thread = threading.Thread(target=start_index_manager)
    index_manager_thread.start()

search_server_thread.join()
