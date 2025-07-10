# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from contextlib import asynccontextmanager
# import time
# import uvicorn
# import os  # Added for PORT environment variable
# from backend.src.utils.logger import logger
# from backend.src.utils.exception import LegalRAGException
# from backend.src.config_settings.config_manager import ConfigurationManager
# from backend.src.pipeline.rag_pipeline import LegalRAGPipeline
#
# # Configuration settings
# origins = [
#     "http://localhost:5173",  # Add this for Vite
#     "https://legal-case-research-app.vercel.app",
#     "https://917cdcae8d56.ngrok-free.app",
#     "https://*.ngrok-free.app"
# ]
#
# # Lifespan handler for startup/shutdown
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Initializes and shuts down the LegalRAGPipeline."""
#     try:
#         logger.info("Initializing LegalRAGPipeline on startup")
#         app.state.pipeline = LegalRAGPipeline(ConfigurationManager())
#         logger.info("LegalRAGPipeline initialized successfully")
#     except Exception as e:
#         logger.error(f"Failed to initialize pipeline: {e}")
#         raise
#     yield
#     logger.info("Application shutdown complete.")
#
# app = FastAPI(
#     title="Legal RAG API",
#     description="API for legal case law queries",
#     version="1.0.0",
#     lifespan=lifespan
# )
#
# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Request model
# class QueryRequest(BaseModel):
#     query: str
#     model_id: str | None = None
#
# # Health check endpoint
# @app.get("/health")
# async def health_check():
#     """Returns a simple health check."""
#     return {"status": "healthy"}
#
# # Root endpoint to handle GET /
# @app.get("/")
# async def root():
#     """Provides API info or redirects to health check."""
#     try:
#         return {"message": "Welcome to Legal RAG API. Use /health or /query endpoints."}
#     except Exception as e:
#         logger.error(f"Error in root endpoint: {e}")
#         raise HTTPException(status_code=500, detail="error")
#
# # Favicon endpoint to handle GET /favicon.ico
# @app.get("/favicon.ico")
# async def favicon():
#     """Returns empty response to prevent 404 for favicon requests."""
#     return {}
#
# # Query endpoint
# @app.post("/query")
# async def process_query(request: QueryRequest):
#     """Processes a legal query using the RAG pipeline."""
#     try:
#         start_time = time.time()
#         logger.info(f"Processing query: {request.query}, model_id: {request.model_id or 'default'}")
#         response = await app.state.pipeline.process_query(request.query, request.model_id)
#         elapsed_time = time.time() - start_time
#         logger.info(f"Query processed in {elapsed_time:.2f} seconds: {response['answer'][:100]}...")
#         return {
#             "status": "success",
#             "data": response,
#             "processing_time": elapsed_time
#         }
#     except LegalRAGException as e:
#         logger.error(f"LegalRAGException processing query: {e}")
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         logger.error(f"Unexpected error processing query: {e}")
#         raise HTTPException(status_code=500, detail="error")
#
# if __name__ == "__main__":
#     """Run the FastAPI server locally for development."""
#     uvicorn.run(
#         "backend.main:app",
#         host="0.0.0.0",
#         port=8000,  # Default local port
#         reload=True  # Enable auto-reload only for local development
#     )

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import time
import uvicorn
from backend.src.utils.logger import logger
from backend.src.utils.exception import LegalRAGException
from backend.src.config_settings.config_manager import ConfigurationManager
from backend.src.pipeline.rag_pipeline import LegalRAGPipeline

# Configuration settings
origins = [
    "https://48e5a33010f5.ngrok-free.app",
    "https://legal-case-research-app.vercel.app",
    "*"



]  # Update to ["https://your-vercel-app.vercel.app"] in production

# Lifespan handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes and shuts down the LegalRAGPipeline."""
    try:
        logger.info("Initializing LegalRAGPipeline on startup")
        app.state.pipeline = LegalRAGPipeline(ConfigurationManager())
        logger.info("LegalRAGPipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise
    yield
    logger.info("Application shutdown complete.")

app = FastAPI(
    title="Legal RAG API",
    description="API for legal case law queries",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QueryRequest(BaseModel):
    query: str
    model_id: str | None = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Returns a simple health check."""
    return {"status": "healthy"}

# Root endpoint to handle GET /
@app.get("/")
async def root():
    """Provides API info or redirects to health check."""
    try:
        return {"message": "Welcome to Legal RAG API. Use /health or /query endpoints."}
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        raise HTTPException(status_code=500, detail="error")

# Favicon endpoint to handle GET /favicon.ico
@app.get("/favicon.ico")
async def favicon():
    """Returns empty response to prevent 404 for favicon requests."""
    return {}

# Query endpoint
@app.post("/query")
async def process_query(request: QueryRequest):
    """Processes a legal query using the RAG pipeline."""
    try:
        start_time = time.time()
        logger.info(f"Processing query: {request.query}, model_id: {request.model_id or 'default'}")
        response = await app.state.pipeline.process_query(request.query, request.model_id)
        elapsed_time = time.time() - start_time
        logger.info(f"Query processed in {elapsed_time:.2f} seconds: {response['answer'][:100]}...")
        return {
            "status": "success",
            "data": response,
            "processing_time": elapsed_time
        }
    except LegalRAGException as e:
        logger.error(f"LegalRAGException processing query: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing query: {e}")
        raise HTTPException(status_code=500, detail="error")

if __name__ == "__main__":
    """Run the FastAPI server locally for development."""
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        reload=True,
        workers=1
    )