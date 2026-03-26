from dataclasses import dataclass


@dataclass(slots=True)
class InvoiceEntity:
    amount: int
    company_name: str
    invoice_id: str
    status: str
    sync_target: str
