# create_booking.py
# Handles POST /bookings — a logged-in user books a service at a specific time.
#
# How it gets called: API Gateway invokes this function and passes the
# request as `event`. The frontend's booking form (static/js/booking.js)
# sends a POST request that ends up here.

import json
from db import get_connection, response

def lambda_handler(event, context):
    # API Gateway puts the JSON body the browser sent as a string — parse it.
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"error": "Request body must be valid JSON."})

    # Cognito has already verified this request before it reaches us (API Gateway
    # checks the JWT token). The verified user's ID is injected into the request
    # context, so we trust it rather than trusting anything the client claims.
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    cognito_sub = claims.get("sub")
    if not cognito_sub:
        return response(401, {"error": "You must be logged in to book."})

    service_id = body.get("service_id")
    scheduled_at = body.get("scheduled_at")  # expects an ISO 8601 timestamp string

    if not service_id or not scheduled_at:
        return response(400, {"error": "service_id and scheduled_at are required."})

    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            # Look up our internal user row from the Cognito identity.
            cur.execute("SELECT id FROM users WHERE cognito_sub = %s", (cognito_sub,))
            user_row = cur.fetchone()
            if not user_row:
                return response(404, {"error": "User account not found."})

            # This INSERT is the actual write — a single new row, no locking
            # of any other table, no rewriting of existing data. That's the
            # "fast writes" design we talked about: bookings are pure appends.
            cur.execute(
                """
                INSERT INTO bookings (user_id, service_id, scheduled_at, status)
                VALUES (%s, %s, %s, 'pending')
                RETURNING id, scheduled_at, status
                """,
                (user_row["id"], service_id, scheduled_at),
            )
            new_booking = cur.fetchone()

        return response(201, {"booking": new_booking})

    except Exception as e:
        # In production, log this to CloudWatch instead of returning raw error text.
        return response(500, {"error": "Could not create booking.", "detail": str(e)})

    finally:
        conn.close()
