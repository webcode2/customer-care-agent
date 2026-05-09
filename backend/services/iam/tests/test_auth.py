import pytest
from ..services.auth_service import AuthService

def test_password_hashing():
    password = "secret_password"
    hashed = AuthService.get_password_hash(password)
    assert hashed != password
    assert AuthService.verify_password(password, hashed) is True
    assert AuthService.verify_password("wrong_password", hashed) is False

def test_create_access_token():
    data = {"sub": "123", "org_id": 1}
    token = AuthService.create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0
