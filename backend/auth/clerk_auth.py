import os
from functools import wraps
from fastapi import Request, HTTPException
import requests
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
import logging
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
)

# Create session with retry strategy
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)


def get_jwks():
    """Fetch the JWKS from Clerk"""
    clerk_issuer = os.getenv("CLERK_ISSUER")
    if not clerk_issuer:
        logger.error("CLERK_ISSUER environment variable not set")
        raise JWTError("Clerk configuration missing")

    try:
        logger.info(f"Fetching JWKS from {clerk_issuer}")
        response = session.get(
            f"{clerk_issuer}/.well-known/jwks.json",
            timeout=10,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch JWKS: {str(e)}")
        raise JWTError(f"Failed to fetch JWKS: {str(e)}")


def verify_token(token):
    """Verify the JWT token from Clerk"""
    try:
        # First decode without verification to check expiry
        unverified_payload = jwt.decode(
            token, None, options={"verify_signature": False}
        )
        exp_timestamp = unverified_payload.get("exp")
        if exp_timestamp:
            exp_time = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()
            if exp_time < now:
                logger.warning(f"Token expired at {exp_time}")
                raise ExpiredSignatureError("Token has expired")

        # Get the JWKS
        jwks = get_jwks()
        unverified_headers = jwt.get_unverified_headers(token)
        logger.debug(f"Token headers: {unverified_headers}")

        # Find the key that matches the token's key ID
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_headers["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if not rsa_key:
            logger.error("No matching key found in JWKS")
            raise JWTError("No matching key found")

        # Verify the token
        options = {"verify_aud": False}

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            issuer=os.getenv("CLERK_ISSUER"),
            options=options,
        )

        logger.info("Token verified successfully")
        return payload
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise


def requires_auth(func):
    @wraps(func)
    async def decorated(*args, **kwargs):
        request = kwargs.get("request")
        if not request or not isinstance(request, Request):
            raise HTTPException(
                status_code=401, detail={"error": "No valid request object"}
            )
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(
                status_code=401, detail={"error": "No authorization header"}
            )

        try:
            token = auth_header.split(" ")[1]
            try:
                payload = verify_token(token)
                request.state.user = payload
                return await func(*args, **kwargs)
            except ExpiredSignatureError:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "Token has expired",
                        "code": "token_expired",
                        "message": "Please refresh your token",
                    },
                )
            except JWTError as e:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": str(e),
                        "code": "invalid_token",
                        "message": "Invalid or malformed token",
                    },
                )

        except Exception as e:
            logger.error(f"Auth error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Invalid token format",
                    "code": "invalid_format",
                    "message": "Authorization header format should be 'Bearer <token>'",
                },
            )

    return decorated
