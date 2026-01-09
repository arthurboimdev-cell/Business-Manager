from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes import router

app = FastAPI(title="AurumCandles API")

# Configure CORS (Open access for local development/mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AurumCandles API is running"}
