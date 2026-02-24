import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .validators import is_strong_password
from members.models import CustomUser, IuMaster, RoleMaster, RoleMapping

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def iu_obj():
    iumaster_obj = IuMaster.objects.create(company_name='Medyaan', domain_name='http://127.0.0.1:8000/')
    return iumaster_obj

@pytest.fixture
def ward_member_role():
    roleobj = RoleMaster.objects.create(role='ward_member')
    return roleobj

@pytest.fixture
def consumer_obj(iu_obj, ward_member_role):

    consumer = CustomUser.objects.create(phonenumber="+919345769198", email="parasuramech@gmail.com", iu_id=iu_obj)
    consumer.set_password('Admin@123')
    consumer.save()

    RoleMapping.objects.create(user=consumer, role=ward_member_role, iu_id=iu_obj)

    return consumer




@pytest.mark.parametrize(
    'password',
    [
        'Admin@123',
        'Parasu@1823',
        'Barath@1234'
    ]
)
def test_password(password):

    is_strong = is_strong_password(password)
    assert is_strong, f"Week Password - {password}"


@pytest.mark.integration
@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload, expected_status",
    [
        (
            {
                'phonenumber':'+919345769198',
                'password':'Admin@123'
            },
            'success'
        ),
        (
            {
                'phonenumber':'+919345769198',
                'password':'wrong@123'
            },
            'error'
        ),
        (
            {
                'phonenumber':'+916381614678',
                'password':'Admin@123'
            },
            'error'
        )
    ]
)
def test_login(api_client,  consumer_obj, payload, expected_status):

    url = reverse('login')
    response = api_client.post(url, payload, format="json", HTTP_ORIGIN='http://127.0.0.1:8000/')

    assert response.data['status'] == expected_status, f"{response.data['message']}"


@pytest.mark.integration
@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload, expected_status",
    [
        (
            { # success
                "phonenumber":"0987654322",
                "email":"arun@gmail.com",
                "password":"Arun@123",
                "role":"ward_member",
            },
            'success'
        ),
        (
            {# Invalid Phone number
                "first_name":"Parasu",
                "last_name":"K",
                "phonenumber":"45769198",
                "email":"Parasu@gmail.com",
                "password":"parasu@123",
                "role":"ward_member",
                "age":23,
                "gender":"male",
                "is_married":True,
                "address":{
                    "city":"Tenkasi"
                }
            },
            'warning'
        ),
        (
            {# Check for strong password
                "first_name":"Parasu",
                "last_name":"K",
                "phonenumber":"9345769198",
                "email":"parasu@gmail.com",
                "password":"parasu@123",
                "role":"ward_member",
                "age":23,
                "gender":"male",
                "is_married":True,
                "address":{
                    "city":"Tenkasi"
                }
            },
            'warning'
        )
    ]
)
def test_register(api_client:APIClient, iu_obj, ward_member_role, payload, expected_status):

    url = reverse('register')
    response = api_client.post(url, payload, format='json', HTTP_ORIGIN='http://127.0.0.1:8000/', Authorization='Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJlbWFpbCI6ImFydW11Z2FtQGdtYWlsLmNvbSIsInJvbGUiOiJtYW5hZ2VyIiwiZXhwIjoxNzY2MjIzODQ5LCJpYXQiOjE3NjYxMzc0NDl9.jX5sB5Bhs6CcEeIgwOV7m3KzCy9CGD89ZZFXMEoRpco')

    assert response.data['status'] == expected_status, f"{response.data['status']} : {response.data['message']}"
