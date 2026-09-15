from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel


router = APIRouter()
class User(BaseModel):
    id: int
    name: str
    role: Literal["teacher", "student"]
    username: str
    password: str
class LoginRequest(BaseModel):
    username: str
    password: str
class TokenResponse(BaseModel):
    access_token: str




users: list[User] = []
sessions: dict[str, int] = {}




def login(username: str, password: str) -> User | None:
    for user in users:
        if user.username == username and user.password == password:
            return user

    return None




def get_current_user(access_token: str = Header()):
    user_id = sessions.get(access_token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing access token"
        )

    for user in users:
        if user.id == user_id:
            return user

    raise HTTPException(
        status_code=401,
        detail="User not found"
    )



@router.post("/users", response_model=User)
def create_user(user: User):
    if any(existing_user.id == user.id for existing_user in users):
        raise HTTPException(
            status_code=400,
            detail="User ID already exists"
        )

    if any(existing_user.username == user.username for existing_user in users):
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    users.append(user)

    return user



@router.get("/users", response_model=list[User])
def get_users():
    return users



@router.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )



@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User):
    for index, existing_user in enumerate(users):

        if existing_user.id == user_id:

            if (
                updated_user.id != user_id
                and any(
                    user.id == updated_user.id
                    for user in users
                )
            ):
                raise HTTPException(
                    status_code=400,
                    detail="New user ID already exists"
                )

            if any(
                user.username == updated_user.username
                and user.id != user_id
                for user in users
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Username already exists"
                )

            users[index] = updated_user

            return updated_user

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )



@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    for index, user in enumerate(users):

        if user.id == user_id:
            deleted_user = users.pop(index)

            return {
                "message": f"User {user_id} deleted successfully",
                "user": deleted_user
            }

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )


@router.post("/login", response_model=TokenResponse)
def login_endpoint(C: LoginRequest):

    user = login(
        C.username,
        C.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = str(uuid4())

    sessions[access_token] = user.id

    return {
        "access_token": access_token
    }

@router.post("/logout")
def logout(access_token: str = Header()):

    if access_token not in sessions:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token"
        )

    del sessions[access_token]

    return {
        "message": "Logged out successfully"
    }





@router.get("/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user