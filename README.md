# KanMind

A Django REST Framework backend for Kanban-style task management — boards,
tasks, comments, and token-based authentication.

## Features

- User registration and login with token authentication
- Email availability check
- Board management (owner and members)
- Task creation, assignment, review workflow, and comments
- Object-level permissions (owner / member / author rules)
- Local development with SQLite

## Tech Stack

- Python 3.14
- Django 6.0
- Django REST Framework (token authentication)
- django-cors-headers
- SQLite (local development)

## Project Structure

```text
.
├── auth_app/      # Registration, login, email-check
├── kanban_app/    # Boards, tasks, comments
├── core/          # Django settings and root URL routing
├── docs/          # Project requirements and API documentation
├── manage.py
├── requirements.txt
└── pytest.ini
```

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd KanMind
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. (Optional) Create an admin user

```bash
python manage.py createsuperuser
```

The Django admin is then available at `http://127.0.0.1:8000/admin/`.

### 6. Run the development server

```bash
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`.

## Authentication

KanMind uses token-based authentication. Protected endpoints require an
`Authorization: Token <token>` header. Registration and login return the token.

Public endpoints:

```text
POST /api/registration/
POST /api/login/
```

## API Overview

All endpoints use the `/api/` prefix.

| Resource | Method | Endpoint                      | Description                              |
| -------- | -----: | ----------------------------- | ---------------------------------------- |
| Auth     |   POST | `/registration/`              | Register a new user                      |
| Auth     |   POST | `/login/`                     | Log in and receive an auth token         |
| Auth     |    GET | `/email-check/?email=`        | Check whether an email belongs to a user |
| Boards   |    GET | `/boards/`                    | List boards the user owns or belongs to  |
| Boards   |   POST | `/boards/`                    | Create a board                           |
| Boards   |    GET | `/boards/{id}/`               | Retrieve a board with members and tasks  |
| Boards   |  PATCH | `/boards/{id}/`               | Update a board's title and members       |
| Boards   | DELETE | `/boards/{id}/`               | Delete a board (owner only)              |
| Tasks    |    GET | `/tasks/assigned-to-me/`      | Tasks assigned to the current user       |
| Tasks    |    GET | `/tasks/reviewing/`           | Tasks the current user reviews           |
| Tasks    |   POST | `/tasks/`                     | Create a task on a board                 |
| Tasks    |  PATCH | `/tasks/{id}/`                | Update a task                            |
| Tasks    | DELETE | `/tasks/{id}/`                | Delete a task (creator or board owner)   |
| Comments |    GET | `/tasks/{id}/comments/`       | List a task's comments                   |
| Comments |   POST | `/tasks/{id}/comments/`       | Add a comment to a task                  |
| Comments | DELETE | `/tasks/{id}/comments/{cid}/` | Delete a comment (author only)           |

Full request/response schemas are documented in
[`docs/projekt/api-endpunkte.md`](docs/projekt/api-endpunkte.md).

## Running Tests

```bash
python manage.py test
```

With coverage:

```bash
coverage run --source=auth_app,kanban_app manage.py test
coverage report -m
```

Tests can also be run via pytest (configured in `pytest.ini`):

```bash
pytest
```

## Author

Michael Friggemann
