# submit_contact.py
# Handles POST /contact — anyone (logged in or not) can send a message
# through the contact form on contact.html.

import json
from db import get_connection, response

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"error": "Request body must be valid JSON."})

    subject = (body.get("subject") or "").strip()
    message = (body.get("message") or "").strip()

    if not subject or not message:
        return response(400, {"error": "Subject and message are required."})

    # Contact form doesn't require login, so this might be empty — that's fine,
    # contact_messages.user_id is nullable for exactly this reason.
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    cognito_sub = claims.get("sub")

    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            user_id = None
            if cognito_sub:
                cur.execute("SELECT id FROM users WHERE cognito_sub = %s", (cognito_sub,))
                row = cur.fetchone()
                user_id = row["id"] if row else None

            cur.execute(
                """
                INSERT INTO contact_messages (user_id, subject, message)
                VALUES (%s, %s, %s)
                RETURNING id, created_at
                """,
                (user_id, subject, message),
            )
            new_message = cur.fetchone()

        # A real version would also call SES here to email you a notification.
        # Left out for clarity — see README "Next steps" for where to add it.
        return response(201, {"message": new_message})

    except Exception as e:
        return response(500, {"error": "Could not submit message.", "detail": str(e)})

    finally:
        conn.close()
