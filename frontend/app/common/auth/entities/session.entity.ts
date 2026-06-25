export interface SessionEntity {
  companyName: string;
  displayName: string;
  email: string;
  permissions?: string[];
  role: 'owner' | 'ops' | 'finance' | 'viewer';
  token: string;
}
