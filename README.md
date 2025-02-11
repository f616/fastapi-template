# FastAPI MySQL Authentication Example

This project demonstrates a FastAPI application using **Python 3.10** that connects to a MySQL database and provides endpoints to interact with an inventory (`inv`) table. The application implements JWT-based authentication via OAuth2 and stores sensitive credentials in a `.env` file. The project is containerized using Docker and orchestrated with Docker Compose (v2). Additionally, the project includes tests (using `pytest`) and a sample CI/CD configuration (GitHub Actions) for automated testing.

## Features

- **FastAPI** for building the API.
- **Python 3.10** as the runtime.
- **MySQL** as the database.
- **SQLAlchemy** as the ORM.
- **JWT-based Authentication** using OAuth2.
- **Password Hashing** with [passlib](https://passlib.readthedocs.io/).
- **Environment Configuration** via a `.env` file.
- **Containerization** with Docker and Docker Compose (v2).
- **Testing with Pytest** for automated tests.
- **CI/CD Integration** (sample GitHub Actions workflow).

## Folder Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py               # Application entry point.
│   ├── config.py             # Loads settings from .env.
│   ├── database.py           # SQLAlchemy engine and session.
│   ├── models.py             # SQLAlchemy models (User & Inv).
│   ├── schemas.py            # Pydantic models for validation.
│   ├── auth.py               # Utility functions for authentication.
│   └── routers/
│       ├── __init__.py
│       ├── auth.py           # Authentication endpoints (e.g., /token).
│       └── inv.py            # Secured inventory endpoints.
├── tests/
│   └── test_main.py          # Pytest test cases.
├── .env                      # Environment variables (not committed to VCS).
├── .gitignore                # Ignores .env and other sensitive files.
├── Dockerfile                # Builds the FastAPI app container.
├── docker-compose.yml        # Orchestrates FastAPI and MySQL containers.
├── requirements.txt          # Python dependencies.
└── README.md                 # Project documentation.
```

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) (v2) installed on your system.
- **Python 3.10** (if running locally).
- Basic knowledge of Python, FastAPI, and SQL.

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd project
```

### 2. Create a `.env` File

Create a `.env` file at the root of the project and add the following content:

```dotenv
# .env

# Database configuration
DB_HOST=db
DB_USER=root
DB_PASSWORD=password
DB_NAME=test_db
DB_PORT=3306

# Security settings
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> **Note:** Do not commit the `.env` file to version control. It is already added to `.gitignore`.

### 3. Build and Run with Docker Compose

From the project root, run:

```bash
docker compose up --build
```

This command builds the FastAPI Docker image and starts both the FastAPI and MySQL containers.

### 4. Database Setup

After the containers are running, set up the required database tables. Connect to the MySQL container:

```bash
docker compose exec db mysql -u root -p
# Enter the password (e.g., password)
```

Then execute the following SQL commands:

```sql
USE test_db;

-- Create the user table (if it doesn't already exist)
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
);

-- Create the inv table (if it doesn't already exist)
CREATE TABLE IF NOT EXISTS inv (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL
);

-- (Optional) Insert sample inventory data
INSERT INTO inv (item_name, quantity) VALUES ('Widget', 100), ('Gadget', 50);
```

#### Creating a Sample User

Generate a hashed password using the helper function in `app/auth.py`. For example, in a Python shell:

```python
from app.auth import get_password_hash
print(get_password_hash("your_plain_password"))
```

Then, insert the user into the database (replace `<hashed_password>` with the output):

```sql
INSERT INTO user (username, hashed_password)
VALUES ('testuser', '<hashed_password>');
```

## API Endpoints

### Authentication

- **POST `/token`**

  Obtain a JWT access token by providing form data with `username` and `password`.

  **Example using `curl`:**

  ```bash
  curl -X POST -F "username=testuser" -F "password=your_plain_password" http://localhost/token
  ```

  **Response:**

  ```json
  {
      "access_token": "<JWT_TOKEN>",
      "token_type": "bearer"
  }
  ```

### Inventory

- **GET `/inv`**

  Retrieve inventory items. This endpoint requires a valid JWT token provided in the `Authorization` header.

  **Example using `curl`:**

  ```bash
  curl -H "Authorization: Bearer <JWT_TOKEN>" http://localhost/inv
  ```

## Using cURL to Pipe the Bearer Token in a Single Command

You can obtain the JWT token and immediately use it to access a secured endpoint with a single piped command. For example, using `jq`:

```bash
curl -s -X POST -F "username=testuser" -F "password=your_plain_password" http://localhost/token \
| jq -r '.access_token' \
| xargs -I {} curl -H "Authorization: Bearer {}" http://localhost/inv
```

If you do not have `jq` installed, you can use Python instead:

```bash
curl -s -X POST -F "username=testuser" -F "password=your_plain_password" http://localhost/token \
| python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" \
| xargs -I {} curl -H "Authorization: Bearer {}" http://localhost/inv
```

### Explanation

- The first `curl` command sends a POST request to `/token` and retrieves a JSON response containing the access token.
- The output is piped into `jq` (or Python) to extract the `access_token`.
- The token is then passed to `xargs`, which uses it in the `Authorization` header of the subsequent `curl` command to call the `/inv` endpoint.

## Running Tests

This project uses `pytest` for testing. Tests are located in the `tests/` directory.

### 1. Install Testing Dependencies

Ensure that `pytest` is included in your `requirements.txt` and install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Run Tests

To run the tests locally, execute:

```bash
pytest
```

If you are running tests inside a Docker container, ensure that the container installs all dependencies (including `pytest`).

## CI/CD Integration

An example GitHub Actions workflow file is provided to run tests automatically on each push or pull request.

Create a file at `.github/workflows/test.yml` with the following content:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest
```

This workflow will run your tests on each push or pull request, helping to maintain code quality and prevent regressions.

## Troubleshooting

### Pydantic Warning

If you see a warning about `orm_mode` being renamed to `from_attributes` in Pydantic v2, update your Pydantic model configurations accordingly. For example:

```python
class InvItem(BaseModel):
    id: int
    item_name: str
    quantity: int

    class Config:
        from_attributes = True
```

### Database Connection Issues

If you encounter a `ConnectionRefusedError`, it means that your FastAPI container is attempting to connect to the MySQL container before it’s ready. To resolve this, use an entrypoint script that waits for MySQL to be ready.

## Waiting for MySQL to Be Ready (Entrypoint Script)

Create an `entrypoint.sh` file in your project root with the following content:

```bash
#!/bin/sh
# entrypoint.sh

# Wait for MySQL to be available on port 3306
while ! nc -z db 3306; do
  echo "Waiting for MySQL on db:3306..."
  sleep 2
done

echo "MySQL is up - starting the application."
exec uvicorn app.main:app --host 0.0.0.0 --port 80
```

> **Note:** In the Dockerfile, install `netcat-openbsd` instead of `netcat`:
>
> ```dockerfile
> RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*
> ```

Update your `Dockerfile` accordingly:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Copy the entrypoint script and make it executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 80

# Use the entrypoint script as the container entrypoint
ENTRYPOINT ["./entrypoint.sh"]
```

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).