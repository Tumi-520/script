import os
import requests
import json
from datetime import datetime

# Configuration
# Get these from environment variables (GitHub Secrets)
QWEATHER_KEY = os.environ.get("QWEATHER_KEY")
QMSG_KEY = os.environ.get("QMSG_KEY")
CITY_NAME = os.environ.get("CITY", "Shenzhen") # Default to Shenzhen if not set

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

def send_qmsg(msg, qmsg_key):
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
            print("Message sent successfully.")
        else:
            print(f"Failed to send message: {result}")
    except Exception as e:
        print(f"Exception sending message: {e}")

def main():
    if not QWEATHER_KEY or not QMSG_KEY:
        print("Error: QWEATHER_KEY or QMSG_KEY not found in environment variables.")
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

    # 3. Get Indices (Optional but nice)
    indices = get_indices(city_id, QWEATHER_KEY)
    
    # 4. Format Message
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    msg = f"【每日天气】{CITY_NAME} {today_date}\n"
    msg += f"天气: {weather_data['textDay']}\n"
    msg += f"温度: {weather_data['tempMin']}°C ~ {weather_data['tempMax']}°C\n"
    msg += f"风向: {weather_data['windDirDay']} {weather_data['windScaleDay']}级\n"
    msg += f"降水概率: {weather_data.get('precip', '0')}%\n"
    
    if indices:
        for idx in indices:
            msg += f"{idx['name']}: {idx['category']}\n"
            
    print("Message content:")
    print(msg)

    # 5. Send Notification
    send_qmsg(msg, QMSG_KEY)

if __name__ == "__main__":
    main()
