from dataclasses import asdict

from src.repositories.repository import BillingRepository
from src.schemas.contracts import InvoiceRequest


class BillingService:
    def __init__(self, repository: BillingRepository | None = None) -> None:
        self.repository = repository or BillingRepository()

    def create_invoice(self, payload: InvoiceRequest) -> dict[str, str | int]:
        return asdict(self.repository.create_invoice(payload.amount, payload.company_name))

    def get_invoice(self, invoice_id: str) -> dict[str, str | int]:
        return asdict(self.repository.get_invoice(invoice_id))
