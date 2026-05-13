from fastapi import HTTPException
from app.core.security import verify_access_token
from app.services.auth import UserService
from app.schema.auth_schema import RegisterUserSchema, UsernameLoginSchema


async def test_create_user_service_success(
    db_session,
):
    user_service = UserService(db_session)

    payload = RegisterUserSchema(
        username="TestUser",
        email="test@example.com",
        password="Password@123",
    )

    user = await user_service.create(payload)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password_hash is not None
    assert user.password_hash != "Password@123"


async def test_create_user_service_duplicate_username(
    db_session,
):
    user_service = UserService(db_session)

    payload = RegisterUserSchema(
        username="testuser",
        email="test@example.com",
        password="Password@123",
    )

    user = await user_service.create(payload)

    assert user.id is not None

    duplicate_payload = RegisterUserSchema(
        username="testuser",
        email="another@example.com",
        password="Password@123",
    )

    try:
        await user_service.create(duplicate_payload)

        assert False

    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "username or email already exists"


async def test_create_user_service_duplicate_email(
    db_session,
):
    user_service = UserService(db_session)

    payload = RegisterUserSchema(
        username="testuser",
        email="test@example.com",
        password="Password@123",
    )

    user = await user_service.create(payload)

    assert user.id is not None

    duplicate_payload = RegisterUserSchema(
        username="anotheruser",
        email="test@example.com",
        password="Password@123",
    )

    try:
        await user_service.create(duplicate_payload)

        assert False

    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "username or email already exists"


async def test_create_user_service_username_normalized(
    db_session,
):
    user_service = UserService(db_session)

    payload = RegisterUserSchema(
        username="  TestUser  ",
        email="test@example.com",
        password="Password@123",
    )

    user = await user_service.create(payload)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"


async def test_create_user_service_password_hashed(
    db_session,
):
    user_service = UserService(db_session)

    payload = RegisterUserSchema(
        username="secure_user",
        email="secure@example.com",
        password="Password@123",
    )

    user = await user_service.create(payload)

    assert user.id is not None
    assert user.username == "secure_user"
    assert user.email == "secure@example.com"

    # ensure raw password is not stored
    assert user.password_hash != "Password@123"

    assert user.password_hash is not None


async def test_login_user_service_success(
    db_session,
):
    user_service = UserService(db_session)

    register_payload = RegisterUserSchema(
        username="testuser",
        email="test@example.com",
        password="Password@123",
    )

    await user_service.create(register_payload)

    login_payload = UsernameLoginSchema(
        username="testuser",
        password="Password@123",
    )

    token_response = await user_service.login(login_payload)

    assert token_response is not None
    assert token_response.token is not None
    assert token_response.token_type == "bearer"


async def test_login_user_service_invalid_username(
    db_session,
):
    user_service = UserService(db_session)

    login_payload = UsernameLoginSchema(
        username="invalid_user",
        password="Password@123",
    )

    try:
        await user_service.login(login_payload)

        assert False

    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.detail == "invalid user credentials"


async def test_login_user_service_invalid_password(
    db_session,
):
    user_service = UserService(db_session)

    register_payload = RegisterUserSchema(
        username="testuser",
        email="test@example.com",
        password="Password@123",
    )

    await user_service.create(register_payload)

    login_payload = UsernameLoginSchema(
        username="testuser",
        password="WrongPassword@123",
    )

    try:
        await user_service.login(login_payload)

        assert False

    except HTTPException as exc:
        assert exc.status_code == 401

        assert exc.detail == "invalid user credentials"


async def test_login_user_service_returns_valid_jwt(
    db_session,
):
    user_service = UserService(db_session)

    register_payload = RegisterUserSchema(
        username="jwt_user",
        email="jwt@example.com",
        password="Password@123",
    )

    created_user = await user_service.create(register_payload)

    login_payload = UsernameLoginSchema(
        username="jwt_user",
        password="Password@123",
    )

    token_response = await user_service.login(login_payload)

    payload = verify_access_token(token_response.token)

    assert payload is not None
    assert payload["sub"] == created_user.id
