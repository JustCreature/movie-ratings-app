import uuid

from starlette import status

from app.domain.repositories.movie_repository import MovieRepository


async def test_create_movie(test_client, db_session):
    # Arrange
    new_movie = {
      "title": "test",
      "description": "test"
    }

    # Act
    response = test_client.post("api/v1/movies", json=new_movie)
    response_data = response.json()
    db_movie = await MovieRepository.find(db_session)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED

    assert "id" in response_data
    assert response_data["title"] == new_movie["title"]
    assert response_data["description"] == new_movie["description"]

    assert len(db_movie) == 1
    assert db_movie[0].title == new_movie["title"]
    assert db_movie[0].description == new_movie["description"]


async def test_create_user_fails_if_movie_exsits(test_client, db_session):
    # Arrange
    new_movie = {
        "title": "test",
        "description": "test"
    }
    _ = await MovieRepository.create(db_session, commit=True, **new_movie)

    # Act
    response = test_client.post("api/v1/movies", json=new_movie)
    response_data = response.json()
    db_movies = await MovieRepository.find(db_session)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT

    assert response_data["detail"] == f"Movie already exists with title {new_movie["title"]}"

    assert len(db_movies) == 1
    assert db_movies[0].title == new_movie["title"]
    assert db_movies[0].description == new_movie["description"]


async def test_get_movies(test_client, db_session):
    # Arrange
    new_movies = [
        {"title": "test","description": "test"},
        {"title": "test_1", "description": "test_1"},
    ]
    movie_1 = await MovieRepository.create(db_session, commit=True, **new_movies[0])
    movie_2 = await MovieRepository.create(db_session, commit=True, **new_movies[1])

    # Act
    response = test_client.get(f"api/v1/movies")
    response_data = response.json()

    # Assert
    assert response.status_code == status.HTTP_200_OK

    assert response_data["total"] == 2
    assert response_data["items"][0]["id"] == str(movie_1.id)
    assert response_data["items"][1]["id"] == str(movie_2.id)


async def test_get_movie_not_found(test_client, db_session):
    # Arrange
    new_movies = [
        {"title": "test", "description": "test"},
    ]
    movie = await MovieRepository.create(db_session, commit=True, **new_movies[0])

    # Act
    response = test_client.get(f"api/v1/movies/{uuid.uuid4()}")
    response_data = response.json()

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response_data["detail"] == "Movie not found"
