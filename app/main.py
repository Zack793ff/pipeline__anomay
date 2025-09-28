from fastapi import FastAPI
from .routes import router
import uvicorn

# Initialize FastAPI application
app = FastAPI(
    title="ESP32 Well Data API",
    description="API to receive sensor/production data from ESP32 and store it in MongoDB",
    version="1.0.0"
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# # Allow running with: python app/main.py
# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
