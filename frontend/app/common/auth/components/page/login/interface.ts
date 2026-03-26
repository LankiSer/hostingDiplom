import type { SessionEntity } from '../../../entities/session.entity';

export interface AuthLoginPageState {
  invite: string;
  session: SessionEntity;
}
