# Hospital Management Test System (Flask & FastAPI, Using SQLAlchemy(SQLite/PostgreSQL/MySQL))

A simple hospital management app built with both **Flask** and **FastAPI**, using **SQLAlchemy** (SQLite/PostgreSQL/MySQL).

- Full CRUD support, with automatic table creation and initial data seeding.
- Install dependencies with `python -m pip install -r requirements.txt`.
- Run `python app.py` and visit http://localhost:5005 for Flask.
- Run `python -m uvicorn main:app --reload` and visit http://localhost:8000/docs for FastAPI.
- SQLite works by default. Both apps use the same database.
- To use MySQL or PostgreSQL, start the server and create the `mft` database. In PowerShell, set `$env:DB_BACKEND = 'mysql'` or `$env:DB_BACKEND = 'postgresql'` before running either app.
- Server settings follow the course examples in `models.py`. Set `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` or `DB_PASSWORD` if your local settings differ.
