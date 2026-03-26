export interface InvoiceEntity {
  id: string;
  company_name: string;
  inn: string;
  description: string;
  amount: number;
  status: 'draft' | 'issued' | 'paid' | 'cancelled';
  onec_id: string;
  onec_number: string;
  created_at: string;
}
