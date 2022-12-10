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
import redis
import time

msg.info("Connecting to DB...")

try:
    redis = redis.Redis(host='db', port=6379, db=0)
    redis.set("test", "ok")
except Exception as e:
    msg.fatal_error(f"Faild to connect DB! \nexception: {str(e)}")
else:
    msg.info("DB ok!")

while True:
    time.sleep(10)
    queue = redis.scan_iter("queue.*")
    #msg.info(f"queue: {str(queue)}")