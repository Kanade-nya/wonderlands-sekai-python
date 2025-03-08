from http.client import HTTPException

from utils import verify_token

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdmF0YXIiLCJleHAiOjE3NDQwMDc0MDN9.x0ekdgkq16L-D8pi2ZN9tkOa7ODrYd1XzlksQecVcbg"
try:
    username = verify_token(token)
    print(f"Verified username: {username}")
except HTTPException as e:
    print(f"Token verification failed: {e.detail}")