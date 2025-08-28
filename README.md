# my todos
* Read mosquito docu
* Read influxDb docu

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

# todo
Phase 0: Foundation & Setup (The "Hello, World!" of Infrastructure)
1. [ ] Install Docker and Docker Compose on your Raspberry Pi.

2. [ ] Create the project folder structure as outlined above.

3. [ ] Create the docker-compose.yml and .env files.

4. [ ] Add only the mosquitto and influxdb services to docker-compose.yml for now.

5. [ ] Run docker-compose up -d.

6. [ ] Verify:

7. [ ] Check that the containers are running with docker ps.

8. [ ] Access the InfluxDB setup UI in your browser at http://<your_pi_ip>:8086.

Phase 1: The Core Data Pipeline (Getting Data IN)

7.  [ ] Write the first version of the sensor_reader service (services/sensor_reader/main.py). For now, it can just generate fake data (e.g., a random number) and publish it to an MQTT topic like home/test/temperature.
8.  [ ] Write the first version of the db_logger service (services/db_logger/main.py). It should connect to Mosquitto, subscribe to home/test/temperature, and print any received messages to the console.
9.  [ ] Create a Dockerfile for each of these services.
10. [ ] Add sensor_reader and db_logger to your docker-compose.yml.
11. [ ] Run docker-compose up --build.
12. [ ] Verify: Watch the logs of the db_logger (docker-compose logs -f db_logger) to see the fake data appearing.
13. [ ] Now, enhance the db_logger to write the received data to InfluxDB.
14. [ ] Verify: Use the InfluxDB UI to query the database and confirm that data is being stored correctly.
15. [ ] Replace the fake data in sensor_reader with code to read from your actual physical sensor.

Phase 2: The Read API & Frontend (Getting Data OUT)

16. [ ] Build the FastAPI web_app (web_app/api/main.py). Create a single endpoint (e.g., /api/readings/last_hour) that queries InfluxDB and returns the data as JSON.
17. [ ] Add the web_app to docker-compose.yml.
18. [ ] Verify: Start the system and access the API endpoint in your browser (http://<your_pi_ip>:8000/api/readings/last_hour) to see the JSON data.
19. [ ] Create a simple index.html file in web_app/frontend/. Use a JavaScript library like Chart.js to fetch data from your API and draw a plot.

Phase 3: Intelligence & Remote Access

20. [ ] Create the telegram_bot service.
21. [ ] Implement a command (e.g., /now) that calls your FastAPI to get the latest reading.
22. [ ] Implement the real-time alert feature by having the bot subscribe to MQTT topics and send a message if a value crosses a threshold.
23. [ ] Create the system_monitor service to publish Pi CPU temp, usage, etc., to MQTT. Update the db_logger to also save this data.

Phase 4: Production-izing

24. [ ] Set up a secure remote access method (e.g., install Tailscale on the Pi).
25. [ ] Write Ansible playbooks to automate the setup of a new Raspberry Pi (installing Docker, cloning the repo, etc.).
26. [ ] Implement a backup strategy for your InfluxDB volume.