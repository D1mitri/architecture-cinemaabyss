from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel

app = FastAPI(title="CinemaAbyss API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "cinemaabyss-movies-service": "http://localhost:8081"
}

@app.get("/{service_name}/{path:path}")
async def proxy_request(service_name: str, path: str):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SERVICES[service_name]}/{path}",
                timeout=10.0
            )
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Service unavailable")

@app.get("/health")
def health_check():
    return {"status": "ok"}

