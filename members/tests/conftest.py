import pytest
from rest_framework.test import APIClient
from members.models import IuMaster, RoleMaster, RoleMapping, CustomUser
from django.urls import reverse

@pytest.fixture
def api_client():
    CLIENT = APIClient.headers(HTTP_ORIGIN='http://127.0.0.1:8000/')
    return CLIENT

@pytest.fixture
def iu_obj():
    iumaster_obj = IuMaster.objects.create(company_name='Medyaan', domain_name='http://127.0.0.1:8000/')
    return iumaster_obj

@pytest.fixture
def role_master():
    roles = [
        RoleMaster(role='ward_member'),
        RoleMaster(role='manager'),
        RoleMaster(role='admin')
    ]
    RoleMaster.objects.bulk_create(roles)

    return RoleMaster.objects.all()

 # for login test
@pytest.fixture
def consumer_obj(iu_obj, role_master):

    consumer = CustomUser.objects.create(phonenumber="+919345769198", email="parasuramech@gmail.com", iu_id=iu_obj)
    consumer.set_password('Admin@123')
    consumer.save()

    RoleMapping.objects.create(user=consumer, role=role_master.get(role='ward_member'), iu_id=iu_obj)

    return consumer

@pytest.fixture
def consumer_client(api_client, consumer_obj):

    url = reverse('login')
    payload = {
        'phonenumber':consumer_obj.phonenumber,
        'password':'Admin@123'
    }
    response = api_client.post(url, payload, 'json')
    token = response.data['token']

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    return api_client
