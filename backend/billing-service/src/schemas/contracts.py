from pydantic import BaseModel


class InvoiceRequest(BaseModel):
    amount: int
    company_name: str
    inn: str


class InvoiceResponse(BaseModel):
    amount: int
    company_name: str
    invoice_id: str
    status: str
    sync_target: str
