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

import msg
from pyfiglet import Figlet
import subprocess
import threading

aa = Figlet(font="slant")
welcome_aa = aa.renderText("Frea Search")

print("Frea Search core API Server ver.3.10\n")
print(welcome_aa)
print("\n(c) 2022 nexryai\nThis program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.\n\n")

def start_nginx():
    msg.info("Starting nginx....")
    subprocess.call(["python3", "nginx.py"])

def start_search_api_server():
    msg.info("Starting search API server workers....")
    subprocess.call(["python3", "worker.py"])

def start_searxng():
    msg.info("Starting SearXNG....")
    subprocess.call(["python3", "searx.py"])

def start_redis():
    msg.info("Starting redis....")
    subprocess.call(["python3", "redis_server.py"])

def start_job_manager():
    subprocess.call(["python3", "job_manager.py"])

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

msg.info("Starting job manager...")
job_manager_thread = threading.Thread(target=start_job_manager)
job_manager_thread.start()

search_server_thread.join()