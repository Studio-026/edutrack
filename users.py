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
class UserCreate(BaseModel):
    id: int
    name: str
    role: Literal["teacher", "student"]
    username: str
    password: str
class UserUpdate(BaseModel):
    name: str
    role: Literal["teacher", "student"]
    username: str
    password: str | None = None
class UserResponse(BaseModel):
    id: int
    name: str
    role: Literal["teacher", "student"]
    username: str
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


def get_current_user(
    access_token: str = Header()
) -> User:

    """
    #most useful function
    return user information like
    id: int
    name: str
    role: Literal["teacher", "student"]
    username: str
    password: str

    and manipulate with user as you want
    and it can check if user current login or not
    and it have a lot of hobbies like football
    """

    user_id = sessions.get(access_token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Login required. Please log in first."
        )

    for user in users:
        if user.id == user_id:
            return user

    raise HTTPException(
        status_code=401,
        detail="User associated with this token was not found."
    )


@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):

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

    new_user = User(
        id=user.id,
        name=user.name,
        role=user.role,
        username=user.username,
        password=user.password
    )

    users.append(new_user)

    return new_user


# @router.get("/users", response_model=list[UserResponse])
# def get_users(
#     current_user: User = Depends(get_current_user)
# ):
#     return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):

    for user in users:
        if user.id == user_id:
            return user

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    updated_user: UserUpdate,
    current_user: User = Depends(get_current_user)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own account"
        )

    for index, existing_user in enumerate(users):

        if existing_user.id == user_id:

            if any(
                user.username == updated_user.username
                and user.id != user_id
                for user in users
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Username already exists"
                )

            new_password = (
                updated_user.password
                if updated_user.password is not None
                else existing_user.password
            )

            users[index] = User(
                id=existing_user.id,
                name=updated_user.name,
                role=updated_user.role,
                username=updated_user.username,
                password=new_password
            )

            return users[index]

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own account"
        )

    for index, user in enumerate(users):

        if user.id == user_id:

            users.pop(index)

            tokens_to_delete = [
                token
                for token, session_user_id in sessions.items()
                if session_user_id == user_id
            ]

            for token in tokens_to_delete:
                del sessions[token]

            return {
                "message": f"User {user_id} deleted successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )


@router.post("/login", response_model=TokenResponse)
def login_endpoint(credentials: LoginRequest):

    user = login(
        credentials.username,
        credentials.password
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
def logout(
    access_token: str = Header()
):

    if access_token not in sessions:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token"
        )

    del sessions[access_token]

    return {
        "message": "Logged out successfully"
    }


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):

    """
    funny function can make funny role like
    return non-sensitive information about user
    """

    return current_user