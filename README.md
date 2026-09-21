# Streamlit SQL Lite

A simple multi-page [Streamlit](https://streamlit.io/) app that stores data in a local SQLite database. Admins log in with a username and password, then use the sidebar pages to add and view user records.

## Features

- Admin login with hashed passwords (bcrypt) and cookie-based sessions, using `streamlit-authenticator`
- SQLite database created automatically on first run
- Input and Display pages for managing user records (first name, last name, date of birth, gender)
- Docker support, with the database kept in a volume so data survives container restarts
- GitHub Actions workflow that builds and publishes the Docker image to GitHub Container Registry

## Tech stack

- Python 3.14
- Streamlit
- streamlit-authenticator
- SQLite (built into Python)
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker

## Project structure

```
.
├── main.py              # Home page and login
├── db.py                # Database setup and queries
├── pages/               # Additional Streamlit pages (Input, Display)
├── pyproject.toml       # Project dependencies
├── uv.lock              # Locked dependency versions
├── Dockerfile           # Instructions for building the image
├── .dockerignore        # Files excluded from the Docker image
├── .gitignore           # Files excluded from Git
└── .github/workflows/   # GitHub Actions workflow (build and push image)
```

## Default login

On first run, the app creates a default admin account:

| Username | Password   |
|----------|------------|
| `admin`  | `admin123` |

> **Change this before deploying anywhere public.** Also replace the hardcoded cookie key (`rand_key`) in `main.py` with a secret of your own.

## Run with Docker

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Option 1: Build the image yourself

```bash
git clone https://github.com/zai20220667-ops/StreamlitApp.git
cd StreamlitApp
docker build -t streamlit-sql-lite .
```

Then run it.

**PowerShell (Windows):**

```powershell
mkdir data
docker run -d -p 8501:8501 -v ${PWD}/data:/data --name my-app streamlit-sql-lite
```

**macOS / Linux:**

```bash
mkdir data
docker run -d -p 8501:8501 -v "$(pwd)/data":/data --name my-app streamlit-sql-lite
```

Open **http://localhost:8501** and log in.

### Option 2: Pull the prebuilt image

The GitHub Actions workflow publishes the image to GitHub Container Registry on every push to `main`:

```bash
docker pull ghcr.io/zai20220667-ops/streamlitapp:latest
docker run -d -p 8501:8501 -v "$(pwd)/data":/data --name my-app ghcr.io/zai20220667-ops/streamlitapp:latest
```




### What the flags mean

| Flag | Purpose |
|------|---------|
| `-d` | Run in the background |
| `-p 8501:8501` | Map port 8501 on your computer to port 8501 in the container |
| `-v ./data:/data` | Store the database in your local `data` folder so it persists |
| `--name my-app` | Give the container a name |

### About the database

The database file is **not** part of the image or the repository. When the container starts, the app creates `database.db` inside the mounted `data` folder if it doesn't already exist.

- **Fresh start:** mount an empty folder and the app creates a new database with the default admin account.
- **Use existing data:** put your existing `database.db` in the `data` folder before starting the container.
- **No volume:** if you leave out `-v`, data is stored inside the container and is lost when the container is removed.

The database location is controlled by the `DATABASE_PATH` environment variable, which the Dockerfile sets to `/data/database.db`. Override it with `-e DATABASE_PATH=/data/other.db`.

### Useful commands

```bash
docker ps                 # list running containers
docker logs my-app        # view app logs
docker stop my-app        # stop the container
docker start my-app       # start it again
docker rm -f my-app       # remove the container (data in ./data is kept)
```

To apply code changes, rebuild and re-run:

```bash
docker rm -f my-app
docker build -t streamlit-sql-lite .
docker run -d -p 8501:8501 -v "$(pwd)/data":/data --name my-app streamlit-sql-lite
```

## Run without Docker

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/zai20220667-ops/StreamlitApp.git
cd StreamlitApp
uv sync
uv run streamlit run main.py
```

The app opens at **http://localhost:8501**, and the database is created as `database.db` in the project folder.

## Continuous integration

`.github/workflows/docker-publish.yml` runs on every push to `main`. It builds the Docker image and pushes it to `ghcr.io` with two tags:

- `latest`
- `sha-<commit>`, which ties each image to the exact commit that built it

## Troubleshooting

- **"Cannot connect to the Docker daemon" or a 500 error:** Docker Desktop isn't running, or WSL 2 / virtualization isn't enabled.
- **"port is already allocated":** something else is using port 8501. Change the left number, e.g. `-p 8502:8501`, and open http://localhost:8502.
- **"name already in use":** remove the old container with `docker rm -f my-app`.
- **Page won't load:** check `docker logs my-app` and confirm `docker ps` shows `0.0.0.0:8501->8501/tcp`.

## Security notes

- Never commit `database.db`; it contains password hashes. It is listed in `.gitignore` and `.dockerignore`.
- Change the default admin password and the cookie key before exposing the app publicly.