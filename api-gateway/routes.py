from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from jose import jwt, JWTError
from config import get_settings
from services import get_http_client

settings = get_settings()
http_client = get_http_client()

async def proxy_request(request: Request, path: str):

    public_endpoints = ["auth/login", "auth/register", "auth/refresh-token"]
    if any(path.startswith(endpoint) for endpoint in public_endpoints):
        user_id = None
    else:    
        user_id = await validate_jwt(request)

    backend_url = get_backend_url(path)

    response = await forward_request(
        request = request,
        backend_url = backend_url,
        path = path,
        user_id = user_id
    )

    return response

async def validate_jwt(req: Request) -> str:
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    token = auth_header.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
def get_backend_url(path: str) -> str:
    if path.startswith("auth"):
        return f"{settings.AUTH_SERVICE_URL}/{path}"
    elif path.startswith("tasks"):
        return f"{settings.TASK_SERVICE_URL}/{path}"
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
async def forward_request(request: Request, backend_url: str, path: str, user_id: str) -> Response:
    method = request.method
    headers = dict(request.headers)
    if user_id:
        headers["X-User-ID"] = user_id
    headers.pop("Authorization", None)
    headers.pop("Host", None)
    

    body = await request.body()

    backend_response = await http_client.client.request(
            method=method,
            url=backend_url,
            headers=headers,
            content=body,
            timeout=settings.HTTP_TIMEOUT
        )

    response = Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=dict(backend_response.headers)
    )

    return response