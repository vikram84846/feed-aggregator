from app.db.repos.user_repo import UserRepository


async def test_user_create_username_only(db_session):
    user_repo = UserRepository(db_session)
    user =await user_repo.create(
        username="karan"
    )
    assert user.id is not None
    assert user.username == "karan"
    assert user.email == None
    assert user.password_hash is None
    assert user.is_deleted == False




async def test_user_create_with_password_hash(db_session):
    user_repo = UserRepository(db_session)

    user = await user_repo.create(username="test-user",password_hash="test_hash_password")
    assert user.id is not None
    assert user.username == "test-user"
    assert user.email == None
    assert user.password_hash == "test_hash_password"
    assert user.is_deleted == False


async def test_user_create_with_email_and_password_hash(db_session):
    user_repo = UserRepository(db_session)

    user = await user_repo.create(username="test-user",password_hash="test_hash_password",email="Test123@test.com")
    assert user.id is not None
    assert user.username == "test-user"
    assert user.email == "Test123@test.com"
    assert user.password_hash == "test_hash_password"
    assert user.is_deleted == False


async def test_user_get_by_id(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user",password_hash="test_hash_password",email="Test123@test.com")
    user_id = user.id

    # fetch the user by id 
    test_user = await user_repo.get_by_id(user_id)
    assert test_user.id == user_id
    assert test_user.username == "test-user"
    assert test_user.password_hash == "test_hash_password"
    assert test_user.email == "Test123@test.com"


async def test_user_get_by_email(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user",password_hash="test_hash_password",email="Test123@test.com")

    # fetch the user by email
    test_user = await user_repo.get_by_email("Test123@test.com")
    assert test_user.id is not None
    assert test_user.username == "test-user"
    assert test_user.password_hash == "test_hash_password"
    assert test_user.email == "Test123@test.com"


async def test_user_get_by_username(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user",password_hash="test_hash_password",email="Test123@test.com")


    # fetch the user by username
    test_user = await user_repo.get_by_username("test-user")
    assert test_user.id is not None
    assert test_user.username == "test-user"
    assert test_user.password_hash == "test_hash_password"
    assert test_user.email == "Test123@test.com"

async def test_user_delete(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user",password_hash="test_hash_password",email="Test123@test.com")
    user_id = user.id

    # delete the user by id 
    test_user = await user_repo.delete(user_id)
    assert test_user.is_deleted == True
    

async def test_get_by_invalid_id(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_id("invalid-id")
    assert user == None

async def test_get_by_invalid_username(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_username("invalid-username")
    assert user == None

async def test_get_by_invalid_email(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_email("invalid-email")
    assert user == None

async def test_delete_invalid_user(db_session):
    user_repo = UserRepository(db_session)

    # delete the user by id 
    test_user = await user_repo.delete("invalid-id")
    assert test_user is None


async def test_user_delete_deleted_user(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user",password_hash="test_hash_password",email="Test123@test.com")
    user_id = user.id

    # delete the user by id 
    await user_repo.delete(user_id)
    test_user = await user_repo.delete(user_id)
    assert test_user.is_deleted == True
    