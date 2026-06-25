import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.core.rbac import CurrentUser, require_permission
from src.repositories.audit_repository import AuditRepository
from src.repositories.billing_repository import BillingRepository
from src.services import onec_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/billing")
repo = BillingRepository()
audit = AuditRepository()


class InvoiceCreate(BaseModel):
    company_name: str
    inn: str
    amount: float
    description: str = ""


@router.get("/invoices")
def list_invoices() -> list[dict]:
    return repo.list_invoices()


@router.post("/invoices", status_code=201)
def create_invoice(
    body: InvoiceCreate,
    actor: CurrentUser = Depends(require_permission("billing:write")),
) -> dict:
    if not body.company_name.strip():
        raise HTTPException(status_code=400, detail="company_name is required")
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")

    invoice = repo.create_invoice(
        company_name=body.company_name.strip(),
        inn=body.inn.strip(),
        amount=body.amount,
        description=body.description,
    )

    onec_result = onec_client.create_invoice(
        company_name=body.company_name,
        inn=body.inn,
        amount=body.amount,
        description=body.description,
    )

    if onec_result:
        invoice = repo.sync_with_onec(
            invoice_id=invoice["id"],
            onec_id=onec_result.get("id", ""),
            onec_number=onec_result.get("number", ""),
            status="issued",
        ) or invoice
        logger.info("Invoice %s synced to 1C as #%s", invoice["id"], onec_result.get("number"))
    else:
        logger.info("Invoice %s stored locally (1C not available)", invoice["id"])

    audit.record(
        actor=actor,
        action="billing.invoice_create",
        resource_type="invoice",
        resource_id=invoice["id"],
        message=f"Создан счёт для {invoice['company_name']}",
        metadata={"amount": float(invoice["amount"]), "status": invoice["status"]},
    )
    return invoice


@router.get("/invoices/export")
def export_for_onec() -> list[dict]:
    """Export draft invoices for 1C file import. Returns JSON array."""
    all_invoices = repo.list_invoices()
    drafts = [i for i in all_invoices if i.get("status") == "draft" and not i.get("onec_id")]
    return [
        {
            "id": i["id"],
            "company": i["company_name"],
            "inn": i.get("inn") or "",
            "amount": float(i["amount"]),
            "description": i.get("description") or "",
            "created_at": i.get("created_at", ""),
        }
        for i in drafts
    ]


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: str) -> dict:
    invoice = repo.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.get("onec_id"):
        live = onec_client.get_invoice_status(invoice["onec_id"])
        if live and live.get("status"):
            invoice["onec_status"] = live["status"]
    return invoice


@router.post("/invoices/{invoice_id}/mark-paid")
def mark_paid(
    invoice_id: str,
    actor: CurrentUser = Depends(require_permission("billing:write")),
) -> dict:
    updated = repo.update_status(invoice_id, "paid")
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    audit.record(
        actor=actor,
        action="billing.invoice_paid",
        resource_type="invoice",
        resource_id=invoice_id,
        message=f"Счёт {invoice_id} отмечен оплаченным",
        metadata={"status": "paid"},
    )
    return updated


@router.post("/invoices/{invoice_id}/cancel")
def cancel_invoice(
    invoice_id: str,
    actor: CurrentUser = Depends(require_permission("billing:write")),
) -> dict:
    updated = repo.update_status(invoice_id, "cancelled")
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    audit.record(
        actor=actor,
        action="billing.invoice_cancel",
        resource_type="invoice",
        resource_id=invoice_id,
        message=f"Счёт {invoice_id} отменён",
        metadata={"status": "cancelled"},
    )
    return updated


@router.get("/status")
def billing_status() -> dict:
    return {
        "onec_configured": onec_client.is_configured(),
        "onec_url": onec_client.ONEC_URL or "not set",
    }
