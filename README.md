# Pet Management Backend – Microservices (FastAPI + MongoDB + Nginx)

Python + FastAPI microservices with MongoDB. **Docker is not used**; Nginx runs as a reverse proxy and each service runs locally.

## Architecture

- **auth_user_service** (port 8000) – Auth and user (register, login, JWT, forgot/reset password).
- **species_service** (port 8001) – Species CRUD (admin only).
- **pet_service** (port 8002) – Pet CRUD (list/get public; create/update/delete admin).
- **adoption_service** (port 8003) – Adoption apply, my applications, admin list/approve/reject.
- **Nginx** (port 8080) – Reverse proxy; single entry point for the API.

All services use the **same MongoDB** database (`pet_management`) and the same **JWT secret** so tokens issued by the auth service can be validated by the others.

## Prerequisites

- Python 3.11+
- MongoDB running (e.g. `mongodb://localhost:27017`)
- Nginx (optional; for single entry point)

## Setup

### 1. MongoDB

Ensure MongoDB is running and reachable at `mongodb://localhost:27017` (or set `MONGODB_URI` in each service’s `.env`).

### 2. Environment

Each service can use a `.env` in its folder (or in `app/`). Shared values:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=pet_management
JWT_SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
```

Create `.env` in:

- `auth_user_service/`
- `species_service/`
- `pet_service/`
- `adoption_service/`

(or copy from a single `.env.example` at repo root).

### 3. Install dependencies and run services

From the **project root** (`pet_management_backend_microservice/`):

```bash
# Auth user service (port 8000)
cd auth_user_service
pip install -r requirements.txt
cd app && uvicorn main:app --reload --port 8000
# Leave running; open a new terminal for each service below.

# Species service (port 8001)
cd species_service
pip install -r requirements.txt
cd app && uvicorn main:app --reload --port 8001

# Pet service (port 8002)
cd pet_service
pip install -r requirements.txt
cd app && uvicorn main:app --reload --port 8002

# Adoption service (port 8003)
cd adoption_service
pip install -r requirements.txt
cd app && uvicorn main:app --reload --port 8003
```

Run each in a separate terminal (or use a process manager).

### 4. Nginx (optional)

1. Download Nginx for Windows from [nginx.org](https://nginx.org/en/download.html) and extract.
2. Replace the `conf/nginx.conf` in the Nginx folder with the repo’s `nginx.conf` (or merge the `http { ... }` block).
3. Start Nginx, e.g. `nginx.exe` from the Nginx directory.

Then the API is available at **http://localhost:8080**:

- `http://localhost:8080/api/auth/...`
- `http://localhost:8080/api/species/...`
- `http://localhost:8080/api/pets/...`
- `http://localhost:8080/api/adoptions/...`

Without Nginx, call each service by port:

- Auth: `http://localhost:8000/api/auth/...`
- Species: `http://localhost:8001/api/species/...`
- Pets: `http://localhost:8002/api/pets/...`
- Adoptions: `http://localhost:8003/api/adoptions/...`

## API overview (aligned with Node backend)

Response shape: `{ "statusCode", "success", "message", "result" }`.

### Auth (`/api/auth/`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/test` | Health/test |
| POST | `/register` | Register (firstName, lastName, email, password) |
| POST | `/login` | Login (email, password) → returns user + token |
| GET | `/validate-token` | Validate JWT (Authorization: Bearer &lt;token&gt;) |
| POST | `/send-verification-link` | Send reset link (email, path) |
| POST | `/forgot-password` | Change password (requires auth; body: password) |
| POST | `/reset-password` | Reset with token (token, password) |

### Species (`/api/species/`) – admin only

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List (query: page, limit) |
| GET | `/{id}` | Get by id |
| POST | `/` | Create (body: name) |
| PUT | `/{id}` | Update (body: name) |
| DELETE | `/{id}` | Soft delete |

### Pets (`/api/pets/`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List (query: page, limit, search, species, breed, ageMin, ageMax, status) – public |
| GET | `/{id}` | Get by id – public |
| POST | `/` | Create – admin (body: name, species, breed, age, description?, imageUrl?) |
| PUT | `/{id}` | Update – admin |
| DELETE | `/{id}` | Soft delete – admin |

### Adoptions (`/api/adoptions/`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Apply – authenticated (body: petId, message?) |
| GET | `/my` | My applications – authenticated |
| GET | `/` | List all – admin (query: page, limit, status) |
| GET | `/{id}` | Get by id – admin |
| PATCH | `/{id}/approve` | Approve – admin |
| PATCH | `/{id}/reject` | Reject – admin |

## Project structure (per service)

```
<service>/
  app/
    main.py
    core/       # config, database, response, messages
    schema/     # Pydantic request/response
    routes/     # FastAPI routers
    controller/ # Business logic
    middlewares/# JWT auth, require_admin
    utils/      # jwt, password
  requirements.txt
```

## Notes

- First registered user gets role `admin`; rest get `user`.
- JWT payload includes `id`, `email`, `role`; all services use the same `JWT_SECRET_KEY` to validate.
- Nginx is only for routing; run services and MongoDB as above when not using Docker.
