/**
 * fileManager.ts
 * Types for the File Manager system
 */

// Document Tag
export interface DocumentTag {
  id: number;
  name: string;
  color: string;
  icon?: string;
  description?: string;
  document_count?: number;
  created_at: string;
}

// Document with full details
export interface FileManagerDocument {
  id: number;
  client: number;
  client_name: string;
  client_afm: string;
  obligation?: number | null;
  obligation_type?: string | null;
  obligation_period?: string | null;
  file: string;
  file_url: string | null;
  filename: string;
  original_filename?: string;
  file_type: string;
  file_size: number;
  file_size_display: string;
  document_category: DocumentCategory;
  category_display: string;
  description?: string;
  year: number;
  month: number;
  version: number;
  is_current: boolean;
  uploaded_at: string;
  uploaded_by?: string | null;
  tags: { id: number; name: string; color: string }[];
  is_favorite: boolean;
  can_preview: boolean;
  shared_links_count: number;
}

// Document categories
export type DocumentCategory =
  | 'contracts'
  | 'invoices'
  | 'tax'
  | 'myf'
  | 'vat'
  | 'apd'
  | 'payroll'
  | 'efka'
  | 'general';

export const DOCUMENT_CATEGORIES: { value: DocumentCategory; label: string; icon: string; color: string }[] = [
  { value: 'contracts', label: 'Συμβάσεις', icon: 'file-signature', color: '#8B5CF6' },
  { value: 'invoices', label: 'Τιμολόγια', icon: 'receipt', color: '#10B981' },
  { value: 'tax', label: 'Φορολογικά', icon: 'landmark', color: '#F59E0B' },
  { value: 'myf', label: 'ΜΥΦ', icon: 'file-spreadsheet', color: '#3B82F6' },
  { value: 'vat', label: 'ΦΠΑ', icon: 'percent', color: '#EF4444' },
  { value: 'apd', label: 'ΑΠΔ', icon: 'users', color: '#6366F1' },
  { value: 'payroll', label: 'Μισθοδοσία', icon: 'wallet', color: '#EC4899' },
  { value: 'efka', label: 'ΕΦΚΑ', icon: 'shield', color: '#14B8A6' },
  { value: 'general', label: 'Γενικά', icon: 'folder', color: '#6B7280' },
];

// Shared Link
export interface SharedLink {
  id: number;
  document?: number | null;
  document_filename?: string | null;
  client?: number | null;
  client_name?: string | null;
  token: string;
  name: string;
  access_level: 'view' | 'download';
  requires_email: boolean;
  expires_at?: string | null;
  max_downloads?: number | null;
  download_count: number;
  view_count: number;
  last_accessed_at?: string | null;
  is_active: boolean;
  is_expired: boolean;
  is_valid: boolean;
  public_url: string;
  created_at: string;
  created_by?: number | null;
  created_by_name?: string | null;
}

// Create shared link request
export interface CreateSharedLinkRequest {
  document_id?: number | null;
  client_id?: number | null;
  name?: string;
  access_level?: 'view' | 'download';
  password?: string;
  requires_email?: boolean;
  expires_in_days?: number | null;
  max_downloads?: number | null;
}

// Document Favorite
export interface DocumentFavorite {
  id: number;
  document: FileManagerDocument;
  note?: string;
  created_at: string;
}

// Document Collection
export interface DocumentCollection {
  id: number;
  name: string;
  description?: string;
  color: string;
  icon: string;
  owner?: number;
  owner_name?: string;
  is_shared: boolean;
  document_count: number;
  documents?: FileManagerDocument[];
  created_at: string;
  updated_at: string;
}

// File Manager Stats
export interface FileManagerStats {
  total_documents: number;
  total_size: number;
  total_size_display: string;
  recent_uploads_count: number;
  active_shared_links: number;
  favorites_count: number;
  collections_count: number;
  by_category: { document_category: string; count: number }[];
  by_file_type: { file_type: string; count: number }[];
}

// Browse response types
export interface BrowseClientsResponse {
  type: 'clients';
  clients: {
    id: number;
    eponimia: string;
    afm: string;
    document_count: number;
  }[];
}

export interface BrowseYearsResponse {
  type: 'years';
  client: { id: number; eponimia: string };
  years: { year: number; count: number }[];
}

export interface BrowseMonthsResponse {
  type: 'months';
  client: { id: number; eponimia: string };
  year: string;
  months: { month: number; count: number }[];
}

export interface BrowseDocumentsResponse {
  type: 'documents';
  client: { id: number; eponimia: string };
  year: string;
  month: string;
  documents: FileManagerDocument[];
}

export type BrowseResponse =
  | BrowseClientsResponse
  | BrowseYearsResponse
  | BrowseMonthsResponse
  | BrowseDocumentsResponse;

// Upload response
export interface UploadResponse {
  message: string;
  uploaded: number;
  errors: string[];
  documents: FileManagerDocument[];
}

// Document filters
export interface DocumentFilters {
  client_id?: number;
  client_afm?: string;
  obligation_id?: number;
  category?: DocumentCategory;
  year?: number;
  month?: number;
  file_type?: string;
  is_current?: boolean;
  has_obligation?: boolean;
  search?: string;
  tag?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

// Preview info
export interface DocumentPreview {
  id: number;
  filename: string;
  file_type: string;
  preview_type: 'pdf' | 'image' | 'unknown';
  can_preview: boolean;
  url: string | null;
  file_size: number;
  file_size_display: string;
  uploaded_at: string;
  version: number;
  client_name: string;
}

// Version history
export interface VersionHistory {
  document_id: number;
  current_version: number;
  total_versions: number;
  versions: FileManagerDocument[];
}

// Access log entry
export interface AccessLogEntry {
  accessed_at: string;
  ip_address: string | null;
  action: 'view' | 'download';
  email_provided?: string;
}

// Public shared content
export interface PublicSharedContent {
  type: 'document' | 'folder';
  name: string;
  access_level: 'view' | 'download';
  document?: {
    id: number;
    filename: string;
    file_type: string;
    file_size_display: string;
    preview_url: string | null;
    can_download: boolean;
  };
  client?: {
    eponimia: string;
    afm: string;
  };
  documents?: {
    id: number;
    filename: string;
    file_type: string;
    file_size_display: string;
    category: string;
    uploaded_at: string;
  }[];
}

// View modes
export type ViewMode = 'grid' | 'list' | 'tree';

// Sort options
export type SortField = 'uploaded_at' | 'filename' | 'file_size' | 'year' | 'month';
export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  field: SortField;
  direction: SortDirection;
}

// Selection state
export interface SelectionState {
  selectedIds: Set<number>;
  isAllSelected: boolean;
}

// Greek months for display
export const GREEK_MONTHS = [
  'Ιανουάριος',
  'Φεβρουάριος',
  'Μάρτιος',
  'Απρίλιος',
  'Μάιος',
  'Ιούνιος',
  'Ιούλιος',
  'Αύγουστος',
  'Σεπτέμβριος',
  'Οκτώβριος',
  'Νοέμβριος',
  'Δεκέμβριος',
];
