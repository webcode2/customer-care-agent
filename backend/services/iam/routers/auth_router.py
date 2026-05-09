from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.schemas import (
    UserCreate, Token, OrganizationCreate, OrganizationResponse, 
    OrganizationUpdate, PasswordReset, PasswordChange, UserUpdate, UserResponse
)
from controllers.auth_controller import AuthController
from services.org_service import OrganizationService
from core.security import verify_jwt

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = AuthController.register(db, user_data)
    return AuthController.login(db, user_data.email, user_data.password)

@router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    return AuthController.login(db, user_data.email, user_data.password)

@router.post("/organizations", response_model=OrganizationResponse, dependencies=[Depends(verify_jwt)])
async def create_org(request: Request, org_data: OrganizationCreate, db: Session = Depends(get_db)):
    owner_id = request.state.user_id
    return await OrganizationService.create_organization(db, org_data, owner_id)

@router.patch("/organizations/{org_id}", response_model=OrganizationResponse, dependencies=[Depends(verify_jwt)])
async def update_org(org_id: int, org_data: OrganizationUpdate, db: Session = Depends(get_db)):
    return await OrganizationService.update_organization(db, org_id, org_data)

@router.post("/reset-password")
def reset_password(data: PasswordReset, db: Session = Depends(get_db)):
    if AuthController.reset_password(db, data.email):
        return {"message": "Password reset email sent"}
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/change-password", dependencies=[Depends(verify_jwt)])
def change_password(request: Request, data: PasswordChange, db: Session = Depends(get_db)):
    if AuthController.change_password(db, request.state.user_id, data.old_password, data.new_password):
        return {"message": "Password changed successfully"}
    raise HTTPException(status_code=400, detail="Invalid credentials")

@router.patch("/users/me", response_model=UserResponse, dependencies=[Depends(verify_jwt)])
def update_profile(request: Request, data: UserUpdate, db: Session = Depends(get_db)):
    user = AuthController.update_user(db, request.state.user_id, data)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")
