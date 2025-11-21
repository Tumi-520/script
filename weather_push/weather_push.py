import os
import requests
import json
from datetime import datetime

# Configuration
# Get these from environment variables (GitHub Secrets)
QWEATHER_KEY = os.environ.get("QWEATHER_KEY")
QMSG_KEY = os.environ.get("QMSG_KEY")
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
WXPUSHER_APP_TOKEN = os.environ.get("WXPUSHER_APP_TOKEN") # New: WXPusher
WXPUSHER_UID = os.environ.get("WXPUSHER_UID") # New: WXPusher User ID
CITY_NAME = os.environ.get("CITY", "Shenzhen")

# QWeather API Endpoints
# GeoAPI to get City ID
GEO_API_URL = "https://geoapi.qweather.com/v2/city/lookup"
# Weather API (Dev/Free tier)
WEATHER_API_URL = "https://devapi.qweather.com/v7/weather/3d"
INDICES_API_URL = "https://devapi.qweather.com/v7/indices/1d"

def get_city_id(city_name, api_key):
    """Get City ID from City Name"""
    params = {
        "location": city_name,
        "key": api_key
    }
    try:
        response = requests.get(GEO_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data["code"] == "200" and data["location"]:
            return data["location"][0]["id"]
        else:
            print(f"Error getting city ID: {data}")
            return None
    except Exception as e:
        print(f"Exception getting city ID: {e}")
        return None

def get_weather(city_id, api_key):
    """Get 3-day weather forecast (we only need today)"""
    params = {
        "location": city_id,
        "key": api_key
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data["code"] == "200":
            return data["daily"][0] # Return today's forecast
        else:
            print(f"Error getting weather: {data}")
            return None
    except Exception as e:
        print(f"Exception getting weather: {e}")
        return None

def get_indices(city_id, api_key):
    """Get Life Indices (Dressing, UV, etc.)"""
    params = {
        "location": city_id,
        "key": api_key,
        "type": "1,3" # 1=Sport, 3=Dressing
    }
    try:
        response = requests.get(INDICES_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data["code"] == "200":
            return data["daily"]
        else:
            print(f"Error getting indices: {data}")
            return []
    except Exception as e:
        print(f"Exception getting indices: {e}")
        return []

def send_wxpusher(msg, app_token, uid):
    """Send message via WXPusher"""
    url = "https://wxpusher.zjiecode.com/api/send/message"
    data = {
        "appToken": app_token,
        "content": msg,
        "summary": f"{CITY_NAME}天气预报", # Summary for list view
        "contentType": 2, # 1=Text, 2=HTML, 3=Markdown
        "uids": [uid]
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        if result["success"]:
            print("WXPusher message sent successfully.")
        else:
            print(f"Failed to send WXPusher message: {result}")
    except Exception as e:
        print(f"Exception sending WXPusher message: {e}")

def send_pushplus(msg, token):
    # ... (Keep existing PushPlus logic just in case) ...
    """Send message via PushPlus (WeChat)"""
    url = "http://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": f"{CITY_NAME}天气预报",
        "content": msg,
        "template": "html"
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        if result["code"] == 200:
            print("PushPlus message sent successfully.")
        else:
            print(f"Failed to send PushPlus message: {result}")
    except Exception as e:
        print(f"Exception sending PushPlus message: {e}")

def send_qmsg(msg, qmsg_key):
    # ... (Keep existing Qmsg logic) ...
    """Send message via Qmsg"""
    url = f"https://qmsg.zendee.cn/send/{qmsg_key}"
    data = {
        "msg": msg
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()
        if result["success"]:
            print("Qmsg message sent successfully.")
        else:
            print(f"Failed to send Qmsg message: {result}")
    except Exception as e:
        print(f"Exception sending Qmsg message: {e}")

def main():
    if not QWEATHER_KEY:
        print("Error: QWEATHER_KEY not found.")
        return
        
    # Check for any valid push configuration
    if not any([QMSG_KEY, PUSHPLUS_TOKEN, (WXPUSHER_APP_TOKEN and WXPUSHER_UID)]):
        print("Error: No valid push configuration found (QMSG, PushPlus, or WXPusher).")
        return

    print(f"Fetching weather for {CITY_NAME}...")
    
    # 1. Get City ID
    city_id = get_city_id(CITY_NAME, QWEATHER_KEY)
    if not city_id:
        print("Could not find city ID.")
        return

    # 2. Get Weather Data
    weather_data = get_weather(city_id, QWEATHER_KEY)
    if not weather_data:
        print("Could not get weather data.")
        return

    # 3. Get Indices
    indices = get_indices(city_id, QWEATHER_KEY)
    
    # 4. Format Message
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # HTML format for WXPusher/PushPlus
    msg = f"早安！今天 <b>{CITY_NAME}</b> 的天气是 {weather_data['textDay']}。<br>"
    msg += f"气温: {weather_data['tempMin']}°C ~ {weather_data['tempMax']}°C<br>"
    msg += f"风向: {weather_data['windDirDay']} {weather_data['windScaleDay']}级<br>"
    
    if int(weather_data.get('precip', '0')) > 0:
        msg += f"<b>下雨概率: {weather_data['precip']}%，记得带伞！</b><br>"
    
    if indices:
        idx = indices[0]
        msg += f"<br>{idx['name']}建议: {idx['category']}"
            
    print("Message content generated.")

    # 5. Send Notification
    if WXPUSHER_APP_TOKEN and WXPUSHER_UID:
        print("Sending via WXPusher...")
        send_wxpusher(msg, WXPUSHER_APP_TOKEN, WXPUSHER_UID)

    if PUSHPLUS_TOKEN:
        print("Sending via PushPlus...")
        send_pushplus(msg, PUSHPLUS_TOKEN)
    
    if QMSG_KEY:
        print("Sending via Qmsg...")
        send_qmsg(msg.replace("<br>", "\n").replace("<b>", "").replace("</b>", ""), QMSG_KEY)

if __name__ == "__main__":
    main()

