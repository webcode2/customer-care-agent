import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from ..services.org_service import OrganizationService
from ..schemas.schemas import OrganizationCreate

@pytest.mark.asyncio
async def test_create_organization_publishes_event():
    db = MagicMock()
    org_data = OrganizationCreate(name="Test Org", slug="test-org", config={})
    
    with patch("backend.services.iam.services.org_service.nats_client", new_callable=AsyncMock) as mock_nats:
        with patch("backend.services.iam.services.org_service.Organization") as mock_org_model:
            mock_org_instance = mock_org_model.return_value
            mock_org_instance.id = 1
            mock_org_instance.name = "Test Org"
            mock_org_instance.slug = "test-org"
            
            result = await OrganizationService.create_organization(db, org_data)
            
            # Verify DB calls
            db.add.assert_called_once()
            db.commit.assert_called_once()
            
            # Verify NATS publish
            mock_nats.publish.assert_called_once_with("org.created", {
                "id": 1,
                "name": "Test Org",
                "slug": "test-org"
            })
            
            assert result.name == "Test Org"
