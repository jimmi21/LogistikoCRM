/**
 * useEmail.ts
 * Hook for email management - templates, send, obligation notifications
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type {
  EmailTemplate,
  EmailPreview,
  SendEmailRequest,
  SendObligationNoticeRequest,
  CompleteAndNotifyRequest,
  BulkCompleteNotifyRequest,
  EmailSendResult,
  BulkCompleteNotifyResult,
  EmailLog,
  PaginatedResponse,
  Obligation,
} from '../types';

const EMAIL_TEMPLATES_KEY = 'email-templates';
const EMAIL_HISTORY_KEY = 'email-history';

/**
 * Fetch all active email templates
 */
export function useEmailTemplates() {
  return useQuery({
    queryKey: [EMAIL_TEMPLATES_KEY],
    queryFn: async () => {
      const response = await apiClient.get<EmailTemplate[]>('/api/v1/email/templates/');
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });
}

/**
 * Fetch a single email template with variables info
 */
export function useEmailTemplate(templateId: number) {
  return useQuery({
    queryKey: [EMAIL_TEMPLATES_KEY, templateId],
    queryFn: async () => {
      const response = await apiClient.get<
        EmailTemplate & { available_variables: Array<[string, string]> }
      >(`/api/v1/email/templates/${templateId}/`);
      return response.data;
    },
    enabled: !!templateId,
  });
}

/**
 * Preview an email with template and context
 */
export function usePreviewEmail() {
  return useMutation({
    mutationFn: async ({
      templateId,
      obligationId,
      clientId,
    }: {
      templateId: number;
      obligationId?: number;
      clientId?: number;
    }): Promise<EmailPreview> => {
      const response = await apiClient.post<EmailPreview>('/api/v1/email/preview/', {
        template_id: templateId,
        obligation_id: obligationId,
        client_id: clientId,
      });
      return response.data;
    },
  });
}

/**
 * Send an email to a client
 */
export function useSendEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: SendEmailRequest): Promise<EmailSendResult> => {
      const response = await apiClient.post<EmailSendResult>('/api/v1/email/send/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_HISTORY_KEY] });
    },
  });
}

/**
 * Send an obligation notice (reminder, completion, overdue)
 */
export function useSendObligationNotice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: SendObligationNoticeRequest): Promise<EmailSendResult> => {
      const response = await apiClient.post<EmailSendResult>(
        '/api/v1/email/send-obligation-notice/',
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_HISTORY_KEY] });
    },
  });
}

/**
 * Complete an obligation and optionally send notification
 */
export function useCompleteAndNotify() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      obligationId,
      data,
    }: {
      obligationId: number;
      data: CompleteAndNotifyRequest;
    }): Promise<{
      success: boolean;
      message: string;
      obligation: Obligation;
      document?: unknown;
      email_sent?: boolean;
      email_error?: string;
    }> => {
      const formData = new FormData();

      // Add file if included
      if (data.file) {
        formData.append('file', data.file);
      }

      // Add document_id if provided
      if (data.document_id) {
        formData.append('document_id', String(data.document_id));
      }

      // Add boolean flags
      formData.append('save_to_client_folder', String(data.save_to_client_folder ?? true));
      formData.append('send_email', String(data.send_email ?? false));
      formData.append('attach_to_email', String(data.attach_to_email ?? false));

      // Add optional fields
      if (data.email_template_id) {
        formData.append('email_template_id', String(data.email_template_id));
      }
      if (data.notes) {
        formData.append('notes', data.notes);
      }
      if (data.time_spent) {
        formData.append('time_spent', String(data.time_spent));
      }

      const response = await apiClient.post(
        `/api/v1/obligations/${obligationId}/complete-and-notify/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['obligations'] });
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: [EMAIL_HISTORY_KEY] });
    },
  });
}

/**
 * Bulk complete obligations with optional notifications
 */
export function useBulkCompleteWithNotify() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: BulkCompleteNotifyRequest): Promise<BulkCompleteNotifyResult> => {
      const response = await apiClient.post<BulkCompleteNotifyResult>(
        '/api/v1/obligations/bulk-complete-notify/',
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['obligations'] });
      queryClient.invalidateQueries({ queryKey: [EMAIL_HISTORY_KEY] });
    },
  });
}

/**
 * Bulk complete obligations with individual documents
 */
export interface BulkCompleteWithDocumentsRequest {
  obligationIds: number[];
  obligationFiles: { [key: number]: File | null };
  saveToClientFolders: boolean;
  sendEmails: boolean;
  attachToEmails: boolean;
  templateId?: number | null;
}

export interface BulkCompleteWithDocumentsResult {
  success: boolean;
  message: string;
  completed_count: number;
  results: Array<{
    obligation_id: number;
    client: string;
    document_id: number | null;
    email_sent: boolean;
  }>;
  email_results?: {
    sent: number;
    failed: number;
    skipped: number;
    details: Array<{
      obligation_id: number;
      client: string;
      status: 'sent' | 'failed' | 'skipped';
      message: string;
    }>;
  };
}

export function useBulkCompleteWithDocuments() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (
      data: BulkCompleteWithDocumentsRequest
    ): Promise<BulkCompleteWithDocumentsResult> => {
      const formData = new FormData();

      // Add obligation IDs as JSON array (from explicit list, not just files)
      formData.append('obligation_ids', JSON.stringify(data.obligationIds));

      // Add individual files for each obligation
      for (const [obligationId, file] of Object.entries(data.obligationFiles)) {
        if (file) {
          formData.append(`file_${obligationId}`, file);
        }
      }

      // Add options
      formData.append('save_to_folders', String(data.saveToClientFolders));
      formData.append('send_emails', String(data.sendEmails));
      formData.append('attach_to_emails', String(data.attachToEmails));
      if (data.templateId) {
        formData.append('template_id', String(data.templateId));
      }

      const response = await apiClient.post<BulkCompleteWithDocumentsResult>(
        '/api/v1/obligations/bulk-complete-with-documents/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['obligations'] });
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: [EMAIL_HISTORY_KEY] });
    },
  });
}

/**
 * Fetch email history with filters
 */
export function useEmailHistory(filters?: {
  client_id?: number;
  obligation_id?: number;
  status?: 'sent' | 'failed' | 'pending';
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: [EMAIL_HISTORY_KEY, filters],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedResponse<EmailLog>>(
        '/api/v1/email/history/',
        { params: filters }
      );
      return response.data;
    },
  });
}

// ============================================
// EMAIL TEMPLATE CRUD OPERATIONS
// ============================================

export interface EmailTemplateFormData {
  name: string;
  description?: string;
  subject: string;
  body_html: string;
  obligation_type?: number | null;
  is_active?: boolean;
}

/**
 * Create a new email template
 */
export function useCreateEmailTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: EmailTemplateFormData): Promise<EmailTemplate> => {
      const response = await apiClient.post<EmailTemplate>(
        '/api/v1/email/templates/',
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_TEMPLATES_KEY] });
    },
  });
}

/**
 * Update an existing email template
 */
export function useUpdateEmailTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: number;
      data: Partial<EmailTemplateFormData>;
    }): Promise<EmailTemplate> => {
      const response = await apiClient.put<EmailTemplate>(
        `/api/v1/email/templates/${id}/`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_TEMPLATES_KEY] });
    },
  });
}

/**
 * Delete an email template
 */
export function useDeleteEmailTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      await apiClient.delete(`api/v1/email/templates/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_TEMPLATES_KEY] });
    },
  });
}

