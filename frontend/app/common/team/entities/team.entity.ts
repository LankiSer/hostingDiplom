export interface TeamMember {
  activated_at?: string;
  created_at?: string;
  email: string;
  id: string;
  initials: string;
  invite_expires_at?: string;
  invite_url?: string;
  invited_at?: string;
  last_seen_at?: string;
  name: string;
  permissions: string[];
  projects: number;
  role: 'owner' | 'ops' | 'finance' | 'viewer';
  role_label: string;
  status: 'active' | 'invited' | 'disabled' | 'cancelled';
}

export interface TeamRole {
  description: string;
  id: 'owner' | 'ops' | 'finance' | 'viewer';
  members: number;
  name: string;
  permissions: string[];
}

export interface TeamOverview {
  members: TeamMember[];
  roles: TeamRole[];
}

export interface AuditLog {
  action: string;
  actor_email: string;
  actor_role: string;
  created_at: string;
  id: string;
  message: string;
  metadata: Record<string, unknown>;
  resource_id: string;
  resource_type: string;
}

export interface AuditResponse {
  items: AuditLog[];
  stats: {
    billing_events: number;
    hosting_events: number;
    last_24h: number;
    team_events: number;
  };
}

export interface TeamCallMessage {
  author_email: string;
  author_name: string;
  body: string;
  created_at: string;
  id: string;
  kind: 'chat' | 'whiteboard' | 'system';
}

export interface TeamCallSession {
  created_by: string;
  ended_at?: string;
  id: string;
  messages: TeamCallMessage[];
  started_at: string;
  status: 'active' | 'ended';
  title: string;
  tldraw_room: string;
  tldraw_url: string;
}

export interface TeamCallLivekitConnection {
  identity: string;
  name: string;
  room: string;
  token: string;
  url: string;
}
