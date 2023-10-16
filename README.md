## Cinemax Auth

[![python](https://img.shields.io/static/v1?label=python&message=3.8%20|%203.9%20|%203.10&color=informational)](https://github.com/temirovazat/cinemax-auth/actions/workflows/main.yml)
[![dockerfile](https://img.shields.io/static/v1?label=dockerfile&message=published&color=2CB3E8)](https://hub.docker.com/r/temirovazat/auth_api)
[![lint](https://img.shields.io/static/v1?label=lint&message=flake8%20|%20mypy&color=brightgreen)](https://github.com/temirovazat/cinemax-auth/actions/workflows/main.yml)
[![code style](https://img.shields.io/static/v1?label=code%20style&message=WPS&color=orange)](https://wemake-python-styleguide.readthedocs.io/en/latest/)
[![tests](https://img.shields.io/static/v1?label=tests&message=%E2%9C%94%2023%20|%20%E2%9C%98%200&color=critical)](https://github.com/temirovazat/cinemax-auth/actions/workflows/main.yml)

### **Description**

_The purpose of this project is to implement an authentication service for an online cinema. For this purpose, authentication and role management APIs have been developed based on the [Flask](https://flask.palletsprojects.com) framework. A relational database [PostgreSQL](https://www.postgresql.org) is used for storing user data and login history. User authentication is done using JWT tokens, and [Redis](https://redis.io) is used to store invalid access tokens. The application also features social login (OAuth protocol), distributed tracing for monitoring (Jaeger program), and rate limiting to prevent excessive server load. The project is launched through a proxy server [NGINX](https://nginx.org), which serves as the entry point for the web application. API endpoints are covered by tests using the [pytest](https://pytest.org) library._

### **Technologies**

```Python``` ```Flask``` ```PostgreSQL``` ```Redis``` ```NGINX``` ```Gunicorn``` ```PyTest``` ```Docker```

### **How to Run the Project:**

Clone the repository and navigate to the `infra` directory inside it:
```
git clone https://github.com/temirovazat/cinemax-auth.git
```
```
cd cinemax-auth/infra/
```

Create a `.env` file and add project settings:
```
nano .env
```
```
# PostgreSQL
POSTGRES_DB=users_database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

Deploy and run the project in containers:
```
docker-compose up
```

The API documentation will be available at:
```
http://127.0.0.1/openapi
```