import uuid

from starlette import status

from app.domain.repositories.user_repository import UserRepository


async def test_create_user(test_client, db_session):
    # Arrange
    new_user = {"name": "Test", "email": "test@test.test"}

    # Act
    response = test_client.post("api/v1/users", json=new_user)
    response_data = response.json()
    db_users = await UserRepository.find(db_session)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED

    assert "id" in response_data
    assert response_data["name"] == new_user["name"]
    assert response_data["email"] == new_user["email"]

    assert len(db_users) == 1
    assert db_users[0].email == new_user["email"]
    assert db_users[0].name == new_user["name"]


async def test_create_user_fails_if_user_exsits(test_client, db_session):
    # Arrange
    new_user = {"name": "Test", "email": "test@test.test"}
    _ = await UserRepository.create(db_session, commit=True, **new_user)

    # Act
    response = test_client.post("api/v1/users", json=new_user)
    response_data = response.json()
    db_users = await UserRepository.find(db_session)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT

    assert response_data["detail"] == "User already exists with email test@test.test"

    assert len(db_users) == 1
    assert db_users[0].email == new_user["email"]
    assert db_users[0].name == new_user["name"]


async def test_get_user(test_client, db_session):
    # Arrange
    new_users = [
        {"name": "Test", "email": "test@test.test"},
    ]
    user = await UserRepository.create(db_session, commit=True, **new_users[0])

    # Act
    response = test_client.get(f"api/v1/users/{user.id}")
    response_data = response.json()

    # Assert
    assert response.status_code == status.HTTP_200_OK

    assert response_data["id"] == str(user.id)
    assert response_data["name"] == user.name
    assert response_data["email"] == user.email


async def test_get_user_not_found(test_client, db_session):
    # Arrange
    new_users = [
        {"name": "Test", "email": "test@test.test"},
    ]
    user = await UserRepository.create(db_session, commit=True, **new_users[0])

    # Act
    response = test_client.get(f"api/v1/users/{uuid.uuid4()}")
    response_data = response.json()

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response_data["detail"] == "User not found"
