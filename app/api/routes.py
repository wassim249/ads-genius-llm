"""API routes for the Ads Genius AI service."""

import structlog
from fastapi import APIRouter, HTTPException, status

from app.api.schemas import CompletionRequest, CompletionResponse
from app.core.queue import get_queue
from app.services.model_service import LLMService

logger = structlog.get_logger(__name__)
router = APIRouter(
    tags=["llm"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error",
            "content": {"application/json": {"example": {"detail": "An unexpected error occurred"}}},
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Service Unavailable",
            "content": {"application/json": {"example": {"detail": "Service is at maximum capacity"}}},
        },
    },
)

model_service = LLMService()


@router.post("/complete", response_model=CompletionResponse)
async def get_completion(request: CompletionRequest) -> CompletionResponse:
    """Get LLM completions for masked tokens in the input text."""
    print(request)
    try:
        logger.info("Processing completion request", text=request.text)
        queue = get_queue()

        async def process_completion():
            return await model_service.get_completion(
                text=request.text,
                temperature=request.temperature,
                max_new_tokens=request.max_new_tokens,
                top_p=request.top_p,
                top_k=request.top_k,
                repetition_penalty=request.repetition_penalty,
                tone=request.tone,
            )

        async with queue.request(process_completion) as response:
            logger.info("Completion successful", response=response.model_dump())
            return response

    except Exception as e:
        logger.error("Error processing completion request", error=str(e))
        if "Queue not initialized" in str(e):
            raise HTTPException(  # noqa: B904
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service is starting up",
            )
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


@router.get("/queue/status")
async def get_queue_status() -> dict:
    """Get current queue status."""
    try:
        queue = get_queue()
        return {
            "active_requests": queue.current_requests,
            "queued_requests": queue.queue.qsize(),
            "max_parallel_requests": queue.max_parallel_requests,
        }
    except Exception as e:
        logger.error("Error getting queue status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    try:
        logger.info("Health check started")
        # Simple inference to check if model is working
        model_service.get_completion("The [MASK] is a test.")
        queue = get_queue()
        return {
            "status": "healthy",
            "queue": {
                "active_requests": queue.current_requests,
                "queued_requests": queue.queue.qsize(),
            },
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")  # noqa: B904
