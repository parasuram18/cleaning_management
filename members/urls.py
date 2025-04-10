from django.urls import path
from . import views
urlpatterns = [
    path('add/', views.add_data, name='add_default'),
    path('company/', views.company_detais.as_view(), name='company'),
]
