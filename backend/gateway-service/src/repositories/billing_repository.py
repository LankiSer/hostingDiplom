from src.core.database import get_connection, serialize_row


class BillingRepository:
    def list_invoices(self) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM invoices ORDER BY created_at DESC")
                return [serialize_row(r) for r in cur.fetchall()]

    def create_invoice(
        self,
        company_name: str,
        inn: str,
        amount: float,
        description: str = "",
    ) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO invoices (company_name, inn, amount, description)
                       VALUES (%s, %s, %s, %s) RETURNING *""",
                    (company_name, inn, amount, description),
                )
                conn.commit()
                return serialize_row(cur.fetchone())

    def get_invoice(self, invoice_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM invoices WHERE id = %s", (invoice_id,))
                return serialize_row(cur.fetchone())

    def sync_with_onec(
        self,
        invoice_id: str,
        onec_id: str,
        onec_number: str,
        status: str = "issued",
    ) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE invoices
                       SET onec_id = %s, onec_number = %s, status = %s
                       WHERE id = %s RETURNING *""",
                    (onec_id, onec_number, status, invoice_id),
                )
                conn.commit()
                return serialize_row(cur.fetchone())

    def update_status(self, invoice_id: str, status: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE invoices SET status = %s WHERE id = %s RETURNING *",
                    (status, invoice_id),
                )
                conn.commit()
                return serialize_row(cur.fetchone())
