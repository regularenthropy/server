# SPDX-License-Identifier: AGPL-3.0-or-later

import sys
import os
import requests
import json
import ast

import redis

import msg


# Config redis
try:
    redis = redis.Redis(host='127.0.0.1', port=6379, db=1)
except Exception as e:
    msg.fatal_error(f"Faild to connect Redis! Exception: {str(e)}")
    sys.exit(1)
else:
    msg.info("Redis ok!")


def get_weather(query):
    import pygeonlp.api
    import datetime
    from zoneinfo import ZoneInfo

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0'
    header = {
	    'User-Agent': user_agent
    }

    pygeonlp.api.init()
    get_location = pygeonlp.api.geoparse(format(query))

    try:
        get_location[0]['geometry']['coordinates']
    except:
        return "NO_DATA"
        
    lon = get_location[0]['geometry']['coordinates'][0]
    lat = get_location[0]['geometry']['coordinates'][1]
    location_name = get_location[0]['properties']['surface']
        
    # get weather data from met norway
    met_api_request_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=" + str(lat) + "&lon=" + str(lon)
    met_api_response = requests.get (met_api_request_url,  headers=header)
    weather_json = met_api_response.json()

    get_date = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
    now_date = get_date.strftime('%Y%m%d%H')

    get_d2_date = datetime.timedelta(days = 1)
    get_d3_date = datetime.timedelta(days = 2)

    date_year = get_date.year
    date_month = get_date.month
    date_day = get_date.day
    date_hour = get_date.hour

    date_d2_month = (get_date + get_d2_date).month
    date_d2_day = (get_date + get_d2_date).day
    date_d3_month = (get_date + get_d3_date).month
    date_d3_day = (get_date + get_d3_date).day

    # 翌日9時までの時間(h)
    d2_key =  24 + 9 - date_hour
    d3_key =  48 + 9 - date_hour

    weather = weather_json['properties']['timeseries'][0]['data']['next_12_hours']['summary']['symbol_code']
    temp_now = weather_json['properties']['timeseries'][0]['data']['instant']['details']['air_temperature']

    weather_d2 = weather_json['properties']['timeseries'][d2_key]['data']['next_12_hours']['summary']['symbol_code']
    weather_d3 = weather_json['properties']['timeseries'][d3_key]['data']['next_12_hours']['summary']['symbol_code']

    def get_max_temp(day):
        max_temp = -99999
        for i in range(23):
            day_index = i + (24 * day - date_hour)
            i_temp = weather_json['properties']['timeseries'][day_index]['data']['instant']['details']['air_temperature']
            if max_temp < i_temp:
                max_temp = i_temp

        return max_temp

    def get_min_temp(day):
        min_temp = 99999
        for i in range(23):
            day_index = i + (24 * day - date_hour)
            i_temp = weather_json['properties']['timeseries'][day_index]['data']['instant']['details']['air_temperature']
            if min_temp > i_temp:
                min_temp = i_temp
            
        return min_temp

    maxtemp_d2 = get_max_temp(1)
    mintemp_d2 = get_min_temp(1)
    maxtemp_d3 = get_max_temp(2)
    mintemp_d3 = get_min_temp(2)
    
    def weather_icon_name_to_japanese(name):
        if "thunder" in name:
            text = "雷を伴う"
        else:
            text = ""
        
        if "clearsky" in name:
            text = "快晴"       
        elif "fair" in name:
            text += "晴れ"
        elif "fog" in name:
            text = "霧"
        # 雪
        elif "lightsnow" in name or "lightssnow" in name:
            text += "弱い雪"
        elif "heavysnow" in name:
            text += "大雪"
        elif "snow" in name:
            text += "雪"
        # 雨
        elif "lightrain" in name:
            text += "小雨"
        elif "heavyrain" in name:
            text += "強雨"
        elif "rain" in name:
            text += "雨"
        #みぞれ
        elif "lightsleet" in name or "lightssleet" in name:
            text += "弱いみぞれ"
        elif "heavysleet" in name:
            text += "強いみぞれ"
        elif "sleet" in name:
            text += "みぞれ"
        # 曇り
        elif "partlycloudy" in name:
            text += "薄曇り"
        elif name == "cloudy":
            text = "曇り"
        
        return text
        

    response = {'weather': weather_icon_name_to_japanese(weather), 'temp_now': temp_now, 'weather_d2': weather_icon_name_to_japanese(weather_d2), 'weather_d3': weather_icon_name_to_japanese(weather_d3), 'maxtemp_d2': maxtemp_d2, 'mintemp_d2': mintemp_d2, 'maxtemp_d3': maxtemp_d3, 'mintemp_d3': mintemp_d3, 'd2_disp':  str(date_d2_month) + '/' + str(date_d2_day), 'd3_disp':  str(date_d3_month) + '/' + str(date_d3_day), 'location_name': location_name} 
    
    del pygeonlp.api
    del datetime
    del ZoneInfo

    return response


