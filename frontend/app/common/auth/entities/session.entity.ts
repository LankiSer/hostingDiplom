export interface SessionEntity {
  companyName: string;
  displayName: string;
  email: string;
  role: 'owner' | 'manager';
  token: string;
}
