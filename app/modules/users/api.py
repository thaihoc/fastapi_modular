from fastapi import APIRouter, Depends, HTTPException

from app.shared.deps import validate_token

from .schemas import UserCreate, UserResponse
from .deps import get_user_service
from .service import UserService

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(validate_token)])

@router.post("/", response_model=UserResponse)
def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        return service.create_user(
            email=data.email,
            password=data.password,
            full_name=data.full_name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 10,
    service: UserService = Depends(get_user_service)
):
    return service.list_users(skip, limit)