def get_train_info(query):
    import feedparser
    feed_data = feedparser.parse('http://api.tetsudo.com/traffic/atom.xml')

    for entry in feed_data.entries:
        train_name = entry.title
        info_url = entry.link

        if query in entry.title:
            result = entry.link
            break
        else:
            result = "NO_DATA"

    del feedparser
    return result


def get_tsunami_info():
    try:
        tsunami_result_str = redis.get("tsunami_status").decode("UTF-8")
        tsunami_result = ast.literal_eval(tsunami_result_str)
    except Exception as e:
        msg.error(f"Faild to get data from redis! Exception: {str(e)}")
        tsunami_result = {'no_tsunami': "true", 'error': "true"}
    
    return tsunami_result


def main(query):
    msg.dbg("called inteli_e")

    msg.dbg("Check tsunami_info...")
    tsunami_info = get_tsunami_info()

    if tsunami_info["no_tsunami"] != "true":
        message = "警告: 現在、一部の沿岸地域に" + tsunami_info["grade"] + "が発表されています。"
        return {'type': 'warning', 'answer': message}

    if '遅延' in query:
        msg.dbg("Check train information....")

        if '　' in query:
            query_split = query.split("　")
            train_name = query_split[0]
        else:
            query_split = query.split()
            train_name = query_split[0]

        result = get_train_info(train_name)

        if result != "NO_DATA":
            message = '"' + train_name + '"の運行情報があります。'
            return {'type': 'answer', 'answer': message, 'url': result}

    if '天気' in query:
        msg.dbg("Check weather info....")

        result = get_weather(query)

        msg.dbg(f"Weather result: {result}")

        if result == "NO_DATA":
            msg.dbg("Weather result is NO_DATA")
            return None

        message=f"今後の{result['location_name']}の天気は{result['weather']}、現在の気温は{result['temp_now']}℃です。明日（{result['d2_disp']}）は最高気温{result['maxtemp_d2']}℃で{result['weather_d2']}、明後日（{result['d3_disp']}）は最高気温{result['maxtemp_d3']}℃で{result['weather_d2']}になる予想です。"
        '''
        weather_data = {'type': 'weather',  'answer': message, 
                        'weather': 'MET Norway', 
                        'hide_icon': 'true',
                        'weather_icon': result['weather'],
                        'weather_temp': result['temp_now'],
                        'weather_icon_2d': result['weather_d2'],
                        'weather_temp_2d': result['maxtemp_d2'],
                        'weather_icon_3d': result['weather_d3'],
                        'weather_temp_3d': result['maxtemp_d3'],
                        'd2_disp': result['d2_disp'],
                        'd3_disp': result['d3_disp']}
        '''
        weather_data = {'type': 'answer', 'answer': message}
        return weather_data

    if 'コロナ' in query:
        w_message = "新型コロナウイルス感染症に関する正しい情報をお求めの場合は、厚生労働省のwebサイトをご確認ください。"
        link = "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000164708_00001.html"

    if 'ワクチン' in query:
        w_message = "新型コロナワクチンに関する信頼できる情報をお求めの場合は、公的機関のページが役に立つでしょう。"
        link = "https://v-sys.mhlw.go.jp/"

    if 'ウクライナ' in query:
        w_message = "ユニセフの緊急募金に参加しウクライナを支援できます。"
        link = "https://www.unicef.or.jp/kinkyu/ukraine/"
    
    if query == 'ping':
        w_message = "pong!"

    if query == '発狂':
        w_message = "ヌァァァァァァァァァァァァァァァァァァァァァァァァァァァァァァァァァァンンンンオオオオンンオンオンオンオンンンンンンンンン゛ン゛！！！！！！！！！！！！！！！！"

    if 'w_message' in locals():
        if 'link' in locals():
            warn_msg = {'type': 'answer', 'answer': w_message, 'url': link}
        else:
            warn_msg = {'type': 'answer', 'answer': w_message}
        
        return warn_msg
    
    msg.dbg("No info!")
    return None
