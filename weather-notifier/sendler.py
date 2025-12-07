import requests
import smtplib
import os
import sys
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

# Настройка логирования для Docker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WeatherAlertSystem:
    def __init__(self):
        # Загружаем .env из текущей директории
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path)
        
        # Конфигурация из переменных окружения
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.email_sender = os.getenv('EMAIL_SENDER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_recipients = os.getenv('EMAIL_RECIPIENTS', '').split(',')
        
        # Валидация
        if not self.weather_api_key:
            logger.error("OPENWEATHER_API_KEY не установлен")
        if not self.email_sender or not self.email_password:
            logger.error("EMAIL_SENDER или EMAIL_PASSWORD не установлены")
        
        # Параметры для определения опасной погоды
        self.alert_conditions = {
            'thunderstorm': {
                'description': 'Гроза',
                'advice': 'Ожидается сильная гроза. Рекомендуется остаться дома, избегать открытых пространств и не использовать электроприборы.',
                'min_intensity': 200
            },
            'heavy_rain': {
                'description': 'Сильный дождь',
                'advice': 'Ожидается сильный дождь. Возможны подтопления. Рекомендуется избегать поездок, проверить герметичность окон.',
                'min_intensity': 502
            },
            'snow': {
                'description': 'Снегопад',
                'advice': 'Ожидается сильный снегопад. Будьте осторожны на дорогах, одевайтесь теплее.',
                'min_intensity': 600
            },
            'extreme_heat': {
                'description': 'Аномальная жара',
                'advice': 'Ожидается аномально высокая температура. Пейте больше воды, избегайте прямых солнечных лучей.',
                'temp_threshold': 35
            },
            'extreme_cold': {
                'description': 'Сильный мороз',
                'advice': 'Ожидается сильный мороз. Одевайтесь тепло, ограничьте время пребывания на улице.',
                'temp_threshold': -15
            },
            'strong_wind': {
                'description': 'Сильный ветер',
                'advice': 'Ожидается сильный ветер. Уберите предметы с балконов, будьте осторожны на улице.',
                'wind_threshold': 15
            }
        }
        
    def get_weather_forecast(self, city="Moscow", country_code="RU"):
        """Получение прогноза погоды на 5 дней"""
        try:
            logger.info(f"Получение прогноза для {city}, {country_code}")
            
            # Геокодирование
            geo_url = "http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                'q': f'{city},{country_code}',
                'limit': 1,
                'appid': self.weather_api_key
            }
            
            geo_response = requests.get(geo_url, params=geo_params, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data:
                logger.error(f"Город {city} не найден")
                return None
            
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']
            
            # Прогноз
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            forecast_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.weather_api_key,
                'units': 'metric',
                'lang': 'ru'
            }
            
            response = requests.get(forecast_url, params=forecast_params, timeout=10)
            response.raise_for_status()
            forecast_data = response.json()
            
            logger.info(f"Прогноз получен для {city}")
            return forecast_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при получении прогноза: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении прогноза: {e}")
            return None
    
    def analyze_weather(self, forecast_data):
        """Анализ погодных условий"""
        alerts = []
        
        if not forecast_data or 'list' not in forecast_data:
            return alerts
        
        # Анализируем ближайшие 24 часа
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        
        for forecast in forecast_data['list']:
            forecast_time = forecast['dt_txt']
            if tomorrow_str in forecast_time:
                weather_id = forecast['weather'][0]['id']
                temp = forecast['main']['temp']
                wind_speed = forecast['wind']['speed']
                weather_desc = forecast['weather'][0]['description']
                
                # Проверка условий
                if 200 <= weather_id <= 232:
                    alerts.append({
                        'time': forecast_time,
                        'type': 'thunderstorm',
                        'description': f'Гроза: {weather_desc}',
                        'advice': self.alert_conditions['thunderstorm']['advice'],
                        'intensity': 'сильная' if weather_id >= 210 else 'умеренная'
                    })
                
                elif 502 <= weather_id <= 531:
                    alerts.append({
                        'time': forecast_time,
                        'type': 'heavy_rain',
                        'description': f'Сильный дождь: {weather_desc}',
                        'advice': self.alert_conditions['heavy_rain']['advice'],
                        'intensity': 'очень сильный' if weather_id >= 511 else 'сильный'
                    })
                
                elif 600 <= weather_id <= 622:
                    alerts.append({
                        'time': forecast_time,
                        'type': 'snow',
                        'description': f'Снегопад: {weather_desc}',
                        'advice': self.alert_conditions['snow']['advice'],
                        'intensity': 'сильный' if weather_id >= 615 else 'умеренный'
                    })
                
                elif temp >= self.alert_conditions['extreme_heat']['temp_threshold']:
                    alerts.append({
                        'time': forecast_time,
                        'type': 'extreme_heat',
                        'description': f'Аномальная жара: {temp}°C',
                        'advice': self.alert_conditions['extreme_heat']['advice'],
                        'intensity': 'опасная'
                    })
                
                elif temp <= self.alert_conditions['extreme_cold']['temp_threshold']:
                    alerts.append({
                        'time': forecast_time,
                        'type': 'extreme_cold',
                        'description': f'Сильный мороз: {temp}°C',
                        'advice': self.alert_conditions['extreme_cold']['advice'],
                        'intensity': 'опасный'
                    })
                
                elif wind_speed >= self.alert_conditions['strong_wind']['wind_threshold']:
                    alerts.append({
                        'time': forecast_time,
                        'type': 'strong_wind',
                        'description': f'Сильный ветер: {wind_speed} м/с',
                        'advice': self.alert_conditions['strong_wind']['advice'],
                        'intensity': 'очень сильный' if wind_speed >= 20 else 'сильный'
                    })
        
        return alerts
    
    def create_email_content(self, alerts, city):
        """Создание содержимого email"""
        if not alerts:
            return None
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert {{ 
                    background-color: #fff3cd; 
                    border: 1px solid #ffeaa7; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 5px;
                }}
                .warning {{ color: #856404; }}
                .time {{ color: #666; font-size: 0.9em; }}
                .advice {{ background-color: #f8f9fa; padding: 10px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h2>⚠️ Погодное предупреждение для {city}</h2>
            <p>На завтра ожидаются следующие опасные погодные условия:</p>
        """
        
        grouped_alerts = {}
        for alert in alerts:
            if alert['type'] not in grouped_alerts:
                grouped_alerts[alert['type']] = []
            grouped_alerts[alert['type']].append(alert)
        
        for alert_type, alert_list in grouped_alerts.items():
            first_alert = alert_list[0]
            times = ', '.join(sorted(set(a['time'][11:16] for a in alert_list)))
            html_content += f"""
            <div class="alert">
                <h3 class="warning">⚠ {first_alert['description']}</h3>
                <p class="time">Время: {times}</p>
                <div class="advice">
                    <strong>Рекомендации:</strong><br>
                    {first_alert['advice']}
                </div>
            </div>
            """
        
        html_content += """
            <hr>
            <p><small>Это автоматическое уведомление от системы мониторинга погоды.<br>
            Будьте осторожны и следите за обновлениями прогноза.</small></p>
        </body>
        </html>
        """
        
        text_content = f"Погодное предупреждение для {city}\n\n"
        text_content += "На завтра ожидаются следующие опасные погодные условия:\n\n"
        
        for alert_type, alert_list in grouped_alerts.items():
            first_alert = alert_list[0]
            times = ', '.join(sorted(set(a['time'][11:16] for a in alert_list)))
            text_content += f"⚠ {first_alert['description']}\n"
            text_content += f"Время: {times}\n"
            text_content += f"Рекомендации: {first_alert['advice']}\n\n"
        
        text_content += "---\nБудьте осторожны и следите за обновлениями прогноза."
        
        return {
            'html': html_content,
            'text': text_content,
            'subject': f"⚠ Погодное предупреждение: {len(alerts)} опасных явлений в {city}"
        }
    
    def send_email(self, email_content, recipients):
        """Отправка email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = email_content['subject']
            msg['From'] = self.email_sender
            msg['To'] = ', '.join(recipients)
            
            part1 = MIMEText(email_content['text'], 'plain')
            part2 = MIMEText(email_content['html'], 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Письмо успешно отправлено {len(recipients)} получателям")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отправке письма: {e}")
            return False
    
    def run_alert_check(self, city="Moscow", country_code="RU"):
        """Основной метод запуска проверки"""
        logger.info(f"=== Начало проверки погоды для {city} ===")
        
        forecast = self.get_weather_forecast(city, country_code)
        if not forecast:
            logger.error(f"Не удалось получить прогноз для {city}")
            return
        
        alerts = self.analyze_weather(forecast)
        
        if alerts:
            logger.info(f"Найдено {len(alerts)} опасных погодных явлений для {city}")
            
            email_content = self.create_email_content(alerts, city)
            if email_content:
                success = self.send_email(email_content, self.email_recipients)
                if success:
                    logger.info(f"Уведомления отправлены для {city}")
                else:
                    logger.error(f"Не удалось отправить уведомления для {city}")
            
            # Логирование в консоль
            for alert in alerts:
                logger.info(f"Обнаружено: {alert['description']} в {alert['time']}")
        else:
            logger.info(f"Опасных погодных явлений не обнаружено для {city}")

def main():
    """Главная функция"""
    logger.info("=" * 60)
    logger.info("Запуск системы оповещения о погоде")
    logger.info(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Проверка переменных окружения
    required_vars = ['OPENWEATHER_API_KEY', 'EMAIL_SENDER', 'EMAIL_PASSWORD']
    load_dotenv()
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Отсутствуют переменные: {', '.join(missing_vars)}")
        logger.error("Запуск прерван")
        return
    
    # Создаем систему
    alert_system = WeatherAlertSystem()
    
    # Список городов для мониторинга
    cities_to_check = [
        ("Moscow", "RU"),
        # ("London", "GB"),
        # ("New York", "US"),
        # Добавьте свои города
    ]
    
    # Проверяем каждый город
    for city, country in cities_to_check:
        try:
            alert_system.run_alert_check(city, country)
            time.sleep(2)  # Пауза между запросами
        except Exception as e:
            logger.error(f"Ошибка при проверке {city}: {e}")
    
    logger.info("=" * 60)
    logger.info("Проверка завершена")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()