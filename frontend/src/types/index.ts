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
export interface Client {
  id: number;
  afm: string;           // ΑΦΜ - Greek Tax ID (9 digits)
  onoma: string;         // Επωνυμία - Company name
  email: string;
  phone: string;
  doy: string;           // ΔΟΥ - Tax office
  address?: string;
  city?: string;
  postal_code?: string;
  is_active: boolean;
  notes?: string;
  created: string;       // ISO date string
  modified: string;      // ISO date string
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
export interface Obligation {
  id: number;
  client: number;        // Foreign key to Client
  client_name?: string;  // Denormalized for display
  obligation_type: ObligationType;
  period_month: number;  // 1-12
  period_year: number;
  due_date: string;      // ISO date string
  status: ObligationStatus;
  completed_date?: string;
  notes?: string;
  created: string;
  modified: string;
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
  onoma: string;
  email?: string;
  phone?: string;
  doy?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  is_active?: boolean;
  notes?: string;
}

export interface ObligationFormData {
  client: number;
  obligation_type: ObligationType;
  period_month: number;
  period_year: number;
  due_date: string;
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
