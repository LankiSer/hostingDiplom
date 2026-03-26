export type WorkspaceTone = 'default' | 'success' | 'warning';

export interface WorkspaceBadgeEntity {
  label: string;
  tone?: WorkspaceTone;
}

export interface WorkspaceFactEntity {
  label: string;
  value: string;
}

export interface WorkspaceActionEntity {
  external?: boolean;
  label: string;
  to: string;
  tone?: 'primary' | 'secondary';
}

export interface WorkspaceCardEntity {
  actions?: WorkspaceActionEntity[];
  badge?: WorkspaceBadgeEntity;
  description: string;
  facts?: WorkspaceFactEntity[];
  title: string;
}

export interface WorkspacePageEntity {
  cards: WorkspaceCardEntity[];
  description: string;
  title: string;
}
