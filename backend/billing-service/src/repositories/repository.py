from src.domain.entities import InvoiceEntity


class BillingRepository:
    def create_invoice(self, amount: int, company_name: str) -> InvoiceEntity:
        return InvoiceEntity(
            amount=amount,
            company_name=company_name,
            invoice_id="inv-001",
            status="issued",
            sync_target="1c",
        )

    def get_invoice(self, invoice_id: str) -> InvoiceEntity:
        return InvoiceEntity(
            amount=54000,
            company_name="Gcloude LLC",
            invoice_id=invoice_id,
            status="issued",
            sync_target="1c",
        )
