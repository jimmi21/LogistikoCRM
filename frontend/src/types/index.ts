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
