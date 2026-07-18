# Tanish.Book

Hotel booking site — Flask + PostgreSQL, deployed on Render's cloud servers.

## Structure

```
tanish_book/
├── app.py              # Flask app + API routes
├── requirements.txt    # Python dependencies
├── render.yaml          # Render Blueprint (web service + Postgres)
├── Procfile             # Start command
├── .env.example          # Local dev DB connection template
├── templates/index.html # Page markup
└── static/
    ├── style.css
    └── script.js
```

## Deploy to Render (cloud, free tier)

1. Push this folder to a GitHub repo.
2. Go to Render → **New → Blueprint** → connect the repo. Render reads
   `render.yaml` and sets up two things automatically:
   - A **PostgreSQL** database (`tanish-book-db`)
   - A **web service** running `gunicorn app:app`, already wired to the
     database's connection string via `DATABASE_URL`
3. Click **Apply**. Render builds and deploys both.
4. Your site is live at `https://tanish-book.onrender.com` (or whatever
   name Render assigns).

No servers to manage, no manual `DATABASE_URL` copy-pasting — the Blueprint
connects the two services for you.

## Viewing the database

**Option 1 — Render dashboard**
Go to your `tanish-book-db` instance on Render → **Connect** tab. It gives
you:
- A **PSQL Command** you can paste into any terminal to open a live
  `psql` session against the cloud database.
- An **External Connection String** for GUI tools (below).

**Option 2 — psql**
```bash
psql "<external connection string from Render>"
```
Then:
```sql
\dt                          -- list tables
SELECT * FROM bookings;
SELECT * FROM contact_messages;
SELECT * FROM profile;
```

**Option 3 — GUI tool**
Use the External Connection String from Render in any of:
- [TablePlus](https://tableplus.com)
- [DBeaver](https://dbeaver.io) (free)
- [pgAdmin](https://www.pgadmin.org)

Paste the connection string in, and you can browse tables, run queries,
and edit rows visually.

## Running it locally

```bash
cp .env.example .env      # fill in a local Postgres URL
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

## API

| Method | Endpoint                     | Description               |
|--------|-------------------------------|-----------------------------|
| GET    | `/api/hotels?destination=goa` | List hotels, filter by city |
| GET    | `/api/bookings`               | List all bookings           |
| POST   | `/api/bookings`               | Create a booking            |
| POST   | `/api/bookings/<id>/cancel`   | Cancel a booking            |
| GET    | `/api/profile`                | Get saved profile           |
| POST   | `/api/profile`                | Save profile                |
| POST   | `/api/contact`                | Submit a contact message    |
