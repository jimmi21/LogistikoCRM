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
// EMAIL TYPES
// ============================================

// Email Template
export interface EmailTemplate {
  id: number;
  name: string;
  description?: string;
  subject: string;
  body_html?: string;
  obligation_type?: number | null;
  obligation_type_name?: string | null;
  obligation_type_code?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  available_variables?: EmailVariable[];
}

export interface EmailVariable {
  key: string;
  description: string;
}

export interface EmailTemplateFormData {
  name: string;
  description?: string;
  subject: string;
  body_html: string;
  obligation_type?: number | null;
  is_active?: boolean;
}

// Email Log
export type EmailLogStatus = 'sent' | 'failed' | 'pending';

export interface EmailLog {
  id: number;
  recipient_email: string;
  recipient_name: string;
  client?: number | null;
  client_name?: string | null;
  client_afm?: string | null;
  obligation?: number | null;
  template_used?: number | null;
  template_name?: string | null;
  subject: string;
  body: string;
  status: EmailLogStatus;
  status_display?: string;
  error_message?: string;
  sent_at: string;
  sent_by?: number | null;
  sent_by_username?: string | null;
}

// Scheduled Email
export type ScheduledEmailStatus = 'pending' | 'sent' | 'failed' | 'cancelled';

export interface ScheduledEmail {
  id: number;
  recipient_email: string;
  recipient_name: string;
  recipient_count?: number;
  recipients_display?: string;
  recipients_list?: string[];
  client?: number | null;
  client_name?: string | null;
  template?: number | null;
  template_name?: string | null;
  automation_rule?: number | null;
  subject: string;
  body_html?: string;
  send_at: string;
  sent_at?: string | null;
  status: ScheduledEmailStatus;
  error_message?: string;
  created_by?: number | null;
  created_by_username?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface ScheduledEmailFormData {
  recipient_email: string;
  recipient_name?: string;
  client?: number | null;
  template?: number | null;
  subject: string;
  body_html: string;
  send_at?: string;
  obligation_ids?: number[];
  client_ids?: number[];
}

// Email Automation Rule
export type EmailTrigger = 'on_complete' | 'before_deadline' | 'on_overdue' | 'manual';
export type EmailTiming = 'immediate' | 'delay_1h' | 'delay_24h' | 'scheduled';

export interface EmailAutomationRule {
  id: number;
  name: string;
  description?: string;
  trigger: EmailTrigger;
  trigger_display?: string;
  filter_obligation_types?: number[];
  filter_obligation_types_data?: ObligationTypeData[];
  filter_types_count?: number;
  template: number;
  template_name?: string;
  timing: EmailTiming;
  timing_display?: string;
  days_before_deadline?: number | null;
  scheduled_time?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmailAutomationRuleFormData {
  name: string;
  description?: string;
  trigger: EmailTrigger;
  filter_obligation_types?: number[];
  template: number;
  timing: EmailTiming;
  days_before_deadline?: number | null;
  scheduled_time?: string | null;
  is_active?: boolean;
}

// Send Email
export interface SendEmailData {
  to: string[];
  subject: string;
  body: string;
  template_id?: number | null;
  client_id?: number | null;
  obligation_id?: number | null;
}

export interface SendBulkEmailData {
  client_ids: number[];
  template_id: number;
  schedule_at?: string | null;
  variables?: Record<string, string>;
}

export interface PreviewEmailData {
  template_id: number;
  client_id?: number | null;
  obligation_id?: number | null;
  variables?: Record<string, string>;
}

export interface EmailPreviewResult {
  subject: string;
  body: string;
  recipient: string;
  recipient_name: string;
}

export interface SendEmailResult {
  message: string;
  results: {
    sent: number;
    failed: number;
    scheduled?: number;
    skipped?: number;
    details: Array<{
      email?: string;
      client?: string;
      status: 'sent' | 'failed' | 'scheduled' | 'skipped';
      message: string;
    }>;
  };
}

// Email filters
export interface EmailLogFilters {
  client?: number;
  status?: EmailLogStatus;
  date_from?: string;
  date_to?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface ScheduledEmailFilters {
  status?: ScheduledEmailStatus;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
}
