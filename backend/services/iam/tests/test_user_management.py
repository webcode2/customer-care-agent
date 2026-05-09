import pytest
from unittest.mock import MagicMock, patch
from ..controllers.auth_controller import AuthController
from ..schemas.schemas import UserUpdate, PasswordChange, OrganizationUpdate
from ..services.org_service import OrganizationService

@pytest.mark.asyncio
async def test_reset_password_mock():
    db = MagicMock()
    email = "test@example.com"
    with patch("backend.services.iam.controllers.auth_controller.User") as mock_user_model:
        db.query().filter().first.return_value = MagicMock(email=email)
        result = AuthController.reset_password(db, email)
        assert result is True

@pytest.mark.asyncio
async def test_change_password_mock():
    db = MagicMock()
    user_id = 1
    data = PasswordChange(old_password="old", new_password="new")
    
    with patch("backend.services.iam.controllers.auth_controller.AuthService") as mock_auth_service:
        mock_auth_service.verify_password.return_value = True
        mock_auth_service.get_password_hash.return_value = "new_hash"
        
        db.query().filter().first.return_value = MagicMock(id=user_id, hashed_password="old_hash")
        
        result = AuthController.change_password(db, user_id, data.old_password, data.new_password)
        assert result is True
        db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_profile_mock():
    db = MagicMock()
    user_id = 1
    data = UserUpdate(email="new@example.com")
    
    mock_user = MagicMock(id=user_id, email="old@example.com")
    db.query().filter().first.return_value = mock_user
    
    result = AuthController.update_user(db, user_id, data)
    assert result.email == "new@example.com"
    db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_organization_mock():
    db = MagicMock()
    org_id = 1
    data = OrganizationUpdate(name="Updated Org")
    
    mock_org = MagicMock(id=org_id, name="Old Org")
    db.query().filter().first.return_value = mock_org
    
    result = await OrganizationService.update_organization(db, org_id, data)
    assert result.name == "Updated Org"
    db.commit.assert_called_once()
