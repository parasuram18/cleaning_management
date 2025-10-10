from django.urls import path
from .views import encrypt_data, generate_keys, decrypt_data_HIU, listen_webhook

urlpatterns = [
    path('keys/',generate_keys, name="generate_keys"),
    path('encrypt/',encrypt_data, name="encrypt"),
    path('decrypt/',decrypt_data_HIU, name="decrypt"),
    # path('webhook/',listen_webhook, name="listen_webhook"),
    path('api/v3/hip/token/on-generate-token/',listen_webhook, name="on-generate-token"),
]
