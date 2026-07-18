# db.py
# Shared helper for connecting to RDS PostgreSQL from any Lambda function.
# Every handler imports this instead of writing its own connection code.

import os
import json
import psycopg2
import psycopg2.extras

def get_connection():
    """
    Opens a connection to the RDS database using credentials stored in
    Lambda environment variables (set in the AWS console, not in this code).
    Never hardcode passwords in source files — that's how credentials leak.
    """
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        cursor_factory=psycopg2.extras.RealDictCursor,  # rows come back as dicts, easy to JSON-ify
    )

def response(status_code, body_dict):
    """
    Every Lambda function behind API Gateway must return this exact shape:
    statusCode, headers, and a JSON-stringified body. This helper keeps
    that formatting in one place instead of repeating it in every handler.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # tighten this to your domain once live
        },
        "body": json.dumps(body_dict, default=str),  # default=str handles datetime objects
    }
