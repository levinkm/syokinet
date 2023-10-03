import pytest
from accounts.models import User
from tests.factories import UserFactory


@pytest.mark.django_db
def test_create_user_model_object_with_factory_method(db):
    # Create a user using the factory
    obj = UserFactory()
    assert User.objects.count() == 1
    assert obj.is_active


@pytest.mark.django_db
def test_login_customer(api_client, Customer, db):
    res = api_client.post("user/login", {"email": Customer.email, "password": "123456"})
    print(res.data)
    # assert User.objects.count() == 1
    assert Customer.is_active
