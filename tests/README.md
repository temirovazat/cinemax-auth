### **How to Run Tests:**

Clone the repository and navigate inside the `tests` directory:
```
git clone https://github.com/temirovazat/cinemax-auth.git
```
```
cd cinemax-auth/tests/
```

Create a .env file and add settings for the tests:
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

Deploy and run tests in containers:
```
docker-compose up --build --exit-code-from tests
```