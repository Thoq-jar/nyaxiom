import httpx
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")
BASE_URL = "https://api.openweathermap.org/data/2.5"

async def get_weather_data(city: str = "Stockholm"):
    async with httpx.AsyncClient() as client:
        try:
            current_url = f"{BASE_URL}/weather?q={city}&appid={API_KEY}&units=metric"
            forecast_url = f"{BASE_URL}/forecast?q={city}&appid={API_KEY}&units=metric"
            
            current_res = await client.get(current_url)
            forecast_res = await client.get(forecast_url)
            
            if current_res.status_code != 200 or forecast_res.status_code != 200:
                return get_mock_weather(city)
                
            current_data = current_res.json()
            forecast_data = forecast_res.json()
            
            return {
                "location": f"{current_data['name']}, {current_data['sys']['country']}",
                "temp": f"{round(current_data['main']['temp'])}°C",
                "icon_url": f"https://openweathermap.org/img/wn/{current_data['weather'][0]['icon']}@4x.png",
                "forecast": [
                    {
                        "temp": f"{round(item['main']['temp'])}°C",
                        "icon_url": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                        "val": item['dt_txt'].split(" ")[1][:5]
                    } for item in forecast_data['list'][:4]
                ]
            }
        except Exception:
            return get_mock_weather(city)

def get_mock_weather(city):
    return {
        "location": f"{city}, SE",
        "temp": "18°C",
        "icon_url": "https://openweathermap.org/img/wn/01d@4x.png",
        "forecast": [
            {"temp": "19°C", "icon_url": "https://openweathermap.org/img/wn/01d@2x.png", "val": "12:00"},
            {"temp": "17°C", "icon_url": "https://openweathermap.org/img/wn/02d@2x.png", "val": "15:00"},
            {"temp": "15°C", "icon_url": "https://openweathermap.org/img/wn/03d@2x.png", "val": "18:00"},
            {"temp": "14°C", "icon_url": "https://openweathermap.org/img/wn/04d@2x.png", "val": "21:00"},
        ]
    }
