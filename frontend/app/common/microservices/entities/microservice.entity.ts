export interface MicroserviceEntity {
  domain: string;
  runtime: 'node' | 'python';
  status: 'healthy' | 'pending';
  version: string;
}
