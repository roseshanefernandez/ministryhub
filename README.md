# Django Portfolio Project

A production-ready Django portfolio application with Dockerized local development, PostgreSQL support, Nginx reverse proxy, self-signed SSL for production, and AWS EC2/RDS deployment support.

The project is designed as a clean foundation for showcasing portfolio projects while also demonstrating modern deployment and DevOps practices.

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [Production Deployment](#production-deployment)
- [SSL Setup](#ssl-setup)
- [CI/CD](#cicd)
- [Useful Commands](#useful-commands)
- [Troubleshooting](#troubleshooting)

## Overview

This project is a Django-based portfolio website that can be run locally with Docker and deployed to an AWS EC2 instance using Docker Compose.

It supports:

- Local PostgreSQL database via Docker
- Production PostgreSQL database via Amazon RDS
- Gunicorn as the production WSGI server
- Nginx as a reverse proxy
- HTTPS using self-signed SSL certificates
- GitHub Actions workflow for CI/CD preparation

## Tech Stack

- **Python**
- **Django**
- **PostgreSQL**
- **Docker**
- **Docker Compose**
- **Gunicorn**
- **Nginx**
- **GitHub Actions**
- **AWS EC2**
- **Amazon RDS**

## Features

- Django portfolio application
- Project listing support
- Dockerized development environment
- Separate development and production Docker Compose configurations
- PostgreSQL support for both local and production environments
- Static file handling for production
- Nginx reverse proxy configuration
- HTTPS support with self-signed certificates
- AWS EC2 deployment workflow
- GitHub Actions CI/CD workflow foundation

## Project Structure

A typical project layout looks like this:

```text
portfolio_project/
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements.txt
├── .env.dev
├── .env.prod
├── nginx/
│   └── gnginx.conf
├── certs/
│   ├── nginx.crt
│   └── nginx.key
├── static/
├── templates/
└── portfolio/
```

> Some files, such as environment files and SSL certificates, should not be committed to version control.

## Local Development

### 1. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
```

### 2. Create a development environment file

Create a `.env.dev` file in the project directory:

```ini
DJANGO_DEBUG=True
SECRET_KEY=<DJANGO_DEVELOPMENT_SECRET_KEY>
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=<LOCAL_DATABASE_NAME>
POSTGRES_USER=<LOCAL_DATABASE_USER>
POSTGRES_PASSWORD=<LOCAL_DATABASE_PASSWORD>
POSTGRES_HOST=db
POSTGRES_PORT=5432

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
DJANGO_LOG_LEVEL=INFO
```

### 3. Build and start the containers

```bash
docker compose up --build
```

### 4. Apply database migrations

In a separate terminal, run:

```bash
docker compose exec web python manage.py migrate
```

### 5. Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Open the application

Visit:

```text
http://localhost:8000
```

## Environment Variables

The project uses environment variables to separate local and production configuration.

### Development

Use `.env.dev` for local development.

Example values:

```ini
DJANGO_DEBUG=True
SECRET_KEY=<DJANGO_DEVELOPMENT_SECRET_KEY>
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=<LOCAL_DATABASE_NAME>
POSTGRES_USER=<LOCAL_DATABASE_USER>
POSTGRES_PASSWORD=<LOCAL_DATABASE_PASSWORD>
POSTGRES_HOST=db
POSTGRES_PORT=5432

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
DJANGO_LOG_LEVEL=INFO
```

### Production

Use `.env.prod` for production deployment.

Example values:

```ini
DJANGO_DEBUG=False
SECRET_KEY=<DJANGO_PRODUCTION_SECRET_KEY>
ALLOWED_HOSTS=<EC2_ELASTIC_IP>

POSTGRES_DB=<RDS_DATABASE_NAME>
POSTGRES_USER=<RDS_DATABASE_USER>
POSTGRES_PASSWORD=<RDS_DATABASE_PASSWORD>
POSTGRES_HOST=<RDS_ENDPOINT>
POSTGRES_PORT=5432

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
DJANGO_LOG_LEVEL=WARNING
```

## Production Deployment

The production setup is intended for deployment on an AWS EC2 instance with Amazon RDS as the database.

### Prerequisites

- AWS EC2 instance
- Elastic IP attached to the EC2 instance
- Amazon RDS PostgreSQL database
- Docker and Docker Compose installed on the EC2 instance
- SSH access to the EC2 instance
- Security groups configured for:
  - HTTP: `80`
  - HTTPS: `443`
  - SSH: `22`
  - PostgreSQL access from EC2 to RDS

### 1. Connect to the EC2 instance

```bash
ssh -i <PATH_TO_SSH_KEY> <EC2_USER>@<EC2_ELASTIC_IP>
```

### 2. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
```

### 3. Create the production environment file

Create `.env.prod`:

```ini
DJANGO_DEBUG=False
SECRET_KEY=<DJANGO_PRODUCTION_SECRET_KEY>
ALLOWED_HOSTS=<EC2_ELASTIC_IP>

POSTGRES_DB=<RDS_DATABASE_NAME>
POSTGRES_USER=<RDS_DATABASE_USER>
POSTGRES_PASSWORD=<RDS_DATABASE_PASSWORD>
POSTGRES_HOST=<RDS_ENDPOINT>
POSTGRES_PORT=5432

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
DJANGO_LOG_LEVEL=WARNING
```

### 4. Generate SSL certificates

Create a `certs` directory:

```bash
mkdir -p certs
```

Generate a self-signed certificate:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/nginx.key \
  -out certs/nginx.crt \
  -subj "/CN=<EC2_ELASTIC_IP>"
```

### 5. Start the production containers

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 6. Apply migrations

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### 7. Collect static files

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 8. Open the production site

Visit:

```text
https://<EC2_ELASTIC_IP>
```

Because the project uses a self-signed certificate, the browser may show a security warning. This is expected unless a certificate from a trusted certificate authority is used.

## SSL Setup

The production deployment uses self-signed SSL certificates mounted into the Nginx container.

Required files:

```text
certs/
├── nginx.crt
└── nginx.key
```

Generate them with:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/nginx.key \
  -out certs/nginx.crt \
  -subj "/CN=<EC2_ELASTIC_IP>"
```

For a public production website, consider using a registered domain and a trusted SSL certificate provider.

## CI/CD

The project includes a GitHub Actions workflow foundation for CI/CD.

The workflow is intended to support:

- Checking out the repository
- Preparing Docker build tooling
- Building Docker images
- Preparing deployment steps

Deployment to EC2 may still require manual execution depending on the hosting setup, SSH configuration, and credential management strategy.

## Useful Commands

### Development logs

```bash
docker compose logs -f
```

### Production logs

```bash
docker compose -f docker-compose.prod.yml logs -f
```

### Stop development containers

```bash
docker compose down
```

### Stop production containers

```bash
docker compose -f docker-compose.prod.yml down
```

### Restart development services

```bash
docker compose restart
```

### Restart production services

```bash
docker compose -f docker-compose.prod.yml restart
```

### Rebuild development containers

```bash
docker compose up --build --force-recreate
```

### Rebuild production containers

```bash
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
```

### Run Django shell

```bash
docker compose exec web python manage.py shell
```

### Create migrations

```bash
docker compose exec web python manage.py makemigrations
```

### Apply migrations

```bash
docker compose exec web python manage.py migrate
```

### Collect static files in production

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## Non-Docker Local Development (Quick Start)

These steps run the app directly on your machine without Docker.

### Windows PowerShell example

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

$env:DJANGO_SECRET_KEY = "dev"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1,testserver"

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Then open:

- http://localhost:8000/
- http://localhost:8000/accounts/login/
- http://localhost:8000/accounts/signup/

## Running Tests (without Docker)

Set the minimal required environment variables and run the Django test suite.

```powershell
python -m pip install -r requirements.txt

$env:DJANGO_SECRET_KEY = "test"
$env:DJANGO_ALLOWED_HOSTS = "testserver,localhost,127.0.0.1"

python manage.py test -v 2
```

## Troubleshooting

### Containers are not starting

Check container status:

```bash
docker compose ps
```

For production:

```bash
docker compose -f docker-compose.prod.yml ps
```

View logs:

```bash
docker compose logs -f
```

For production:

```bash
docker compose -f docker-compose.prod.yml logs -f
```

### Static files are not loading

Try running:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

Also verify that Nginx is configured to serve the static files directory correctly.

### Database connection fails

Check that:

- Database environment variables are correct
- PostgreSQL container is running locally
- RDS security groups allow access from EC2
- The database host and port are reachable
- The database name and user exist

### Site is not reachable on EC2

Check that:

- EC2 security groups allow inbound traffic on ports `80` and `443`
- Docker containers are running
- Nginx is running
- The Elastic IP is correctly assigned
- `ALLOWED_HOSTS` includes the EC2 Elastic IP

### Browser shows SSL warning

This is expected when using a self-signed SSL certificate.

To avoid browser warnings, use:

- A registered domain
- A trusted SSL certificate
- A certificate authority such as Let's Encrypt

## License

Add your preferred license information here.