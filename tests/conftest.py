import pytest
from django.conf import settings
from rest_framework.test import APIClient
from accounts.models import User

@pytest.fixture()
def Customer(db):
    User.objects.create_user("test_user", "test@gmail.com", "test")
    user = User.objects.get(username="test_user")
    return user

@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def ip_address_test(customer,api_client,db):
    res = api_client.post(
        "/ip/allocate",
        {
            "customer_name": customer.customer_name,
            "email": "johndoe@gmail.com"
        }
        )
    return res.data
            
    