from fastapi import APIRouter

from src.core.config import get_settings
from src.schemas.contracts import InvoiceRequest, InvoiceResponse
from src.services.service import BillingService

router = APIRouter()
settings = get_settings()
service = BillingService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@router.get("/api/v1/info")
def info() -> dict[str, list[str] | str]:
    return {"name": settings.service_name, "capabilities": settings.capabilities}


@router.post("/api/v1/invoices", response_model=InvoiceResponse)
def create_invoice(payload: InvoiceRequest) -> InvoiceResponse:
    return InvoiceResponse(**service.create_invoice(payload))


@router.get("/api/v1/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: str) -> InvoiceResponse:
    return InvoiceResponse(**service.get_invoice(invoice_id))
