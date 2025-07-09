# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# from backend.src.utils.logger import logger
# from backend.src.utils.exception import LegalRAGException
# from backend.src.config_settings.config_manager import ConfigurationManager
# from backend.src.pipeline.rag_pipeline import LegalRAGPipeline
# import time
# import uvicorn
#
# app = FastAPI(title="Legal RAG API", description="API for legal case law queries", version="1.0.0")
#
# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change to specific origins (e.g., ["https://your-vercel-app.vercel.app"]) in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Rate limiter
# limiter = Limiter(key_func=get_remote_address)
# app.state.limiter = limiter
#
# # Initialize pipeline at startup
# @app.on_event("startup")
# async def startup_event():
#     try:
#         logger.info("Initializing LegalRAGPipeline on startup")
#         app.state.pipeline = LegalRAGPipeline(ConfigurationManager())
#         logger.info("LegalRAGPipeline initialized successfully")
#     except Exception as e:
#         logger.error(f"Failed to initialize pipeline: {e}")
#         raise
#
# # Request model
# class QueryRequest(BaseModel):
#     query: str
#     model_id: str | None = None
#
# # Health check endpoint
# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}
#
# # Query endpoint
# @app.post("/query")
# @limiter.limit("10/second")  # Adjust limit as needed (e.g., 10 requests/second per IP)
# async def process_query(request: QueryRequest, _=Depends(limiter)):
#     try:
#         start_time = time.time()
#         logger.info(f"Received query: {request.query}, model_id: {request.model_id or 'default'}")
#         response = await app.state.pipeline.process_query(request.query, request.model_id)
#         elapsed_time = time.time() - start_time
#         logger.info(f"Processed query in {elapsed_time:.2f} seconds: {response['answer'][:100]}...")
#         return {
#             "status": "success",
#             "data": response,
#             "processing_time": elapsed_time
#         }
#     except LegalRAGException as e:
#         logger.error(f"LegalRAGException processing query: {e}")
#         raise HTTPException(status_code=400, detail=str(e))
#     except RateLimitExceeded:
#         logger.warning(f"Rate limit exceeded for query: {request.query}")
#         raise HTTPException(status_code=429, detail="Too many requests")
#     except Exception as e:
#         logger.error(f"Unexpected error processing query: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")
#
# if __name__ == "__main__":
#     """Run the FastAPI server locally for development."""
#     uvicorn.run(
#         app,
#         host="localhost",
#         port=8000,
#         reload=True  # Enable hot-reloading for development
#     )
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# from slowapi.middleware import SlowAPIMiddleware
# from contextlib import asynccontextmanager
# from backend.src.utils.logger import logger
# from backend.src.config_settings.config_manager import ConfigurationManager
# from backend.src.pipeline.rag_pipeline import LegalRAGPipeline
# import uvicorn
#
# # Lifespan handler for resource management
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Initialize and clean up resources"""
#     try:
#         logger.info("Initializing LegalRAGPipeline")
#         app.state.pipeline = LegalRAGPipeline(ConfigurationManager())
#         logger.info("Pipeline ready")
#         yield
#     except Exception as e:
#         logger.error(f"Startup failed: {e}")
#         raise
#     finally:
#         logger.info("Shutting down")
#
# # App configuration
# app = FastAPI(
#     title="Legal RAG API",
#     description="High-performance API for legal case law queries",
#     version="1.0.0",
#     lifespan=lifespan,
#     docs_url="/docs",
#     redoc_url=None
# )
#
# # CORS (adjust for production)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"]
# )
#
# # Rate limiting setup
# limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
# app.state.limiter = limiter
# app.add_middleware(SlowAPIMiddleware)
# app.add_exception_handler(RateLimitExceeded, lambda _, exc: HTTPException(429, detail="Too many requests"))
#
# # Data models
# class QueryRequest(BaseModel):
#     query: str
#     model_id: str | None = None
#
# class HealthResponse(BaseModel):
#     status: str
#     version: str
#
# # Endpoints
# @app.get("/health", response_model=HealthResponse)
# async def health_check():
#     """System status endpoint"""
#     return {"status": "healthy", "version": app.version}
#
# @app.post("/query")
# @limiter.limit("30/minute")  # Adjust based on your expected load
# async def process_query(request: QueryRequest):
#     """Main query processing endpoint"""
#     try:
#         logger.info(f"Processing query: {request.query[:50]}...")
#         response = await app.state.pipeline.process_query(request.query, request.model_id)
#         return {
#             "status": "success",
#             "data": response,
#             "model": request.model_id or "default"
#         }
#     except Exception as e:
#         logger.error(f"Query failed: {str(e)}")
#         raise HTTPException(500, detail="Processing error")
#
# # Production-ready server config
# if __name__ == "__main__":
#     uvicorn.run(
#         app="main:app",
#         host="0.0.0.0",
#         port=8000,
#         workers=4,  # Adjust based on your server cores
#         timeout_keep_alive=60
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
origins = ["*"]  # Update to ["https://your-vercel-app.vercel.app"] in production

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