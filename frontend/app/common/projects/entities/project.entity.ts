export interface ProjectEntity {
  environment: 'production' | 'staging';
  microservices: number;
  name: string;
  status: 'active' | 'draft';
}
