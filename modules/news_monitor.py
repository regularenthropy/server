import sys
import requests
import json
import time
import redis

import msg


def get_tsunami_info():
    api_url = 'https://api.p2pquake.net/v2/jma/tsunami?limit=1&offset=0&order=-1'

    # For debug
    # api_url = 'https://api.p2pquake.net/v2/jma/tsunami?limit=1&offset=8&order=-1'

    try:
        result = requests.get(api_url).json()
    except Exception as e:
        sys.stdout.write(str(e))
        response = {'no_tsunami': "true", 'error': "true"}
    else:
        if result[0]["cancelled"]:
            response = {'no_tsunami': "true"}
        else:
            grade = result[0]["areas"][0]["grade"]
            if grade == "Watch":
                grade_disp = "津波注意報"
            elif grade == "Warning":
                grade_disp = "津波警報"
            elif grade == "MajorWarning":
                grade_disp = "大津波警報"
            else:
                grade_disp = "津波に関する情報"

            response = {'no_tsunami': "false", 'grade': grade_disp}
    
    return response

msg.info("Starting news_monitor")

# Config redis
try:
    redis = redis.Redis(host='127.0.0.1', port=6379, db=1)
    redis.set("should_i_die", "true")
except Exception as e:
    msg.fatal_error(f"Faild to connect Redis! Exception: {str(e)}")
    sys.exit(1)
else:
    msg.info("Redis ok!")


while True:
    msg.info("Getting tsunami info...")
    _result = get_tsunami_info()
    try:
        redis.set("tsunami_status", str(_result))
    except Exception as e:
        msg.fatal_error(f"Faild to save data to redis! Exception: {str(e)}")

    time.sleep(60)
