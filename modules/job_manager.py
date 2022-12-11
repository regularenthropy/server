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

import time
import os
import sys
import dataset

# Load DB config from env
msg.info("Loading DB config...")

try:
    db_host = os.environ['POSTGRES_HOST']
    db_name = os.environ['POSTGRES_DB']
    db_user = os.environ['POSTGRES_USER']
    db_passwd = os.environ['POSTGRES_PASSWD']
except KeyError as e:
    msg.fatal_error(f"Faild to load DB config! \nundefined environment variable: {str(e)}")
    sys.exit(1)

db_url = f"postgresql://{db_user}:{db_passwd}@{db_host}/{db_name}"
msg.dbg(f"DB url: {db_url}")

# Connect to DB
msg.info("Connecting to DB...")

try:
    db = dataset.connect(db_url)
    job_queue = db["queue"]
except Exception as e:
    msg.fatal_error(f"Faild to connect DB! \nexception: {str(e)}")
    sys.exit(1)
else:
    msg.info("DB connection is OK !")

try:
    job_queue.insert(dict(hash="TEST", result="{\"status\": \"OK\"}", archived=True, analyzed=1))
    db.commit()
except Exception as e:
    msg.fatal_error(f"DB error! \nexception: {str(e)}")
    db.rollback()
    sys.exit(1)

while True:
    time.sleep(10)
    #queue = redis.scan_iter("queue.*")
    #msg.info(f"queue: {str(queue)}")