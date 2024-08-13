from django.urls import path
from WeatherForecastAPI import views

app_name = 'WeatherForecastAPI'

urlpatterns = [
    # path('api/forecast/', views.ForecastView.as_view(), name='forecast'),
    path('api/check-condition/', views.CheckConditionView.as_view(), name='condition')
]
