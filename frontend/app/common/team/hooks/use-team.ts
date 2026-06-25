import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';
import type { AuditResponse, TeamCallLivekitConnection, TeamCallMessage, TeamCallSession, TeamOverview } from '../entities/team.entity';

export function useTeam() {
  const api = usePlatformApi();

  return {
    activateMember: (id: string) => api.put<TeamOverview>(`/api/v1/platform/team/members/${id}`, { status: 'active' }),
    addCallMessage: (sessionId: string, body: string, kind = 'chat') => api.post<TeamCallMessage>(`/api/v1/platform/team/calls/${sessionId}/messages`, { body, kind }),
    cancelInvite: (id: string) => api.post<TeamOverview>(`/api/v1/platform/team/members/${id}/cancel-invite`, {}),
    createCall: (title: string) => api.post<TeamCallSession>('/api/v1/platform/team/calls', { title }),
    deleteMember: (id: string) => api.del(`/api/v1/platform/team/members/${id}`) as Promise<TeamOverview>,
    disableMember: (id: string) => api.put<TeamOverview>(`/api/v1/platform/team/members/${id}`, { status: 'disabled' }),
    endCall: (sessionId: string) => api.post<TeamCallSession>(`/api/v1/platform/team/calls/${sessionId}/end`, {}),
    getActiveCall: () => api.get<TeamCallSession | null>('/api/v1/platform/team/calls/active'),
    getLivekitConnection: (sessionId: string) => api.get<TeamCallLivekitConnection>(`/api/v1/platform/team/calls/${sessionId}/livekit`),
    getAudit: () => api.get<AuditResponse>('/api/v1/platform/team/audit'),
    getOverview: () => api.get<TeamOverview>('/api/v1/platform/team/overview'),
    inviteMember: (email: string, role: string) => api.post<TeamOverview>('/api/v1/platform/team/invite', { email, role }),
    resendInvite: (id: string) => api.post<TeamOverview>(`/api/v1/platform/team/members/${id}/resend-invite`, {}),
    updateRole: (id: string, role: string) => api.put<TeamOverview>(`/api/v1/platform/team/members/${id}`, { role }),
  };
}
