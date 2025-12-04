// User types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
}

// Client/Customer types (ClientProfile in Django)
// Fields match accounting/serializers.py ClientSerializer
export interface Client {
  id: number;
  afm: string;                      // ΑΦΜ - Greek Tax ID (9 digits)
  eponimia: string;                 // Επωνυμία - Company name
  email?: string | null;
  kinito_tilefono?: string | null;  // Κινητό τηλέφωνο
  tilefono_oikias_1?: string | null;
  tilefono_oikias_2?: string | null;
  tilefono_epixeirisis_1?: string | null;
  tilefono_epixeirisis_2?: string | null;
  total_obligations?: number;
  is_active?: boolean;
}

// Obligation status types
export type ObligationStatus =
  | 'pending'      // Εκκρεμεί
  | 'in_progress'  // Σε εξέλιξη
  | 'completed'    // Ολοκληρώθηκε
  | 'overdue'      // Εκπρόθεσμη
  | 'cancelled';   // Ακυρώθηκε

// Obligation type codes
export type ObligationType =
  | 'ΦΠΑ'    // Φόρος Προστιθέμενης Αξίας
  | 'ΑΠΔ'    // Αναλυτική Περιοδική Δήλωση ΕΦΚΑ
  | 'ΕΝΦΙΑ'  // Ενιαίος Φόρος Ιδιοκτησίας
  | 'Ε1'     // Δήλωση Φορολογίας Εισοδήματος
  | 'Ε3'     // Κατάσταση Οικονομικών Στοιχείων
  | 'ΜΥΦ'    // Συγκεντρωτικές Καταστάσεις
  | string;  // Allow custom types

// Monthly Obligation type
// Fields match accounting/serializers.py MonthlyObligationSerializer
export interface Obligation {
  id: number;
  client: number;               // Foreign key to Client
  client_name?: string;         // from client.eponimia (read_only)
  obligation_type: number;      // Foreign key to ObligationType
  type_name?: string;           // from obligation_type.name (read_only)
  type_code?: string;           // from obligation_type.code (read_only)
  month: number;                // 1-12
  year: number;
  deadline: string;             // ISO date string
  status: ObligationStatus;
  completed_date?: string | null;
  completed_by?: number | null;
  notes?: string;
  time_spent?: number | null;
  hourly_rate?: number | null;
  attachment?: string | null;
  attachments?: string[];
  created_at: string;
  updated_at: string;
}

// Ticket types
export type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'closed';
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Ticket {
  id: number;
  client: number;
  client_name?: string;
  subject: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  assigned_to?: number;
  assigned_to_name?: string;
  created_at: string;
  updated_at: string;
}

// API response types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  [key: string]: unknown;
}

// Auth types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

// Form types for creating/updating
export interface ClientFormData {
  afm: string;
  eponimia: string;
  email?: string;
  kinito_tilefono?: string;
  tilefono_oikias_1?: string;
  tilefono_epixeirisis_1?: string;
  is_active?: boolean;
}

export interface ObligationFormData {
  client: number;
  obligation_type: number;  // FK to ObligationType
  month: number;
  year: number;
  deadline: string;
  status?: ObligationStatus;
  notes?: string;
}

// Dashboard statistics
export interface DashboardStats {
  total_clients: number;
  active_clients: number;
  pending_obligations: number;
  overdue_obligations: number;
  completed_this_month: number;
}

// Obligation Type from API
export interface ObligationTypeData {
  id: number;
  code: string;
  name: string;
  frequency: 'monthly' | 'quarterly' | 'annual' | 'follows_vat';
  deadline_type: 'last_day' | 'specific_day' | 'last_day_prev' | 'last_day_next';
  deadline_day: number | null;
}

// Bulk creation form data
export interface BulkObligationFormData {
  client_ids: number[];
  obligation_type: number;
  month: number;
  year: number;
}

// Bulk update form data
export interface BulkUpdateFormData {
  obligation_ids: number[];
  status: ObligationStatus;
}

// ============================================
// CLIENT DETAILS TYPES
// ============================================

