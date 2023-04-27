from fastapi.responses import JSONResponse
from starlette import status

ERROR_RESPONSE = JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={
        "ok": False,
        "error": "Unhandled error",
        "error_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
    },
)
