"""
Simplified FastAPI application for testing.
"""
from fastapi import FastAPI

# Create application instance
app = FastAPI(
    title="FastAPI Enterprise MVP",
    version="1.0.0",
    description="Enterprise-grade FastAPI application with DevContainer support",
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to FastAPI Enterprise MVP",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "fastapi-enterprise-mvp"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
