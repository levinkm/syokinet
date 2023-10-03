from accounts.models import User
from django.contrib.auth.hashers import make_password
import factory

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("username")
    email = factory.Faker("email")
    password = make_password("123456")
    is_active = True
    customer_name = factory.Faker("name")


