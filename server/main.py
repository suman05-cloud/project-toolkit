from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import convert, pdf_ops, images

import os
import asyncio
import tempfile

app = FastAPI(title="Document Toolkit API", description="API for document conversions and manipulations.")

# CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # React default
    "*" # For development convenience
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Include Routers
app.include_router(convert.router)
app.include_router(pdf_ops.router)
app.include_router(images.router)

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to Document Toolkit API. Docs at /docs"}

# Periodic cleanup (fallback)
async def cleanup_tmp_folder():
    base_tmp = tempfile.gettempdir()
    folders = [os.path.join(base_tmp, "uploads"), os.path.join(base_tmp, "outputs")]
    for folder in folders:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    # Remove files older than 1 hour as fallback
                    if os.path.isfile(file_path):
                        # check time... implementation skipped for brevity, just defining the idea
                        pass
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")

@app.on_event("startup")
async def startup_event():
    # Setup directories
    base_tmp = tempfile.gettempdir()
    os.makedirs(os.path.join(base_tmp, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(base_tmp, "outputs"), exist_ok=True)
