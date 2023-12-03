# producer_consumer_csv

![Build Status](https://github.com/github/docs/actions/workflows/test.yml/badge.svg)
![Code Coverage](./coverage.svg)

## Description
This is a simple producer consumer application that reads a csv file and writes the data to a database. The application is written in Python.

## Installation
1. Clone the repository
2. Install make and docker
- For Ubuntu and Debian
```bash
sudo apt install make
```
- For Fedora and CentOS
```bash
sudo yum install make
```

For Docker installation, please refer to the [official documentation](https://docs.docker.com/engine/install/)

## Usage

### Postgres in Docker
If you don't have a postgres database running, you can use the docker image provided in this repository. The docker image is based on the official postgres docker image. The docker image is configured to create a database and a user with the following .env variables:

- `POSTGRES_VERSION_TAG`
- `POSTGRES_PORT`
- `POSTGRES_USERNAME`
- `POSTGRES_PASSWORD`
- `POSTGRES_DATABASE`

Please make sure you don't change the name of the variables as they are used in the python application as well.

### Running the application

1. Run the following command to build the docker image
```bash
$ make build
```
2. Run the following command to start the docker compose stack
```bash
$ make up / make up_d
```
The `up_d` command will run the container in detached mode.

3. Run the following command to stop the docker compose stack
```bash
$ make down
```
