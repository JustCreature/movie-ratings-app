
# movie-ratings-app

You can see all the instructions for the installation below, here is a nit of a description:


To start you need to set up local dependencies, 
install python 3.12.4 and poetry 2.1.3

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
3. Run the service
```shell
make run
```

## How to test the service
```shell
make test
```

Test with coverage
```shell
make test-with-coverage
```


## Before pushing new code
Make sure you run the following command before committing your code to the repo:
```shell
 make lint-full-check 
```
This will run the lint and the checking types tools and will warn you if there is something you need to change in order to follow standards.


## Integration tests
There is a folder called integration in tests folder. This folder contains the PSQL integration tests for the service. These tests are run with a real database everytime a commit is pushed to the repo.

### How to run the integration tests locally?

There's a command to run the integration tests locally. This command will run the tests in a docker container with a real database.
```shell
make local-integration-test
```
