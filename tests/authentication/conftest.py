import pytest
from django.conf import settings
from oauth2_provider.models import Application
from rest_framework.test import APIClient

from authentication.models import CustomUser as User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin", email="admin@gmail.com", password="adminpassword"
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser", email="testuser@example.com", password="testpassword"
    )


@pytest.fixture
@pytest.mark.django_db
def application(db, user):
    return Application.objects.create(
        name="Test Application",
        client_id=settings.OAUTH2_CLIENT_ID,
        client_secret=settings.OAUTH2_CLIENT_SECRET,
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_PASSWORD,
        user=user,
    )


@pytest.fixture
def mock_custom_token_generator():
    return None


@pytest.fixture
def mock_authenticate():
    return None


@pytest.fixture
def clear_users():
    yield
    User.objects.all().delete()
