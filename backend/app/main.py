from fastapi import FastAPI

app = FastAPI(
    title="OpenOps API",
    description="Independent endpoint monitoring and management platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "application": "OpenOps",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "openops-api",
    }
