# Distributed File Processor

## Overview

The Distributed File Processor is a microservices-based application designed to efficiently process CSV files in a distributed manner. This application leverages Docker, RabbitMQ, and PostgreSQL to handle file uploads, message queuing, and data storage, respectively.

## Features

- **Microservices Architecture**: Composed of multiple services that can be scaled independently.
- **File Uploading**: Users can upload CSV files via a RESTful API.
- **Message Queue**: Utilizes RabbitMQ to queue messages for processing.
- **Data Storage**: Stores processed data in a PostgreSQL database.
- **Scalability**: Easily scale the number of consumer services to handle more load.

## Architecture

The architecture consists of the following components:

- **Service A**: Handles file uploads and sends messages to the RabbitMQ queue.
- **Service B**: Reads the uploaded CSV file, formats the data, and sends messages to RabbitMQ.
- **Service C**: Consumes messages from RabbitMQ and writes data to PostgreSQL.
- **RabbitMQ**: Acts as the message broker.
- **PostgreSQL**: The relational database where processed data is stored.
- **pgAdmin**: A web-based interface for managing PostgreSQL databases.

## Requirements

- Docker
- Docker Compose

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ayeshrodz/distributed-file-processor.git
cd distributed-file-processor
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory and configure the following variables:

```env
UPLOAD_FOLDER=/app/process_files
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=csv_data
POSTGRES_PORT=5432
RABBITMQ_DEFAULT_USER=your_rabbitmq_user
RABBITMQ_DEFAULT_PASS=your_rabbitmq_password
PGADMIN_DEFAULT_EMAIL=your_pgadmin_email
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
```

### 3. Build and Start the Services

```bash
docker-compose up --build
```

### 4. Access the Application

- **Service A**: Access the file upload API at `http://localhost:5000/process_file`.
- **pgAdmin**: Access pgAdmin at `http://localhost:8080`, using the credentials specified in your `.env` file.

## Usage

### Upload a CSV File

Send a POST request to the `/process_file` endpoint with the path to the CSV file:

```bash
curl -X POST http://localhost:5000/process_file -H "Content-Type: application/json" -d '{"file_path": "/app/process_files/your_file.csv"}'
```

### Monitor RabbitMQ

You can monitor the RabbitMQ queue and messages through the RabbitMQ management interface at `http://localhost:15672` using the RabbitMQ credentials specified in your `.env` file.

## Development

### Stop All Services

To stop all running services:

```bash
docker-compose down
```

### Scale Service C

To stop only Service C:

```bash
docker-compose stop service_c
```

To rebuild and start Service C:

```bash
docker-compose up --build service_c
```

## Contributing

Contributions are welcome! Please fork the repository and create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
