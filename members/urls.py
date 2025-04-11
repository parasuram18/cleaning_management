from django.urls import path
from . import views
urlpatterns = [
    path('add/', views.add_data, name='add_default'),
    path('company/', views.iu_detais.as_view(), name='company'),
    path('user/', views.user_details.as_view(), name='user'),
]
