# Streamlit SQL App

A simple multi-page [Streamlit](https://streamlit.io/) app backed by PostgreSQL, with login handled by [Keycloak](https://www.keycloak.org/). Users log in through Keycloak, then use the sidebar pages to add, edit, and view user records. The whole stack (app, database, and Keycloak) runs with Docker Compose.

## Features

- Login via Keycloak (OpenID Connect), using Streamlit's native `st.login()` / `st.logout()` / `st.user`
- PostgreSQL database, with tables created automatically on first run
- Input, Display, and Edit pages for managing user records (first name, last name, date of birth, gender)
- One-command setup with Docker Compose
- GitHub Actions workflow that builds and publishes the Docker image to GitHub Container Registry

## Tech stack

- Python 3.14
- Streamlit, with built-in OIDC authentication (Authlib under the hood)
- Keycloak (identity provider / login)
- PostgreSQL 17 (via `psycopg`)
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker and Docker Compose

## Project structure

```
.
├── main.py                    # Home page and login
├── db.py                      # Database connection, setup, and queries
├── pages/                     # Additional Streamlit pages (Input, Display, Edit)
├── .streamlit/
│   └── secrets.toml.example   # Template for the OIDC config (copy to secrets.toml)
├── pyproject.toml             # Project dependencies
├── uv.lock                    # Locked dependency versions
├── Dockerfile                 # Builds the app image
├── compose.yaml                # Runs the app, PostgreSQL, and Keycloak together
├── .env.example                # Template for required settings
├── .dockerignore                # Files excluded from the Docker image
├── .gitignore                   # Files excluded from Git
└── .github/workflows/            # GitHub Actions workflow (build and push image)
```

## Configuration

There are **two** separate config files, and both hold secrets — neither is ever committed to Git.

### `.env`

Sits next to `compose.yaml`. Copy `.env.example` to `.env` and fill it in.

| Variable | Purpose |
|----------|---------|
| `POSTGRES_USER` | Database username |
| `POSTGRES_PASSWORD` | Database password (letters, numbers, and dashes are safest, since it is placed inside a URL) |
| `POSTGRES_DB` | Database name |
| `KEYCLOAK_ADMIN_USER` | Username for Keycloak's own admin console |
| `KEYCLOAK_ADMIN_PASSWORD` | Password for Keycloak's own admin console |

### `.streamlit/secrets.toml`

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill it in after setting up the Keycloak realm and client (see below).

| Key | Purpose |
|-----|---------|
| `redirect_uri` | Your app's login callback URL. For local dev: `http://localhost:8501/oauth2callback` |
| `cookie_secret` | Random secret used to sign the login cookie. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `client_id` | The client ID you create in Keycloak (e.g. `streamlit-app`) |
| `client_secret` | The client secret from that client's **Credentials** tab in Keycloak |
| `server_metadata_url` | Keycloak's OIDC discovery URL: `http://keycloak.local:8080/realms/<realm>/.well-known/openid-configuration` |

## Run with Docker Compose

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A `keycloak.local` entry in your hosts file pointing at `127.0.0.1` (see [Local hostname setup](#local-hostname-setup) below) — required so your browser and the app container can both reach Keycloak the same way

### Steps

```bash
git clone https://github.com/zai20220667-ops/StreamlitApp.git
cd StreamlitApp
```

Create your settings files from the templates and edit them:

```bash
# Windows (PowerShell / cmd)
copy .env.example .env
copy .streamlit\secrets.toml.example .streamlit\secrets.toml

# macOS / Linux
cp .env.example .env
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Open `.env` and fill in every value. Then start the database and Keycloak first:

```bash
docker compose up -d db keycloak
```

Set up Keycloak (one-time):

1. Open `http://keycloak.local:8080`, click **Administration Console**, and log in with `KEYCLOAK_ADMIN_USER` / `KEYCLOAK_ADMIN_PASSWORD` from `.env`.
2. Realm dropdown (top-left) → **Create realm** → name it, e.g. `streamlit-app`.
3. **Clients** → **Create client** → Client ID `streamlit-app` → **Client authentication: On** → Next.
4. Valid redirect URIs: `http://localhost:8501/oauth2callback`
   Valid post logout redirect URIs: `http://localhost:8501/*`
5. Save, open the **Credentials** tab, copy the **Client secret**.
6. **Users** → **Add user** → set a username, then in that user's **Credentials** tab, set a password (toggle **Temporary** off).

Now fill in `.streamlit/secrets.toml` with the client ID, client secret, and realm name from above, and start the app:

```bash
docker compose up -d --build
```

Open **http://localhost:8501**, click **Log in**, and sign in with the Keycloak user you created.

### Local hostname setup

Your browser needs to reach Keycloak directly, but the app container also needs to reach it server-to-server — and Docker's internal service name (`keycloak`) only works from inside the Docker network. To give both sides one consistent hostname, add this line to your hosts file:

- Windows: `C:\Windows\System32\drivers\etc\hosts` (edit as Administrator)
- macOS/Linux: `/etc/hosts` (edit with `sudo`)

```
127.0.0.1 keycloak.local
```

`compose.yaml` already maps `keycloak.local` to the host machine from inside the `app` container via `extra_hosts`, so once this line is in place, `http://keycloak.local:8080` resolves correctly from both your browser and the app.

### How it works

`compose.yaml` defines three services:

- **db**: a PostgreSQL container. Its data is stored in a Docker volume named `pgdata`.
- **keycloak**: the identity provider. Runs in dev mode with its data in the `keycloak_data` volume. Handles login, logout, and issuing tokens.
- **app**: the Streamlit app, built from the `Dockerfile`. It waits for the database to report healthy and for Keycloak to start, then connects to Postgres at the hostname `db` and to Keycloak at `keycloak.local`.

### Access from other devices

The app is published on port 8501 of your computer, so other devices on the same network can open it at your machine's IP address:

1. Find your IP: run `ipconfig` (Windows) or `ip addr` (Linux) and look for the IPv4 address, for example `192.168.1.25`.
2. Open `http://192.168.1.25:8501` from another device on the same network.
3. If it doesn't load, allow the port through your firewall. On Windows, in PowerShell as Administrator:
   ```powershell
   New-NetFirewallRule -DisplayName "Streamlit 8501" -Direction Inbound -Protocol TCP -LocalPort 8501 -Action Allow
   ```

Note that for other devices to log in, Keycloak's redirect URIs and `keycloak.local` DNS mapping would need to point at a reachable hostname rather than `localhost`/`127.0.0.1` — the default setup here is for local single-machine development.

The database port is bound to `127.0.0.1` only, so it is reachable from your own computer (for tools like DBeaver) but not from the network.

### Useful commands

```bash
docker compose ps                # list services and their status
docker compose logs -f app       # follow the app logs
docker compose logs db           # view the database logs
docker compose logs keycloak     # view the Keycloak logs
docker compose down              # stop and remove containers (data is kept)
docker compose down -v           # also DELETE the database and Keycloak volumes (all data)
docker compose up -d --build     # rebuild and restart after code changes
```

Open a SQL shell in the database:

```bash
docker compose exec db psql -U appuser -d appdb
```

(Use your own `POSTGRES_USER` and `POSTGRES_DB` values.)

### Data persistence

Database data lives in the `pgdata` volume and Keycloak's realm/client/user data lives in the `keycloak_data` volume, so both survive restarts, rebuilds, and `docker compose down`. They are only removed by `docker compose down -v`.

## Run without Docker

Requires Python 3.14+, [uv](https://docs.astral.sh/uv/), a running PostgreSQL, and a running Keycloak. The easiest way to get both is to start them from Compose:

```bash
docker compose up -d db keycloak
```

Then set the environment variable and run the app. In PowerShell:

```powershell
$env:DATABASE_URL="postgresql://appuser:your-password@localhost:5432/appdb"
uv sync
uv run streamlit run main.py
```

`.streamlit/secrets.toml` is read automatically by Streamlit; no extra environment variables are needed for auth outside of that file.

## Continuous integration

`.github/workflows/docker-publish.yml` runs on every push to `main`. It builds the Docker image and pushes it to `ghcr.io` with two tags:

- `latest`
- `sha-<commit>`, which ties each image to the exact commit that built it

The image needs a PostgreSQL database, a Keycloak instance, and `.streamlit/secrets.toml` to run, so use it through Compose rather than on its own.

## Troubleshooting

- **"Cannot connect to the Docker daemon" or a 500 error:** Docker Desktop isn't running, or WSL 2 / virtualization isn't enabled.
- **"port is already allocated" (5432, 8080, or 8501):** something else is using that port. Find it with `netstat -ano | findstr :<port>` (Windows) or `lsof -i :<port>` (macOS/Linux), stop it, or remap the left-hand port number in `compose.yaml`. If you move Keycloak off `8080`, also update `KC_HOSTNAME_PORT` in `compose.yaml` and `server_metadata_url` in `secrets.toml` to match.
- **Compose says a variable is missing:** `.env` is missing, in the wrong folder, or lacks that variable. Run `docker compose config` to see the resolved settings.
- **App can't connect to the database:** run `docker compose logs db` and check the credentials in `.env`. If you changed `POSTGRES_PASSWORD` after the first start, the old password is still stored in the volume; reset with `docker compose down -v`.
- **`ModuleNotFoundError` on login (e.g. `httpx`):** Streamlit's OIDC login needs a couple of Authlib's optional dependencies. Make sure `httpx` is listed in `pyproject.toml`, run `uv lock`, and rebuild.
- **App can't reach Keycloak / login hangs or errors:** confirm `docker compose exec app curl -s http://keycloak.local:8080/realms/<realm>/.well-known/openid-configuration` returns JSON from inside the container. If not, check that `keycloak.local` is in your hosts file and that the `extra_hosts` entry is present in `compose.yaml`.
- **"We are sorry... Invalid redirect uri" on logout:** the client's **Valid post logout redirect URIs** field in Keycloak doesn't match. Set it to `http://localhost:8501/*` (the bare `+` shorthand isn't accepted by the admin console UI, only via the REST API).
- **"A post-logout redirect URI is not a valid URI":** the field must contain a well-formed URL — make sure it's `http://localhost:8501/*` on its own, not blank or missing the scheme.

## Security notes

- Never commit `.env` or `.streamlit/secrets.toml`. Both are listed in `.gitignore`.
- Use a long random `cookie_secret` and a strong Keycloak admin password.
- Don't publish the database port to the network unless you understand the risk.
- This setup runs Keycloak in dev mode (`start-dev`) with HTTP, which is fine for local development only. For a real deployment, run Keycloak with `start` behind HTTPS, a dedicated production database, and a real hostname.