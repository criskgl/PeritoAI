"""FastAPI server for PeritoAI with WhatsApp webhook support."""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add engine module to path
sys.path.insert(0, str(Path(__file__).parent))

from engine.rag_engine import RAGEngine
from engine.generator import ReportGenerator
from engine.pdf_exporter import ReportPDFExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PeritoAI API",
    description="API for generating insurance adjuster reports using RAG and LLM",
    version="1.0.0",
)

# Global instances (initialized on startup)
rag_engine: Optional[RAGEngine] = None
generator: Optional[ReportGenerator] = None
pdf_exporter: Optional[ReportPDFExporter] = None


# Pydantic models for request/response
class ReportRequest(BaseModel):
    """Request model for report generation."""

    field_notes: str = Field(..., description="Adjuster's field notes from visit")
    policy_id: str = Field(..., description="Policy ID to search for")
    claim_id: Optional[str] = Field(None, description="Optional claim ID")
    query_context: Optional[str] = Field(None, description="Optional query context for RAG search")


class WebhookPayload(BaseModel):
    """Webhook payload model for Meta WhatsApp Cloud API."""

    object: Optional[str] = None
    entry: Optional[list] = None

    class Config:
        extra = "allow"  # Allow additional fields from Meta


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    message: str
    engine_initialized: bool


@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine and generator on startup."""
    global rag_engine, generator, pdf_exporter

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not found. Some endpoints may not work.")
        return

    try:
        logger.info("Initializing RAG engine...")
        rag_engine = RAGEngine(
            policies_dir="data/policies",
            chroma_db_dir="data/chroma_db",
            api_key=api_key,
        )
        generator = ReportGenerator(
            rag_engine=rag_engine,
            api_key=api_key,
        )
        pdf_exporter = ReportPDFExporter()
        logger.info("RAG engine and generator initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing engine: {str(e)}")
        raise


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check."""
    return HealthResponse(
        status="ok",
        message="PeritoAI API is running",
        engine_initialized=rag_engine is not None and generator is not None,
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if (rag_engine and generator) else "unhealthy",
        message="Service is operational" if (rag_engine and generator) else "Engine not initialized",
        engine_initialized=rag_engine is not None and generator is not None,
    )


@app.post("/api/generate-report")
async def generate_report(request: ReportRequest):
    """
    Generate an insurance adjuster report.

    Args:
        request: Report generation request with field notes, policy ID, etc.

    Returns:
        Generated report in JSON format
    """
    if not generator or not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized. Please check GEMINI_API_KEY configuration.",
        )

    try:
        logger.info(f"Generating report for policy_id={request.policy_id}, claim_id={request.claim_id}")

        # Generate report
        report_dict = generator.generate_report_dict(
            field_notes=request.field_notes,
            policy_id=request.policy_id,
            claim_id=request.claim_id,
            query_context=request.query_context,
        )

        return JSONResponse(content=report_dict)

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@app.post("/api/generate-report-pdf")
async def generate_report_pdf(request: ReportRequest):
    """
    Generate an insurance adjuster report and return PDF.

    Args:
        request: Report generation request

    Returns:
        PDF file as response
    """
    from fastapi.responses import FileResponse

    if not generator or not rag_engine or not pdf_exporter:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized. Please check GEMINI_API_KEY configuration.",
        )

    try:
        logger.info(f"Generating PDF report for policy_id={request.policy_id}")

        # Generate report
        report_dict = generator.generate_report_dict(
            field_notes=request.field_notes,
            policy_id=request.policy_id,
            claim_id=request.claim_id,
            query_context=request.query_context,
        )

        # Generate PDF
        pdf_path = pdf_exporter.export_from_dict(report_dict)

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=Path(pdf_path).name,
        )

    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF report: {str(e)}")


@app.post("/webhook")
async def webhook(request: Request):
    """
    Webhook endpoint for Meta WhatsApp Cloud API.

    This endpoint is prepared to receive JSON payloads from Meta.
    For now, it logs the payload and can call the generator logic.

    Args:
        request: FastAPI request object

    Returns:
        Response for Meta webhook verification or processing confirmation
    """
    try:
        # Get raw body for verification (if needed)
        body = await request.body()

        # Try to parse as JSON
        try:
            payload = await request.json()
            logger.info(f"Received webhook payload: {payload}")

            # Log the payload structure
            logger.info(f"Webhook object: {payload.get('object')}")
            logger.info(f"Webhook entries: {payload.get('entry')}")

            # TODO: Implement WhatsApp message parsing
            # Extract message content, sender, etc. from Meta payload format
            # Example structure from Meta:
            # {
            #     "object": "whatsapp_business_account",
            #     "entry": [{
            #         "id": "...",
            #         "changes": [{
            #             "value": {
            #                 "messages": [{
            #                     "from": "...",
            #                     "text": {"body": "..."}
            #                 }]
            #             }
            #         }]
            #     }]
            # }

            # For now, just acknowledge receipt
            # In production, you would:
            # 1. Parse the WhatsApp message
            # 2. Extract field notes and policy ID from message
            # 3. Call generator.generate_report_dict()
            # 4. Send response back via WhatsApp Business API

            return JSONResponse(
                content={
                    "status": "received",
                    "message": "Webhook payload logged successfully",
                    "payload_object": payload.get("object"),
                }
            )

        except Exception as json_error:
            # Handle GET request for webhook verification
            if request.method == "GET":
                # Meta sends GET request for webhook verification
                verify_token = request.query_params.get("hub.verify_token")
                challenge = request.query_params.get("hub.challenge")
                mode = request.query_params.get("hub.mode")

                # Verify the token (should match your configured token)
                expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "peritoai_verify_token")

                if mode == "subscribe" and verify_token == expected_token:
                    logger.info("Webhook verified successfully")
                    return int(challenge) if challenge else JSONResponse(
                        content={"status": "verified"}
                    )
                else:
                    logger.warning(f"Webhook verification failed. Token mismatch or invalid mode.")
                    raise HTTPException(status_code=403, detail="Forbidden")

            logger.error(f"Error parsing webhook JSON: {str(json_error)}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid JSON payload", "detail": str(json_error)},
            )

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


@app.post("/api/index-policies")
async def index_policies(overwrite: bool = False):
    """
    Index PDF policies from the policies directory.

    Args:
        overwrite: If True, recreate the index from scratch

    Returns:
        Status of indexing operation
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized. Please check GEMINI_API_KEY configuration.",
        )

    try:
        logger.info(f"Indexing policies (overwrite={overwrite})")
        rag_engine.index_policies(overwrite=overwrite)
        return JSONResponse(
            content={
                "status": "success",
                "message": "Policies indexed successfully",
                "overwrite": overwrite,
            }
        )
    except Exception as e:
        logger.error(f"Error indexing policies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error indexing policies: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
