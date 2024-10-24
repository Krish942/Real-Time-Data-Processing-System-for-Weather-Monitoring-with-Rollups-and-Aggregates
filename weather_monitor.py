import requests
import json
import os
from datetime import datetime

DATA_DIR = "data"

def get_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to retrieve data for {city}")
        return None

def process_weather_data(data):
    main = data['weather'][0]['main']
    temp_k = data['main']['temp']
    temp_c = temp_k - 273.15
    feels_like_k = data['main']['feels_like']
    feels_like_c = feels_like_k - 273.15
    timestamp = data['dt']
    
    return {
        "main": main,
        "temp_celsius": temp_c,
        "feels_like_celsius": feels_like_c,
        "timestamp": datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    }

def save_weather_data(city, processed_data):
    today = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join(DATA_DIR, f"{city}_weather_{today}.json")
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)

    with open(file_path, 'r+') as f:
        weather_data = json.load(f)
        weather_data.append(processed_data)
        f.seek(0)
        json.dump(weather_data, f, indent=4)

def calculate_daily_summary(city):
    today = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join(DATA_DIR, f"{city}_weather_{today}.json")
    
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r') as f:
        weather_data = json.load(f)

    if len(weather_data) == 0:
        return None

    avg_temp = sum([d['temp_celsius'] for d in weather_data]) / len(weather_data)
    max_temp = max([d['temp_celsius'] for d in weather_data])
    min_temp = min([d['temp_celsius'] for d in weather_data])
    dominant_condition = max(set([d['main'] for d in weather_data]), key=[d['main'] for d in weather_data].count)
    
    return {
        "average_temp": avg_temp,
        "max_temp": max_temp,
        "min_temp": min_temp,
        "dominant_condition": dominant_condition
    }

def check_thresholds(processed_data, thresholds):
    alerts = []
    if processed_data['temp_celsius'] > thresholds['temp_high']:
        alerts.append(f"High Temperature Alert: {processed_data['temp_celsius']}°C")
    if processed_data['temp_celsius'] < thresholds['temp_low']:
        alerts.append(f"Low Temperature Alert: {processed_data['temp_celsius']}°C")
    return alerts
