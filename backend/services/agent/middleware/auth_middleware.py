from fastapi import Request, HTTPException, status
import jose.jwt as jwt
import os

# --- Security Rationale ---
# The Secret is shared between IAM and Agent service to ensure 
# that tokens issued by one are trusted by the other.
SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"

async def verify_jwt(request: Request):
    """
    Middleware function to enforce multi-tenant isolation at the gateway.
    Every request MUST be authenticated to determine the Organization context.
    """
    # Rationale: We look for the standard Authorization header or a 'token' query param.
    # Without this, we cannot identify WHICH tenant's data to search.
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif request.query_params.get("token"):
        token = request.query_params.get("token")
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header/token",
        )
    try:
        # Rationale: Decoding the JWT verifies that the user is who they say they are.
        # We extract 'sub' (user_id) and 'org_id' to bind the request to a specific tenant.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        org_id = payload.get("org_id")
        
        # Rationale: If the payload is missing these keys, the token is malformed 
        # and cannot be used for multi-tenant filtering.
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Missing user identity (sub)",
            )
        if org_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Missing organization context (org_id). Please ensure you have created an organization.",
            )
        
        # Rationale: Injecting these into request.state makes them available 
        # to all downstream controllers and routers without re-parsing the JWT.
        request.state.user_id = user_id
        request.state.org_id = org_id
        
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Invalid or expired token",
        )
    except Exception as e:
        # Rationale: Catch-all for any other unexpected failures.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
        )
