from sqlalchemy.orm import Session
from models.models import Organization
from schemas.schemas import OrganizationCreate
from messaging.nats_client import nats_client

class OrganizationService:
    @staticmethod
    async def create_organization(db: Session, org: OrganizationCreate, owner_id: int):
        db_org = Organization(name=org.name, slug=org.slug, config=org.config, owner_id=owner_id)
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        
        # Automatically link the owner to the organization
        from models.models import User
        user = db.query(User).filter(User.id == owner_id).first()
        if user:
            user.organization_id = db_org.id
            db.commit()

        # Publish event
        await nats_client.publish("org.created", {
            "id": db_org.id,
            "name": db_org.name,
            "slug": db_org.slug
        })
        
        return db_org

    @staticmethod
    async def update_organization(db: Session, org_id: int, org_update: any):
        db_org = db.query(Organization).filter(Organization.id == org_id).first()
        if not db_org:
            return None
        if org_update.name:
            db_org.name = org_update.name
        if org_update.slug:
            db_org.slug = org_update.slug
        if org_update.config:
            db_org.config = org_update.config
        db.commit()
        db.refresh(db_org)
        return db_org

    @staticmethod
    def get_organization(db: Session, org_id: int):
        return db.query(Organization).filter(Organization.id == org_id).first()

    @staticmethod
    def get_organization_by_slug(db: Session, slug: str):
        return db.query(Organization).filter(Organization.slug == slug).first()
