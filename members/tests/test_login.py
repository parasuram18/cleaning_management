import pytest
from django.urls import reverse


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
    response = api_client.post(url, payload, format="json")

    assert response.data['status'] == expected_status, f"{response.data['message']}"