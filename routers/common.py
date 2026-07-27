"""
routers/common.py

Shared plumbing used by every router:

`run_service` calls a service-layer function and translates its typed
exceptions (ValidationError, AuthError, NotFoundError, ServiceError)
into the correct HTTPException status code. This is the ONLY place
that maps business exceptions to HTTP - individual routes never do
their own try/except, which keeps every route function a thin,
readable one-liner.
"""

from fastapi import HTTPException

from services.utils import ValidationError, NotFoundError, AuthError, ServiceError


def run_service(fn, *args, **kwargs):
    """
    Call a service function and re-raise its exceptions as the
    appropriate HTTPException. Returns the service's dict envelope
    ({"success", "message", "data"}) unchanged on success.
    """
    try:
        return fn(*args, **kwargs)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:  # pragma: no cover - truly unexpected failure
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc}")