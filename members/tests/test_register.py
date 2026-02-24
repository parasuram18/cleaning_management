import pytest
from django.urls import reverse


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
def test_register(api_client, iu_obj, ward_member_role, payload, expected_status):

    url = reverse('register')
    response = api_client.post(url, payload, format='json', Authorization='Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJlbWFpbCI6ImFydW11Z2FtQGdtYWlsLmNvbSIsInJvbGUiOiJtYW5hZ2VyIiwiZXhwIjoxNzY2MjIzODQ5LCJpYXQiOjE3NjYxMzc0NDl9.jX5sB5Bhs6CcEeIgwOV7m3KzCy9CGD89ZZFXMEoRpco')

    assert response.data['status'] == expected_status, f"{response.data['status']} : {response.data['message']}"
