# list_my_bookings.py
# Handles GET /bookings/me — shows a logged-in user their own bookings,
# used on profile.html.

from db import get_connection, response

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    cognito_sub = claims.get("sub")
    if not cognito_sub:
        return response(401, {"error": "You must be logged in."})

    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            # One query joining bookings -> services so the frontend gets
            # readable service names, not just IDs.
            cur.execute(
                """
                SELECT b.id, b.scheduled_at, b.status, s.name AS service_name, s.duration_minutes
                FROM bookings b
                JOIN services s ON s.id = b.service_id
                JOIN users u ON u.id = b.user_id
                WHERE u.cognito_sub = %s
                ORDER BY b.scheduled_at DESC
                """,
                (cognito_sub,),
            )
            bookings = cur.fetchall()

        return response(200, {"bookings": bookings})

    except Exception as e:
        return response(500, {"error": "Could not load bookings.", "detail": str(e)})

    finally:
        conn.close()