// Full client interface with all fields
export interface ClientFull {
  id: number;
  // Basic info
  afm: string;
  doy?: string | null;
  eponimia: string;
  onoma?: string | null;
  onoma_patros?: string | null;
  // Identity
  arithmos_taftotitas?: string | null;
  eidos_taftotitas?: string | null;
  prosopikos_arithmos?: string | null;
  amka?: string | null;
  am_ika?: string | null;
  arithmos_gemi?: string | null;
  arithmos_dypa?: string | null;
  // Personal dates
  imerominia_gennisis?: string | null;
  imerominia_gamou?: string | null;
  filo?: 'M' | 'F' | null;
  // Home address
  diefthinsi_katoikias?: string | null;
  arithmos_katoikias?: string | null;
  poli_katoikias?: string | null;
  dimos_katoikias?: string | null;
  nomos_katoikias?: string | null;
  tk_katoikias?: string | null;
  tilefono_oikias_1?: string | null;
  tilefono_oikias_2?: string | null;
  kinito_tilefono?: string | null;
  // Business address
  diefthinsi_epixeirisis?: string | null;
  arithmos_epixeirisis?: string | null;
  poli_epixeirisis?: string | null;
  dimos_epixeirisis?: string | null;
  nomos_epixeirisis?: string | null;
  tk_epixeirisis?: string | null;
  tilefono_epixeirisis_1?: string | null;
  tilefono_epixeirisis_2?: string | null;
  email?: string | null;
  // Bank info
  trapeza?: string | null;
  iban?: string | null;
  // Tax info
  eidos_ipoxreou: 'individual' | 'professional' | 'company';
  katigoria_vivlion?: 'A' | 'B' | 'C' | 'none' | null;
  nomiki_morfi?: string | null;
  agrotis?: boolean;
  imerominia_enarksis?: string | null;
  // Credentials
  onoma_xristi_taxisnet?: string | null;
  kodikos_taxisnet?: string | null;
  onoma_xristi_ika_ergodoti?: string | null;
  kodikos_ika_ergodoti?: string | null;
  onoma_xristi_gemi?: string | null;
  kodikos_gemi?: string | null;
  // Related
  afm_sizigou?: string | null;
  afm_foreas?: string | null;
  am_klidi?: string | null;
  // Meta
  is_active: boolean;
  created_at: string;
  updated_at: string;
  // Computed counts
  obligations_count?: number;
  documents_count?: number;
  pending_obligations_count?: number;
  // Extended counts from /full endpoint
  counts?: {
    obligations: number;
    pending_obligations: number;
    overdue_obligations: number;
    documents: number;
    emails: number;
    calls: number;
    tickets: number;
    open_tickets: number;
  };
}

// Client Document interface
export interface ClientDocument {
  id: number;
  client: number;
  client_name?: string;
  obligation?: number | null;
  obligation_type?: string | null;
  file: string;
  file_url?: string | null;
  filename: string;
  file_type: string;
  document_category: 'contracts' | 'invoices' | 'tax' | 'myf' | 'vat' | 'payroll' | 'general';
  category_display?: string;
  description?: string;
  uploaded_at: string;
}

// Document categories with Greek labels
export const DOCUMENT_CATEGORIES = [
  { value: 'contracts', label: 'Συμβάσεις', icon: '📜' },
  { value: 'invoices', label: 'Τιμολόγια', icon: '🧾' },
  { value: 'tax', label: 'Φορολογικά', icon: '📋' },
  { value: 'myf', label: 'ΜΥΦ', icon: '📊' },
  { value: 'vat', label: 'ΦΠΑ', icon: '💶' },
  { value: 'payroll', label: 'Μισθοδοσία', icon: '👥' },
  { value: 'general', label: 'Γενικά', icon: '📁' },
] as const;

// Email Log interface
export interface EmailLog {
  id: number;
  recipient_email: string;
  subject: string;
  status: 'sent' | 'failed' | 'pending';
  status_display?: string;
  sent_at: string | null;
  template_name?: string | null;
  obligation_id?: number | null;
}

// VoIP Call interface
export interface VoIPCall {
  id: number;
  call_id: string;
  phone_number: string;
  direction: 'incoming' | 'outgoing';
  direction_display?: string;
  status: 'active' | 'completed' | 'missed' | 'failed';
  status_display?: string;
  started_at: string | null;
  ended_at?: string | null;
  duration_seconds: number;
  duration_formatted?: string;
  notes?: string;
  resolution?: 'pending' | 'closed' | 'follow_up';
  ticket_created?: boolean;
}

// VoIP Ticket interface (extended from base Ticket)
export interface VoIPTicket {
  id: number;
  title: string;
  description?: string;
  status: 'open' | 'assigned' | 'in_progress' | 'resolved' | 'closed';
  status_display?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  priority_display?: string;
  assigned_to?: number | null;
  assigned_to_name?: string | null;
  created_at: string;
  resolved_at?: string | null;
  is_open: boolean;
  days_since_created: number;
}

// Taxpayer types (eidos_ipoxreou)
export const TAXPAYER_TYPES = [
  { value: 'individual', label: 'Ιδιώτης' },
  { value: 'professional', label: 'Επαγγελματίας' },
  { value: 'company', label: 'Εταιρεία' },
] as const;

// Book categories (katigoria_vivlion)
export const BOOK_CATEGORIES = [
  { value: 'A', label: 'Α Κατηγορία' },
  { value: 'B', label: 'Β Κατηγορία' },
  { value: 'C', label: 'Γ Κατηγορία' },
  { value: 'none', label: 'Χωρίς Βιβλία' },
] as const;

// Legal forms (nomiki_morfi)
export const LEGAL_FORMS = [
  { value: 'ΑΕ', label: 'Ανώνυμη Εταιρεία (Α.Ε.)' },
  { value: 'ΕΠΕ', label: 'Εταιρεία Περιορισμένης Ευθύνης (Ε.Π.Ε.)' },
  { value: 'ΙΚΕ', label: 'Ιδιωτική Κεφαλαιουχική Εταιρεία (Ι.Κ.Ε.)' },
  { value: 'ΟΕ', label: 'Ομόρρυθμη Εταιρεία (Ο.Ε.)' },
  { value: 'ΕΕ', label: 'Ετερόρρυθμη Εταιρεία (Ε.Ε.)' },
  { value: 'ΑΤΟΜΙΚΗ', label: 'Ατομική Επιχείρηση' },
] as const;
