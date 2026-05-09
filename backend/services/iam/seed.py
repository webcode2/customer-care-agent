from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from models.models import Organization, User
from services.auth_service import AuthService
import sys

def seed():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Seeding database...")
        
        # 1. Create Organizations if they don't exist
        org_acme = db.query(Organization).filter(Organization.slug == "acme-corp").first()
        if not org_acme:
            org_acme = Organization(name="Acme Corp", slug="acme-corp", config={})
            db.add(org_acme)
            db.commit()
            db.refresh(org_acme)
            print("Created Org: Acme Corp")
        else:
            print("Org Acme Corp already exists")

        org_stark = db.query(Organization).filter(Organization.slug == "stark-ind").first()
        if not org_stark:
            org_stark = Organization(name="Stark Industries", slug="stark-ind", config={})
            db.add(org_stark)
            db.commit()
            db.refresh(org_stark)
            print("Created Org: Stark Industries")
        else:
            print("Org Stark Industries already exists")

        # 2. Create Users
        users_data = [
            {
                "email": "admin@acme.com",
                "password": "password123",
                "role": "business_admin",
                "org_id": org_acme.id
            },
            {
                "email": "assistant@acme.com",
                "password": "password123",
                "role": "assistant",
                "org_id": org_acme.id
            },
            {
                "email": "admin@stark.com",
                "password": "password123",
                "role": "business_admin",
                "org_id": org_stark.id
            },
            {
                "email": "assistant@stark.com",
                "password": "password123",
                "role": "assistant",
                "org_id": org_stark.id
            }
        ]

        for u in users_data:
            existing_user = db.query(User).filter(User.email == u["email"]).first()
            if not existing_user:
                hashed_pwd = AuthService.get_password_hash(u["password"])
                user = User(
                    email=u["email"],
                    hashed_password=hashed_pwd,
                    role=u["role"],
                    organization_id=u["org_id"]
                )
                db.add(user)
                print(f"Created User: {u['email']}")
            else:
                print(f"User {u['email']} already exists")
        
        db.commit()
        
        # Update Org Owners (setting first admin as owner)
        acme_admin = db.query(User).filter(User.email == "admin@acme.com").first()
        if acme_admin:
            org_acme.owner_id = acme_admin.id
            
        stark_admin = db.query(User).filter(User.email == "admin@stark.com").first()
        if stark_admin:
            org_stark.owner_id = stark_admin.id
            
        db.commit()

        print("Database seeding process completed!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
