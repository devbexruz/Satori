from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError
from app.config import settings

# Setup standard HTTPBearer security schema for Swagger / API documentation
security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme)
) -> dict:
    """
    Dependency that extracts and validates a JWT token from incoming requests.
    Supports standard Bearer headers, cookies, or X-Access-Token headers.
    Returns a dict containing user identity claims and the raw token for microservice forwarding.
    """
    token = None
    
    # 1. Try extracting from standard HTTP Authorization Bearer header
    if credentials:
        token = credentials.credentials
        
    # 2. Try extracting from Cookie: X-Access-Token
    if not token:
        token = request.cookies.get("X-Access-Token")
        
    # 3. Try extracting from custom Header: X-Access-Token
    if not token:
        token = request.headers.get("X-Access-Token")
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are required. Access token missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        # Decode and validate using settings matching SatoriBackend
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER
        )
        
        # Standard OIDC/JWT 'sub' claim, or ASP.NET Core ClaimTypes.NameIdentifier URL format
        user_id = payload.get("sub") or payload.get("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier")
        
        # Standard OIDC/JWT 'name' / 'unique_name' claim, or ASP.NET Core ClaimTypes.Name URL format
        username = payload.get("unique_name") or payload.get("name") or payload.get("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials: User identity identifier claim is missing.",
            )
            
        return {
            "id": user_id,
            "username": username,
            "token": token  # Retain the raw token to forward to other microservices (e.g. SatoriDocs)
        }
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
