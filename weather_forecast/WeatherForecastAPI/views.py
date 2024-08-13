from django.views.generic import View
from django.http import HttpResponse
from .config import YANDEX_API_KEY, OPENWEATHERMAP_API_KEY
import requests
import json


def get_coordinates(city: str) -> list[str]:
    url = 'http://api.openweathermap.org/geo/1.0/direct'
    params = {
        'q': city,
        'appid': OPENWEATHERMAP_API_KEY,
    }
    response = requests.get(url, params).json()
    lat = response[0]['lat']
    lon = response[0]['lon']
    return [lat, lon]


# class ForecastView(View):
#
#     def get(self, request):
#         coordinates = get_coordinates(request.GET['city'])


class CheckConditionView(View):

    @staticmethod
    def exec_graphql_query(lat, lon):
        query = f"""
            {{
              weatherByPoint(request: {{lat: {lat}, lon: {lon}}}) {{
                forecast {{
                  days(limit: 1) {{
                    hours {{
                      condition
                    }}
                  }}
                }}
              }}
            }}
            """
        return query

    def get_weather_response(self, lat, lon):

        headers = {
            "X-Yandex-Weather-Key": YANDEX_API_KEY
        }

        query = self.exec_graphql_query(lat, lon)

        response = requests.post('https://api.weather.yandex.ru/graphql/query', headers=headers, json={'query': query})

        return response.json()['data']['weatherByPoint']['forecast']['days'][0]['hours']

    @staticmethod
    def transform_weather_data_to_set(forecast_conditions: list) -> set:
        for dic in forecast_conditions:
            if dic['condition'] in ['PARTLY_CLOUDY', 'CLOUDY']:
                dic['condition'] = 'OVERCAST'
            elif dic['condition'] in ['LIGHT_RAIN', 'HEAVY_RAIN', 'SHOWERS']:
                dic['condition'] = 'RAIN'
            elif dic['condition'] in ['LIGHT_SNOW', 'SNOWFALL']:
                dic['condition'] = 'SNOW'
            elif dic['condition'] in ['THUNDERSTORM_WITH_RAIN', 'THUNDERSTORM_WITH_HAIL']:
                dic['condition'] = 'THUNDERSTORM'
        return {event['condition'] for event in forecast_conditions}

    def get(self, request):
        requested_params = json.loads(request.GET.get('data'))
        final_response = []

        for dic in requested_params:
            lat, lon = get_coordinates(dic['city'])
            weather = self.get_weather_response(lat, lon)
            forecast_conditions = self.transform_weather_data_to_set(weather)

            real_dic = {
                'city': dic['city'],
                'events': [event for event in dic['events'] if event.upper() in forecast_conditions]
            }

            if len(real_dic['events']) == 0:
                pass
            else:
                final_response.append(real_dic)

            return HttpResponse(json.dumps(final_response, ensure_ascii=False))
