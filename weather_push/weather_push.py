import os
import requests
import json
from datetime import datetime

# Configuration
# Get these from environment variables (GitHub Secrets)
QWEATHER_KEY = os.environ.get("QWEATHER_KEY")
QMSG_KEY = os.environ.get("QMSG_KEY")
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN") # New: WeChat Push
CITY_NAME = os.environ.get("CITY", "Shenzhen")

# ... (Keep existing API URLs) ...

# ... (Keep get_city_id, get_weather, get_indices functions) ...

def send_pushplus(msg, token):
    """Send message via PushPlus (WeChat)"""
    url = "http://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": f"{CITY_NAME}天气预报",
        "content": msg,
        "template": "html" # Use HTML for better formatting if needed, or txt
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
        
    if not QMSG_KEY and not PUSHPLUS_TOKEN:
        print("Error: No push token found (QMSG_KEY or PUSHPLUS_TOKEN).")
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
    
    # HTML format for PushPlus, plain text for Qmsg
    # We'll construct a generic one and maybe tweak if needed
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
    if PUSHPLUS_TOKEN:
        print("Sending via PushPlus...")
        send_pushplus(msg, PUSHPLUS_TOKEN)
    
    if QMSG_KEY:
        print("Sending via Qmsg...")
        # Strip HTML tags for Qmsg if necessary, or Qmsg might handle them poorly
        # For simplicity, sending the same string. Qmsg might show raw HTML tags.
        # Let's make a simple text version for Qmsg if both are present?
        # Or just assume user only uses one.
        send_qmsg(msg.replace("<br>", "\n").replace("<b>", "").replace("</b>", ""), QMSG_KEY)

if __name__ == "__main__":
    main()

