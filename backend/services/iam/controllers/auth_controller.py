from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services.auth_service import AuthService
from models.models import User
from schemas.schemas import UserCreate

class AuthController:
    @staticmethod
    def login(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not AuthService.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "org_id": user.organization_id}
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def register(db: Session, user_data: UserCreate):
        hashed_password = AuthService.get_password_hash(user_data.password)
        
        # If no organization_id is provided, create a default workspace for the user
        if not user_data.organization_id:
            from models.models import Organization
            # Create a unique slug from email handle and a random component to prevent collisions
            import uuid
            slug = f"{user_data.email.split('@')[0]}-{str(uuid.uuid4())[:8]}"
            new_org = Organization(
                name=f"{user_data.email.split('@')[0].capitalize()}'s Workspace",
                slug=slug,
                config={}
            )
            db.add(new_org)
            db.flush() # Flush to get the new_org.id
            user_data.organization_id = new_org.id

        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            organization_id=user_data.organization_id
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Set the user as the owner of their new organization
        if not user_data.organization_id is None: # Actually it's guaranteed to be set now
            org = db.query(Organization).filter(Organization.id == user_data.organization_id).first()
            if org and not org.owner_id:
                org.owner_id = db_user.id
                db.commit()
                
        return db_user
    @staticmethod
    def reset_password(db: Session, email: str):
        # In a real app, this would send an email with a token
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        # Mocking reset logic
        return True

    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not AuthService.verify_password(old_password, user.hashed_password):
            return False
        user.hashed_password = AuthService.get_password_hash(new_password)
        db.commit()
        return True

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: any):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if user_update.email:
            user.email = user_update.email
        if user_update.is_active is not None:
            user.is_active = user_update.is_active
        db.commit()
        db.refresh(user)
        return user
