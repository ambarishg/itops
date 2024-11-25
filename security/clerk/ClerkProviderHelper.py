from fastapi import HTTPException,Request
import httpx
import jwt

class ClerkProviderHelper():
    def __init__(self,JWKS_URL):
        self.JWKS_URL = JWKS_URL

    async def fetch_jwks(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(self.JWKS_URL)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        
    async def verify_jwt(self,token: str):
        # Decode the token to get the header and extract the kid
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        # Fetch JWKS
        jwks = await self.fetch_jwks()

        # Find the key with the matching kid
        key = next((key for key in jwks['keys'] if key['kid'] == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid key ID")

        # Convert JWK to PEM format
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)

        # Verify the token using the public key
        try:
            decoded_token = jwt.decode(token, public_key, algorithms=['RS256'])
            return decoded_token
        except jwt.PyJWTError as e:
            raise HTTPException(status_code=401, detail=str(e))
        
    async def get_user_name(self,request:Request):
        payload = await request.json()
        auth = payload["headers"]["Authorization"]
        token = auth.replace("Bearer ", "")
        print(f"TOKEN is ========={token}")

        decoded_token = await self.verify_jwt(token)
        print(f"User Name is {decoded_token}")
        return(decoded_token["sub"])