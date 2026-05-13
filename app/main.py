"""
This Module is the main entry point of the fastapi app
    - generates fastapi app object
    - includes various routes
    - runs uvicorn server
"""

from fastapi import FastAPI
from app.api.auth import router as auth_route
import uvicorn

app = FastAPI()


# home route
@app.get("/")
async def home():
    return {"message": "async feed generator is running"}


app.include_router(auth_route)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
