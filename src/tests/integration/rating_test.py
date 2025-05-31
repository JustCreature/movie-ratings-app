import uuid

from starlette import status

from app.domain.repositories.movie_repository import MovieRepository
from app.domain.repositories.rating_repository import RatingRepository
from app.domain.repositories.user_repository import UserRepository


async def test_create_rating(test_client, db_session):
    # Arrange
    # create movies
    new_movies = [
        {"title": "test", "description": "test"},
    ]
    movie_1 = await MovieRepository.create(db_session, commit=True, **new_movies[0])

    # create users
    new_users = [
        {"name": "Test", "email": "test@test.test"},
    ]
    user_1 = await UserRepository.create(db_session, commit=True, **new_users[0])

    new_rating = {
        "movie_id": str(movie_1.id),
        "user_id": str(user_1.id),
        "rating": 2.0,
    }

    # Act
    response = test_client.post("api/v1/ratings", json=new_rating)
    response_data = response.json()
    db_ratings = await RatingRepository.find(db_session)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED

    assert "id" in response_data
    assert response_data["movie_id"] == new_rating["movie_id"]
    assert response_data["user_id"] == new_rating["user_id"]

    assert len(db_ratings) == 1
    assert str(db_ratings[0].movie_id) == new_rating["movie_id"]
    assert str(db_ratings[0].user_id) == new_rating["user_id"]
    assert db_ratings[0].rating == new_rating["rating"]


async def test_create_rating_fails_if_rating_exsits(test_client, db_session):
    # Arrange
    # create movies
    new_movies = [
        {"title": "test", "description": "test"},
        {"title": "test_1", "description": "test_1"},
    ]
    movie_1 = await MovieRepository.create(db_session, commit=True, **new_movies[0])
    _ = await MovieRepository.create(db_session, commit=True, **new_movies[1])

    # create users
    new_users = [
        {"name": "Test", "email": "test@test.test"},
        {"name": "Test_1", "email": "test_1@test.test"},
    ]
    user_1 = await UserRepository.create(db_session, commit=True, **new_users[0])
    _ = await UserRepository.create(db_session, commit=True, **new_users[1])

    new_rating = {
        "movie_id": movie_1.id,
        "user_id": user_1.id,
        "rating": 2.0,
    }
    _ = await RatingRepository.create(db_session, commit=True, **new_rating)
    new_rating = {
        "movie_id": str(movie_1.id),
        "user_id": str(user_1.id),
        "rating": 2.0,
    }

    # Act
    response = test_client.post("api/v1/ratings", json=new_rating)
    response_data = response.json()
    db_ratings = await RatingRepository.find(db_session)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT

    assert response_data["detail"] == "Rating already exists for this user/movie"

    assert len(db_ratings) == 1
    assert str(db_ratings[0].movie_id) == new_rating["movie_id"]
    assert str(db_ratings[0].user_id) == new_rating["user_id"]
    assert db_ratings[0].rating == new_rating["rating"]


async def test_get_ratings_by_movie_id(test_client, db_session):
    # Arrange
    # create movies
    new_movies = [
        {"title": "test", "description": "test"},
        {"title": "test_1", "description": "test_1"},
    ]
    movie_1 = await MovieRepository.create(db_session, commit=True, **new_movies[0])
    _ = await MovieRepository.create(db_session, commit=True, **new_movies[1])

    # create users
    new_users = [
        {"name": "Test", "email": "test@test.test"},
        {"name": "Test_1", "email": "test_1@test.test"},
    ]
    user_1 = await UserRepository.create(db_session, commit=True, **new_users[0])
    _ = await UserRepository.create(db_session, commit=True, **new_users[1])

    new_rating = {
        "movie_id": movie_1.id,
        "user_id": user_1.id,
        "rating": 2.0,
    }
    rating_1 = await RatingRepository.create(db_session, commit=True, **new_rating)

    # Act
    response = test_client.get(f"api/v1/ratings/{movie_1.id}")
    response_data = response.json()

    # Assert
    assert response.status_code == status.HTTP_200_OK

    assert response_data["total"] == 1
    assert str(response_data["items"][0]["id"]) == str(rating_1.id)
    assert str(response_data["items"][0]["movie_id"]) == str(movie_1.id)
    assert response_data["items"][0]["user_id"] == str(user_1.id)


async def test_get_rating_not_found(test_client, db_session):
    # Arrange
    # create movies
    new_movies = [
        {"title": "test", "description": "test"},
        {"title": "test_1", "description": "test_1"},
    ]
    movie_1 = await MovieRepository.create(db_session, commit=True, **new_movies[0])
    movie_2 = await MovieRepository.create(db_session, commit=True, **new_movies[1])

    # create users
    new_users = [
        {"name": "Test", "email": "test@test.test"},
        {"name": "Test_1", "email": "test_1@test.test"},
    ]
    user_1 = await UserRepository.create(db_session, commit=True, **new_users[0])
    _ = await UserRepository.create(db_session, commit=True, **new_users[1])

    new_rating = {
        "movie_id": str(movie_1.id),
        "user_id": str(user_1.id),
        "rating": 2.0,
    }
    rating_1 = await RatingRepository.create(db_session, **new_rating)

    # Act

    response = test_client.get(f"api/v1/ratings/{movie_2.id}")
    response_data = response.json()

    # Assert
    assert response.status_code == status.HTTP_200_OK

    assert response_data["total"] == 0
    assert len(response_data["items"]) == 0
