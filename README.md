# Radiant Home Monitor

This project is a home monitoring system designed to collect, store, and analyze environmental data from a house, with an initial focus on calculating the dew point to assess feasibility for radiant floor cooling.

The system is built on a modern, scalable microservice architecture, designed to be robust and flexible for future expansion.

---

## Core Architecture

The system uses a decoupled, event-driven architecture based on the MQTT protocol. This separates data producers (sensors) from data consumers (database, alert systems).

![Architecture Diagram](https://i.imgur.com/gK6lB2K.png) 
*(This is a hosted version of the diagram we discussed. You can create your own if you prefer.)*

* **Data Ingestion (Writing)**: Sensors publish data to an MQTT Broker. A dedicated `db_logger` service subscribes to these messages and writes them to the InfluxDB time-series database.
* **Data Retrieval (Reading)**: A FastAPI server provides a REST API for reading historical data from the database. This API is used by the web frontend and the Telegram bot for queries.
* **Real-time Alerts**: The Telegram bot also subscribes directly to the MQTT broker to provide instant push notifications for critical events.

---

## Technology Stack

* **Backend Services**: Python 3.10+
* **Messaging**: Mosquitto (MQTT Broker)
* **Database**: InfluxDB (Time-Series Database)
* **Web API**: FastAPI
* **Containerization**: Docker & Docker Compose
* **Deployment**: Ansible (planned)

---

## Setup and Installation

This entire system is designed to run using Docker, which simplifies setup and ensures consistency.

1.  **Prerequisites**:
    * Install [Docker](https://docs.docker.com/engine/install/) on your Raspberry Pi or host machine.
    * Install [Docker Compose](https://docs.docker.com/compose/install/).

2.  **Configuration**:
    * Create a file named `.env` in the root of the project. This file will hold all your secrets and configuration.
    * Populate it with initial values. See the `docker-compose.yml` file for required variables (e.g., `INFLUXDB_DB`, `INFLUXDB_ADMIN_USER`, `INFLUXDB_ADMIN_PASSWORD`, `TELEGRAM_BOT_TOKEN`).

3.  **Build and Run**:
    * From the root directory, build all the custom service images:
        ```bash
        docker-compose build
        ```
    * Launch the entire application stack in detached mode:
        ```bash
        docker-compose up -d
        ```

---

## Services Overview

* **Mosquitto**: The MQTT message broker. The central nervous system of the application.
* **InfluxDB**: The time-series database used for long-term storage of all sensor data.
* **`sensor_reader`**: A Python service that reads data from a physical sensor (e.g., DHT22) and publishes it to MQTT topics.
* **`db_logger`**: A Python service that subscribes to MQTT topics and writes the incoming data into InfluxDB. **This is the only service that writes to the database.**
* **`web_app` (FastAPI)**: A Python service that provides a read-only REST API to fetch historical data from InfluxDB.
* **`telegram_bot`**: A Python service that interacts with users via Telegram. It uses the API for historical data and subscribes to MQTT for real-time alerts.
