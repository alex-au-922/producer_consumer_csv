# Producer Consumer CSV

![Build Status](https://github.com/github/docs/actions/workflows/test.yml/badge.svg)
![Code Coverage](./coverage.svg)

## Table of contents

* [Producer Consumer CSV](#producer-consumer-csv)
   * [Description](#description)
   * [Architecture](#architecture)
      * [Requirements](#requirements)
      * [Database Schema](#database-schema)
         * [records](#records)
      * [Database Indexes](#database-indexes)
      * [Queue](#queue)
   * [Test Data](#test-data)
   * [Installation](#installation)
   * [Usage](#usage)
      * [Postgres in Docker](#postgres-in-docker)
      * [Running the application](#running-the-application)
      * [End to end test](#end-to-end-test)
   * [Unit tests](#unit-tests)
      * [Code coverage report](#code-coverage-report)

## Description
This is a simple producer consumer application that reads a csv file and writes the data to a database. The application is written in Python.

## Architecture
The application is composed of the following components:
- Producer (Reads the csv file and sends the data to the message queue)
- Consumer (Reads the data from the message queue and writes the data to the database)
- Persistent Message Queue (RabbitMQ)
- Database (Postgres)

All the components are running in docker containers. The producer and consumer are running in multiple containers. The producer and consumer containers are scaled using docker compose. The producer and consumer containers are running in different containers to simulate a real world scenario where the producer and consumer are running in different servers.

For performance, you can scale the number of consumer containers by changing the `CONSUMER_REPLICAS` variable in the .env file. The default value is 16.

### Requirements
- Python 3.11
- Docker
- Make

### Database Schema
The initialization script is located in the `database/assets` folder. The script will create the following tables:

#### records
|column|type|description|
|------|----|-----------|
|record_time|timestamp with timezone|The time when the record was generated|
|sensor_id|text|The id of the sensor|
|value|double precision|The value of the sensor|

### Database Indexes
|index|columns|
|-----|-------|
|PK|sensor_id, record_time|
|BRIN|record_time|
|HASH|sensor_id|

BRIN index is used for the `record_time` column as the data is generated in a sequential manner (time-series data). The HASH index is used for the `sensor_id` column as the data is usually queried by equality operation, but not range operation. The HASH index is more efficient than the BTREE index for equality operation.

### Queue
The queue is implemented using RabbitMQ. The queue is configured to be persistent. The queue is configured to be durable and the messages are configured to be persistent.

However, due to the complexity of the application, in this project the `get` operation is prefered over the `consume` operation, which stimulates a short polling queue.

## Test Data
The test data is generated using the `generate_csv_demo` command. The command will generate a csv file with the following columns:
- `record_time`: The time when the record was generated
- `sensor_id`: The id of the sensor
- `value`: The value of the sensor

You can check the section [Running the application](#running-the-application) for more details on how to generate the csv file.

## Installation
1. Clone the repository
2. Install make and docker
- For Ubuntu and Debian
```bash
$ sudo apt install make
```
- For Fedora and CentOS
```bash
$ sudo yum install make
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

1. First run the `generate_csv_demo` command to generate a csv file. You can change the following parameters in the .env:
- `GEN_NUM_SENSORS`
- `GEN_NUM_RECORDS`
- `GEN_START_DATE`
- `GEN_RECORD_INTERVAL`
- `GEN_TIMEZONE`

```bash
$ make gen_csv_demo
```

2. Run the following command to build the docker image
```bash
$ make build
```

3. Run the following command to start the docker compose stack. This will start the postgres database, rabbitmq, producer and different consumer containers. You can change the following parameters in the .env:
- `CONSUMER_REPLICAS`
```bash
$ make up
```

4. Run the following command to stop the docker compose stack
```bash
$ make down
```

### End to end test
While the unit tests are run as part of the build process, you can run the end to end test by running the following steps:

1. Change the

1. Run the make command `generate_csv_end_to_end_test`. It will generate 10 sensor's data of 5 records each. The data will be generated in the `records_test` folder.
```bash
$ make generate_csv_end_to_end_test
```

2. Run the following command to build the docker image
```bash
$ make build
```

3. Run the following command to start the docker compose stack. This will start the postgres database, rabbitmq, producer and different consumer containers. You can change the following parameters in the .env:
- `CONSUMER_REPLICAS`

```bash
$ make up
```

4. Query the database to check if the data has been written to the database and check the record with the following data from sql:
```sql
SELECT *
    FROM records
    ORDER BY sensor_id ASC, record_time ASC
```

|record_time|sensor_id|value|
|-----------|---------|-----|
|2021-01-01 00:00:00.000 +0800|17fc695a_4|0.9100387476052705|
|2021-01-01 00:00:01.000 +0800|17fc695a_4|0.9470819312177097|
|2021-01-01 00:00:02.000 +0800|17fc695a_4|0.9646317173285254|
|2021-01-01 00:00:03.000 +0800|17fc695a_4|0.5588283283219546|
|2021-01-01 00:00:04.000 +0800|17fc695a_4|0.10032294940781161|
|2021-01-01 00:00:00.000 +0800|23b8c1e9_1|0.17833466762332717|
|2021-01-01 00:00:01.000 +0800|23b8c1e9_1|0.5828395773770179|
|2021-01-01 00:00:02.000 +0800|23b8c1e9_1|0.6709222475097419|
|2021-01-01 00:00:03.000 +0800|23b8c1e9_1|0.08392094150600504|
|2021-01-01 00:00:04.000 +0800|23b8c1e9_1|0.519270757199653|
|2021-01-01 00:00:00.000 +0800|47378190_8|0.8730491223149253|
|2021-01-01 00:00:01.000 +0800|47378190_8|0.9269235181749119|
|2021-01-01 00:00:02.000 +0800|47378190_8|0.7912797041193453|
|2021-01-01 00:00:03.000 +0800|47378190_8|0.7901636441724763|
|2021-01-01 00:00:04.000 +0800|47378190_8|0.7886736978911509|
|2021-01-01 00:00:00.000 +0800|6b65a6a4_7|0.10293554590959142|
|2021-01-01 00:00:01.000 +0800|6b65a6a4_7|0.2888706613682428|
|2021-01-01 00:00:02.000 +0800|6b65a6a4_7|0.4279942939571587|
|2021-01-01 00:00:03.000 +0800|6b65a6a4_7|0.23512685053378612|
|2021-01-01 00:00:04.000 +0800|6b65a6a4_7|0.5272935984703412|
|2021-01-01 00:00:00.000 +0800|972a8469_3|0.7642357069109641|
|2021-01-01 00:00:01.000 +0800|972a8469_3|0.5701299072914774|
|2021-01-01 00:00:02.000 +0800|972a8469_3|0.17473379247794074|
|2021-01-01 00:00:03.000 +0800|972a8469_3|0.12464021515158785|
|2021-01-01 00:00:04.000 +0800|972a8469_3|0.5390567336729636|
|2021-01-01 00:00:00.000 +0800|9a1de644_5|0.3758090093767995|
|2021-01-01 00:00:01.000 +0800|9a1de644_5|0.33553000407688316|
|2021-01-01 00:00:02.000 +0800|9a1de644_5|0.9667728274172214|
|2021-01-01 00:00:03.000 +0800|9a1de644_5|0.9549845776369301|
|2021-01-01 00:00:04.000 +0800|9a1de644_5|0.7740952070735415|
|2021-01-01 00:00:00.000 +0800|b74d0fb1_6|0.3213794858378719|
|2021-01-01 00:00:01.000 +0800|b74d0fb1_6|0.5947556423536645|
|2021-01-01 00:00:02.000 +0800|b74d0fb1_6|0.8872919823927438|
|2021-01-01 00:00:03.000 +0800|b74d0fb1_6|0.28297514015876457|
|2021-01-01 00:00:04.000 +0800|b74d0fb1_6|0.6590113969392454|
|2021-01-01 00:00:00.000 +0800|bd9c66b3_2|0.36466072100083013|
|2021-01-01 00:00:01.000 +0800|bd9c66b3_2|0.8408935901254108|
|2021-01-01 00:00:02.000 +0800|bd9c66b3_2|0.8945802964470245|
|2021-01-01 00:00:03.000 +0800|bd9c66b3_2|0.027150264273096747|
|2021-01-01 00:00:04.000 +0800|bd9c66b3_2|0.9236042897439161|
|2021-01-01 00:00:00.000 +0800|bdd640fb_0|0.0746765216767864|
|2021-01-01 00:00:01.000 +0800|bdd640fb_0|0.8404332126798344|
|2021-01-01 00:00:02.000 +0800|bdd640fb_0|0.31870553433981874|
|2021-01-01 00:00:03.000 +0800|bdd640fb_0|0.825033074919654|
|2021-01-01 00:00:04.000 +0800|bdd640fb_0|0.7161990766355211|
|2021-01-01 00:00:00.000 +0800|c241330b_9|0.6940489142492581|
|2021-01-01 00:00:01.000 +0800|c241330b_9|0.7748088833830469|
|2021-01-01 00:00:02.000 +0800|c241330b_9|0.85280342321841|
|2021-01-01 00:00:03.000 +0800|c241330b_9|0.32443698906841056|
|2021-01-01 00:00:04.000 +0800|c241330b_9|0.4457555011219805|


## Unit tests
The unit tests are run as part of the CI pipeline. You can run the unit tests locally by running the following steps:

1. Run the make `setup_test_env` command to setup the test environment
```bash
$ make setup_test_env
```

2. Install the following pip packages:
```bash
$ pip install -r producer/requirements-dev.txt
$ pip install -r consumer/requirements-dev.txt
```

3. Run the following command to run the unit tests
```bash
$ make test
```

The unit test will run the both the producer and consumer unit tests. The coverage report will be generated in the `.coverage` file.

### Code coverage report
You can generate the code coverage report by visiting the following link: https://alex-au-922.github.io/producer_consumer_csv/
