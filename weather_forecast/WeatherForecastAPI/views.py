from django.views.generic import View
from django.http import JsonResponse
import requests
from typing import Dict


def get_coordinates(city: str) -> list[str]:
    KEY = '18a96da4a6867b5c0fbe4297cdfdf9a8'
    url = 'http://api.openweathermap.org/geo/1.0/direct'
    params = {
        'q': city,
        'appid': KEY
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

        access_key = "7874040d-7b9d-4553-a7c8-5b9e00b1feed"

        headers = {
            "X-Yandex-Weather-Key": access_key
        }

        query = self.exec_graphql_query(lat, lon)

        response = requests.post('https://api.weather.yandex.ru/graphql/query', headers=headers, json={'query': query})

        return response.json()['data']['weatherByPoint']['forecast']['days'][0]['hours']

    def get(self, request):
        requested_params = request.GET
        final_response = []

        for dic in requested_params:
            lat, lon = get_coordinates(dic['city'])
            weather = self.get_weather_response(lat, lon)
            forecast_conditions = set(event['condition'] for event in weather)

            real_dic = {
                'city': dic['city'],
                'events': [event for event in dic['events'] if event.upper() in forecast_conditions]
            }

            if len(real_dic['events']) == 0:
                pass
            else:
                final_response.append(real_dic)

            return JsonResponse(final_response)
