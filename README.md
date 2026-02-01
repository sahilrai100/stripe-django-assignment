# stripe-django-assignment


A lightweight Django demo app that demonstrates a minimal Stripe Checkout flow. This project is intended for learning, testing, and evaluation; it provides a simple storefront with three fixed products, Stripe Checkout integration, server-side verification, and a small admin-like UI to view recorded paid orders.

---

## 🔦 Features

- Simple storefront with 3 fixed products (T‑shirt, Mug, Sticker Pack)
- Quantity selection and Stripe Checkout session creation from the server
- Server-side verification of completed checkout sessions and idempotent order creation
- Webhook endpoint to reliably record orders when Stripe notifies your server
- Management commands to seed demo orders and simulate a checkout session for testing
- Docker Compose configuration for a full stack with Postgres for production-like testing

---

## 📦 Project Structure (high level)

- `shop/` — Django project settings, WSGI, and URL configuration
- `store/` — main app: models, views, templates, management commands, static files
- `manage.py` — Django entrypoint
- `requirements.txt` — Python dependencies
- `.env.example` — example env variables (copy to `.env` in local dev)
- `Dockerfile`, `docker-compose.yml` — containerized setup (web + db)

---
## 🚀 Quick Start (Development)

Choose one of the following workflows.

### A) Local development (recommended fast path)

1. Open PowerShell / terminal and change to the project root (where `manage.py` is).
2. Create & activate a virtual environment:

```powershell
python -m venv .venv
# PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example` (do not commit `.env`):

```powershell
copy .env.example .env
notepad .env
# or: code .env
```

5. Edit `.env` and set your Stripe keys and other values (see Environment variables below).
6. Use SQLite for local dev (default if `DATABASE_URL` is unset). Run migrations and seed demo orders:

```powershell
python manage.py migrate
python manage.py seed_orders
```

7. Start the dev server:

```powershell
python manage.py runserver 127.0.0.1:8000
```

8. Open the app: http://127.0.0.1:8000


### B) Docker (production-like stack with Postgres)

1. Ensure Docker Desktop is installed and running.
2. Copy `.env.example` → `.env` and configure values (especially `DATABASE_URL`, or keep defaults in the example).
3. Build & start containers:

```bash
docker compose up --build
```

4. Run migrations & (optionally) create superuser:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

5. The app will be available at http://localhost:8000

---

## 🔐 Environment variables

List of the important `.env` variables (copy from `.env.example`):

- `SECRET_KEY` — Django secret, set to a strong random string
- `DEBUG` — `True` for local dev, `False` for production
- `ALLOWED_HOSTS` — comma-separated list (include `127.0.0.1` and/or `localhost` for local dev)
- `DATABASE_URL` — (optional) Postgres connection string. Leave blank to use SQLite for local dev
- `STRIPE_SECRET_KEY` — your **Stripe secret API key** (starts with `sk_...`)
- `STRIPE_PUBLISHABLE_KEY` — your **Stripe publishable key** (starts with `pk_...`)
- `STRIPE_WEBHOOK_SECRET` — webhook signing secret (starts with `whsec_...`)
- `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD` / `DJANGO_SUPERUSER_EMAIL` — optional; `entrypoint.sh` can create a superuser on container start

> Note: Never commit real secret keys or `.env` to source control. Add `.env` to `.gitignore`.

---

## 💳 Stripe setup & webhooks

1. Sign in to the Stripe Dashboard and use **Test mode** for development.
2. Get your keys under **Developers → API keys** and paste into your `.env`.
3. For webhooks, the recommended workflow is to use the Stripe CLI on your machine:

```bash
# install stripe CLI (see https://stripe.com/docs/stripe-cli)
stripe login
stripe listen --forward-to http://127.0.0.1:8000/webhook
# copy the printed `whsec_...` signing secret to STRIPE_WEBHOOK_SECRET in .env
```

4. You can also create a webhook endpoint in the Dashboard and copy the signing secret.

5. To simulate Stripe events locally with the CLI:

```bash
stripe trigger checkout.session.completed
```

The app validates webhook signatures using `STRIPE_WEBHOOK_SECRET` to avoid processing forged events.

---

## ✅ Useful management commands

- `python manage.py migrate` — apply migrations
- `python manage.py seed_orders` — create a few demo orders for UI testing
- `python manage.py simulate_checkout --session-id SID --amount 2200 --items '{"items": [...]}'` — simulate a paid checkout session for testing
- `python manage.py test` — run test suite

---

## 🐞 Troubleshooting (common issues)

- DisallowedHost: `Invalid HTTP_HOST header: '127.0.0.1:8000'. You may need to add '127.0.0.1' to ALLOWED_HOSTS.`
  - Fix: add `127.0.0.1` to `ALLOWED_HOSTS` in `.env` or `shop/settings.py` (for dev). For example: `ALLOWED_HOSTS=localhost,127.0.0.1`

- `ModuleNotFoundError: No module named 'django'`
  - Fix: activate your virtualenv and install dependencies with `pip install -r requirements.txt`.

- `psycopg2.OperationalError: could not translate host name "db" to address` when starting locally
  - Cause: `DATABASE_URL` is pointing to `db` (the Docker service name) but you're not running Docker.
  - Fixes:
    - For quick local dev, comment out `DATABASE_URL` in `.env` so Django will use SQLite.
    - Or run Postgres via `docker compose up -d` so `db` resolves.

- Stripe-related 500 on `/create-checkout-session/` or missing keys
  - Fix: ensure `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` are set in `.env`. Restart server after changes.

If an error happens, copy the terminal traceback and open an issue here or paste it in for help.

---

## 🔁 Testing & CI

- Tests are executed by `python manage.py test` and are also wired into the repository's CI (see `.github/workflows`).
- Use the Stripe test card numbers (e.g., `4242 4242 4242 4242`) when running in test mode.

---

## 🛡️ Security & best practices

- Never commit secrets. Use environment variables or a secrets manager in production.
- Use HTTPS and secure webhook endpoints in production.
- Rotate Stripe keys if they are exposed.

---

## 🤝 Contributing

- Fork the repo and open a PR with small, focused changes.
- Keep tests green and add tests for new behavior.
- Use the existing code style and include descriptive commit messages.

---

## 📄 License

This project is provided for educational/testing purposes. Add a license file if you intend to reuse it in production.

---

## Appendix: Quick Commands Reference

```bash
# Local dev
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # PowerShell
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_orders
python manage.py runserver 127.0.0.1:8000

# Docker
docker compose up --build
docker compose exec web python manage.py migrate

# Stripe CLI (for webhook testing)
stripe login
stripe listen --forward-to http://127.0.0.1:8000/webhook
stripe trigger checkout.session.completed
```

---

If you'd like, I can:
- add usage examples to the `store/` templates, or
- add a step-by-step demo script to exercise the checkout flow for QA, or
- include a `CONTRIBUTING.md` and expand the test suite further.

If you want any of those, reply with what I should add next. ✨

>>>>>>> ca83056 (upload project on github)
