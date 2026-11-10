from fastapi import FastAPI

app = FastAPI(
    title="PolyGen API",
    description="Generative Text-to-3D Asset Pipeline API",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {
        "name": "PolyGen API",
        "description": "Generative Text-to-3D Asset Pipeline",
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "app": "PolyGen API",
        "status": "healthy",
        "version": "0.1.0",
    }

