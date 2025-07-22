from django.urls import path
from chat.views import room_page
urlpatterns = [
    path('<sender>/<receiver>/', room_page, name='chatpage')
]
