
# movie-ratings-app

You can see all the instructions for the installation below, here is a nit of a description:
## ✅ Requirements

- [x] The backend should expose RESTful endpoints to handle user input and
  return movie ratings.
- [x] The system should store data in a database. You can use any existing
  dataset or API to populate the initial database.
- [x] Implement user endpoints to create and view user information.
- [x] Implement movie endpoints to create and view movie information.
- [x] Implement a rating system to rate the entertainment value of a movie.
- [x] Implement a basic profile where users can view their rated movies.
- [x] Include unit tests to ensure the reliability of your code.
- [x] Ensure proper error handling and validation of user inputs.

## ✨ Bonus Points

- [ ] Implement authentication and authorization mechanisms for users.
- [x] Provide documentation for your API endpoints using tools like Swagger.
- [x] Implement logging to record errors and debug information.
- [ ] Implement caching mechanisms to improve the rating system's performance.
- [x] Implement CI/CD quality gates.

### Quick info:

- you can hit /docs to get openAPI documentation
- in the repo you can see 2 MRs one of tham fails on linters and another one is all green :)
- you can run it all locally and see the logs
- other than that it's pretty basic logic because I concentrated on implementation,
it uses repository pattern with a generic repo for easy access to DB,
some logic can of course be extracted to services to make it even more abstract but for now it seems to be an overkill

### Start
To start you need to set up local dependencies, 
install **python 3.12.4** and **poetry 2.1.3**

Run te following command
```shell
poetry config virtualenvs.in-project true
```

## How to run the service locally
1. Clone the repo
2. Setup the project
```shell
make install
```
2. Run with a clean DB
```shell
make new-db-start
```
3. Run the service locally
```shell
make start-db
make run
```

## How to test the service
```shell
make start-db
make test
```

Test with coverage
```shell
make start-db
make test-with-coverage
```


## Before pushing new code
Make sure you run the following command before committing your code to the repo:
```shell
 make lint-full-check 
```
This will run the lint and the checking types tools and will warn you if there is something you need to change in order to follow standards.
