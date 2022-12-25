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
import analyze

import time
import os
import sys
import ast
import dataset

analyzer_version = 103

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
msg.dbg(f"DB url: postgresql://{db_user}:[!DB password was hidden for security!]@{db_host}/{db_name}")

# Connect to DB
msg.info("Connecting to DB...")

try:
    db = dataset.connect(db_url)
    job_queue = db["queue"]
    reports = db["reports"]
    index = db["index"]
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


if not os.path.exists("/app/mecab/dic_installed"):
    msg.info("Download MeCab dictionary for analyze")
    _mecab_dic_dl_result = os.system("bash /app/modules/download_dic.sh")
    if _mecab_dic_dl_result != 0:
        msg.fatal_error(f"Faild to download MeCab dictionary! \nExit code: {str(_mecab_dic_dl_result)}")

while True:
    time.sleep(10)
    msg.dbg("Check job queue...")
    job_queue.delete(hash="TEST")
    job_queue.delete(query=None)
    job_queue.delete(score=None)

    for analyze_result in db['queue']:
        msg.dbg("Loading result from job queue...")
        result_dict = ast.literal_eval(analyze_result["result"])
        
        if analyze_result["analyzed"] < analyzer_version :
            for chk_result in result_dict["results"]:

                _chk_title = chk_result['title']
                _chk_url = chk_result['url']
                try:
                    _chk_content = chk_result['content']
                except KeyError:
                    _chk_content = None

                msg.dbg(f"Check result...url: {_chk_url}  title: {_chk_title}")
                if analyze.chk_text(_chk_title) == 1:
                    msg.info(f"Suspicious site detected! url: {_chk_url}  title: {_chk_title}")
                    try:
                        reports.insert(dict(url=_chk_url, text=_chk_title, reason="title", analyzer_version=analyzer_version))
                        db.commit()
                    except Exception as e:
                        msg.fatal_error(f"Faild to save report to DB. \nException{e}")
                        db.rollback()

                if _chk_content != None:
                    if analyze.chk_text(_chk_content) == 1:
                        msg.info(f"Suspicious site detected! url: {_chk_url}  content:{_chk_content}")
                        try:
                            reports.insert(dict(url=_chk_url, text=_chk_content, reason="content", analyzer_version=analyzer_version))
                            db.commit()
                        except Exception as e:
                            msg.fatal_error(f"Faild to save report to DB. \nException{e}")
                            db.rollback()

                time.sleep(0.1)
        
        if len(result_dict["unresponsive_engines"]) >= 4:
            job_queue.delete(hash=analyze_result["hash"])
            break

        
        # 既にインデックスに存在する項目を登録する場合、新たに検索を行い、応答しないエンジンが少ない方が優先されどちらも応答しないエンジンの数が同じなら新しい方を優先する。また何回も検索されているならスコアを上げる。
        try:
            if analyze_result["query"] != None:
                msg.info(f"query: {analyze_result['query']}")

                if index.count(query=analyze_result['query']) > 0:
                    msg.warn(f"Same query found in index! {index.count(query=analyze_result['query'])}")
                    for _old_index in index.find(query=analyze_result['query']):
                        _old_index_result = ast.literal_eval(_old_index["result"])
                        _old_index_score = _old_index["score"]
                        msg.dbg(f"Old result unresponsive_engines: {_old_index_result['unresponsive_engines']} Result unresponsive_engines: {result_dict['unresponsive_engines']}")

                        if len(_old_index_result["unresponsive_engines"]) >= len(result_dict["unresponsive_engines"]) :
                            msg.info("Update old result in the index!")
                            index.delete(query=analyze_result["query"])
                            index.insert(dict(query=analyze_result["query"], result=analyze_result["result"], score=_old_index_score + 1))
                        else:
                            msg.info("Do not update old result in the index!")
                            index.update(dict(query=analyze_result["query"], result=analyze_result["result"], score=_old_index_score + 1), ["query"])

                else:
                    msg.info("Add to index")
                    index.insert(dict(query=analyze_result["query"], result=analyze_result["result"], score=1))
                
                db.commit()

            else:
                msg.warn(f"Skipping index creation because query is None.")
            
            job_queue.delete(hash=analyze_result["hash"])
            db.commit()

        except KeyError as e:
            msg.warn(f"Skipping index creation because {e} is undefined.")
        except Exception as e:
            msg.fatal_error(f"Faild to save index to DB. \nException: {e}")
            db.rollback()
