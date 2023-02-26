from django.urls import path
from emo_app.views import test_num

app_name = 'emo_app'
num2 = 2
urlpatterns = [
    path('<str:num1>/',test_num, name='num2')
]