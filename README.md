# Streamlit SQL App

A simple multi-page [Streamlit](https://streamlit.io/) app backed by PostgreSQL. Admins log in with a username and password, then use the sidebar pages to add and view user records. The whole stack (app and database) runs with Docker Compose.

## Features

- Admin login with hashed passwords (bcrypt) and cookie-based sessions, using `streamlit-authenticator`
- PostgreSQL database, with tables created automatically on first run
- Input and Display pages for managing user records (first name, last name, date of birth, gender)
- One-command setup with Docker Compose
- GitHub Actions workflow that builds and publishes the Docker image to GitHub Container Registry

## Tech stack

- Python 3.14
- Streamlit and streamlit-authenticator
- PostgreSQL 17 (via `psycopg`)
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker and Docker Compose

## Project structure

```
.
├── main.py              # Home page and login
├── db.py                # Database connection, setup, and queries
├── pages/               # Additional Streamlit pages (Input, Display)
├── pyproject.toml       # Project dependencies
├── uv.lock              # Locked dependency versions
├── Dockerfile           # Builds the app image
├── compose.yaml         # Runs the app and PostgreSQL together
├── .env.example         # Template for required settings
├── .dockerignore        # Files excluded from the Docker image
├── .gitignore           # Files excluded from Git
└── .github/workflows/   # GitHub Actions workflow (build and push image)
```

## Configuration

All settings are read from a `.env` file that sits next to `compose.yaml`. This file holds secrets and is **never committed to Git**. Use `.env.example` as the template.

| Variable | Purpose |
|----------|---------|
| `POSTGRES_USER` | Database username |
| `POSTGRES_PASSWORD` | Database password (letters, numbers, and dashes are safest, since it is placed inside a URL) |
| `POSTGRES_DB` | Database name |
| `ADMIN_PASSWORD` | Password for the first `admin` account, used only when the admin user is first created |
| `COOKIE_KEY` | Secret used to sign login cookies. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"` |

## Run with Docker Compose

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Steps

```bash
git clone https://github.com/zai20220667-ops/StreamlitApp.git
cd StreamlitApp
```

Create your settings file from the template and edit it:

```bash
# Windows (PowerShell / cmd)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and replace every `change-me` value with your own. Then start everything:

```bash
docker compose up -d --build
```

Open **http://localhost:8501** and log in as `admin` with the `ADMIN_PASSWORD` you set.

### How it works

`compose.yaml` defines two services:

- **db**: a PostgreSQL container. Its data is stored in a Docker volume named `pgdata`.
- **app**: the Streamlit app, built from the `Dockerfile`. It waits for the database to report healthy, then starts, and connects to it at the hostname `db` (the service name).

### Access from other devices

The app is published on port 8501 of your computer, so other devices on the same network can open it at your machine's IP address:

1. Find your IP: run `ipconfig` (Windows) or `ip addr` (Linux) and look for the IPv4 address, for example `192.168.1.25`.
2. Open `http://192.168.1.25:8501` from another device on the same network.
3. If it doesn't load, allow the port through your firewall. On Windows, in PowerShell as Administrator:
   ```powershell
   New-NetFirewallRule -DisplayName "Streamlit 8501" -Direction Inbound -Protocol TCP -LocalPort 8501 -Action Allow
   ```

The database port is bound to `127.0.0.1` only, so it is reachable from your own computer (for tools like DBeaver) but not from the network.

### Useful commands

```bash
docker compose ps                # list services and their status
docker compose logs -f app       # follow the app logs
docker compose logs db           # view the database logs
docker compose down              # stop and remove containers (data is kept)
docker compose down -v           # also DELETE the database volume (all data)
docker compose up -d --build     # rebuild and restart after code changes
```

Open a SQL shell in the database:

```bash
docker compose exec db psql -U appuser -d appdb
```

(Use your own `POSTGRES_USER` and `POSTGRES_DB` values.)

### Data persistence

Database data lives in the `pgdata` volume, so it survives restarts, rebuilds, and `docker compose down`. It is only removed by `docker compose down -v`.

`ADMIN_PASSWORD` is only used when the database has no admin user yet. Changing it later does **not** change the existing admin's password. To start over with a new one, run `docker compose down -v` (this deletes all data) and bring the stack up again.

## Run without Docker

Requires Python 3.14+, [uv](https://docs.astral.sh/uv/), and a running PostgreSQL. The easiest way to get one is to start only the database from Compose:

```bash
docker compose up -d db
```

Then set the environment variables and run the app. In PowerShell:

```powershell
$env:DATABASE_URL="postgresql://appuser:your-password@localhost:5432/appdb"
$env:ADMIN_PASSWORD="your-admin-password"
$env:COOKIE_KEY="your-long-random-string"
uv sync
uv run streamlit run main.py
```

## Continuous integration

`.github/workflows/docker-publish.yml` runs on every push to `main`. It builds the Docker image and pushes it to `ghcr.io` with two tags:

- `latest`
- `sha-<commit>`, which ties each image to the exact commit that built it

The image needs a PostgreSQL database and the environment variables above to run, so use it through Compose rather than on its own.

## Troubleshooting

- **"Cannot connect to the Docker daemon" or a 500 error:** Docker Desktop isn't running, or WSL 2 / virtualization isn't enabled.
- **"port is already allocated":** something else is using port 8501. Stop it, or change the left number in `compose.yaml` (for example `"8502:8501"`).
- **Compose says a variable is missing:** `.env` is missing, in the wrong folder, or lacks that variable. Run `docker compose config` to see the resolved settings.
- **App can't connect to the database:** run `docker compose logs db` and check the credentials in `.env`. If you changed `POSTGRES_PASSWORD` after the first start, the old password is still stored in the volume; reset with `docker compose down -v`.
- **Old admin password still works:** see "Data persistence" above.

## Security notes

- Never commit `.env`. It is listed in `.gitignore`.
- Use a long random `COOKIE_KEY` and a strong `ADMIN_PASSWORD`.
- Don't publish the database port to the network unless you understand the risk.git add README.md
git status
git commit -m "Update README for Docker Compose and PostgreSQL setup"
git push -u origin update-readme-compose