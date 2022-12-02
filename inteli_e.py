# SPDX-License-Identifier: AGPL-3.0-or-later

import sys
import chardet
import os
import datetime
from zoneinfo import ZoneInfo
import requests
import json
import ast
import urllib
import pygeonlp.api
import feedparser

import msg

debug_mode = True

def dbglog(message):
    if debug_mode:
        msg.dbg(message)



def get_weather(query):
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

    response = {'weather': weather, 'temp_now': temp_now, 'weather_d2': weather_d2, 'weather_d3': weather_d3, 'maxtemp_d2': maxtemp_d2, 'mintemp_d2': mintemp_d2, 'maxtemp_d3': maxtemp_d3, 'mintemp_d3': mintemp_d3, 'd2_disp':  str(date_d2_month) + '/' + str(date_d2_day), 'd3_disp':  str(date_d3_month) + '/' + str(date_d3_day)} 
    return response


def get_train_info(query):
    feed_data = feedparser.parse('http://api.tetsudo.com/traffic/atom.xml')

    for entry in feed_data.entries:
        train_name = entry.title
        info_url = entry.link

        if query in entry.title:
            result = entry.link
            break
        else:
            result = "NO_DATA"

    return result


def get_tsunami_info():
    api_url = 'https://api.p2pquake.net/v2/jma/tsunami?limit=1&offset=0&order=-1'

    # For debug
    #api_url = 'https://api.p2pquake.net/v2/jma/tsunami?limit=1&offset=8&order=-1'

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


def main(query):
    dbglog("called inteli_e")

    dbglog("Check tsunami_info...")
    tsunami_info = get_tsunami_info()

    if tsunami_info["no_tsunami"] != "true":
        message = "警告: 現在、一部の沿岸地域に" + tsunami_info["grade"] + "が発表されています。"
        dbglog("Done!")
        return {'type': 'tsunami_warn', 'message': message, 'tsunami': 'true', 'hide_icon': 'true'}

    if '遅延' in query:
        dbglog("Check train information....")

        if '　' in query:
            query_split = query.split("　")
            train_name = query_split[0]
        else:
            query_split = query.split()
            train_name = query_split[0]

        result = get_train_info(query)

        if result != "NO_DATA":
            message = "/"" + train_name + "/"が遅延しています。"
            dbglog("Done!")
            return {'type': 'train_delay', 'message': message, 'url': result}

    if '天気' in query:
        dbglog("Check weather info....")

        result = get_weather(query)

        dbglog(f"Weather result: {result}")

        if result == "NO_DATA":
            dbglog("Weather result is NO_DATA")
            return None

        message="現在の天気: " + result['weather']

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

    if 'w_message' in locals():
        if 'link' in locals():
            warn_msg = {'type': 'answer', 'answer': w_message, 'url': link}
        else:
            warn_msg = {'type': 'answer', 'answer': w_message}
        
        return warn_msg
    
    dbglog("No info!")
    return None