// ============================================
// EMAIL SETTINGS OPERATIONS
// ============================================

const EMAIL_SETTINGS_KEY = 'email-settings';

export interface EmailSettingsData {
  id: number;
  smtp_host: string;
  smtp_port: number;
  smtp_username: string;
  smtp_password?: string; // Write-only
  has_password: boolean;
  smtp_security: 'tls' | 'ssl' | 'none';
  from_email: string;
  from_name: string;
  reply_to: string;
  company_name: string;
  company_phone: string;
  company_website: string;
  accountant_name: string;
  accountant_title: string;
  email_signature: string;
  rate_limit: number;
  burst_limit: number;
  is_active: boolean;
  last_test_at: string | null;
  last_test_success: boolean | null;
  last_test_error: string;
  created_at: string;
  updated_at: string;
}

export interface EmailSettingsUpdateData {
  smtp_host?: string;
  smtp_port?: number;
  smtp_username?: string;
  smtp_password?: string;
  smtp_security?: 'tls' | 'ssl' | 'none';
  from_email?: string;
  from_name?: string;
  reply_to?: string;
  company_name?: string;
  company_phone?: string;
  company_website?: string;
  accountant_name?: string;
  accountant_title?: string;
  email_signature?: string;
  rate_limit?: number;
  burst_limit?: number;
  is_active?: boolean;
}

/**
 * Fetch email settings
 */
export function useEmailSettings() {
  return useQuery({
    queryKey: [EMAIL_SETTINGS_KEY],
    queryFn: async () => {
      const response = await apiClient.get<EmailSettingsData>('/api/v1/email/settings/');
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });
}

/**
 * Update email settings
 */
export function useUpdateEmailSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: EmailSettingsUpdateData): Promise<EmailSettingsData> => {
      const response = await apiClient.put<EmailSettingsData>(
        '/api/v1/email/settings/',
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_SETTINGS_KEY] });
    },
  });
}

/**
 * Test SMTP connection
 */
export function useTestEmailConnection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data?: EmailSettingsUpdateData): Promise<{
      success: boolean;
      message: string;
      last_test_at: string;
    }> => {
      const response = await apiClient.post('/api/v1/email/settings/test/', data || {});
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_SETTINGS_KEY] });
    },
  });
}

/**
 * Send test email
 */
export function useSendTestEmail() {
  return useMutation({
    mutationFn: async (recipientEmail: string): Promise<{
      success: boolean;
      message: string;
    }> => {
      const response = await apiClient.post('/api/v1/email/settings/send-test/', {
        recipient_email: recipientEmail,
      });
      return response.data;
    },
  });
}
