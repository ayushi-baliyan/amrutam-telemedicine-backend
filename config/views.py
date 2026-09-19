from django.db import connection
from django.http import JsonResponse


def health_check(request):
    database = "ok"

    try:
        connection.ensure_connection()
    except Exception:
        database = "error"

    status_code = 200 if database == "ok" else 503

    return JsonResponse(
        {
            "status": "ok" if database == "ok" else "error",
            "database": database,
        },
        status=status_code,
    )