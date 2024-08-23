from dotenv import load_dotenv

import os

load_dotenv()

HOST = os.getenv("HOST") or "localhost"
PORT = os.getenv("PORT") or "2005"

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

JWT_SECRET = os.environ.get("JWT_SECRET")
