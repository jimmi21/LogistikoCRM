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
      // Build form data if file is included
      if (data.file) {
        const formData = new FormData();
        formData.append('file', data.file);
        if (data.send_email !== undefined) {
          formData.append('send_email', String(data.send_email));
        }
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
      }

      // Regular JSON request
      const response = await apiClient.post(
        `/api/v1/obligations/${obligationId}/complete-and-notify/`,
        {
          document_id: data.document_id,
          send_email: data.send_email,
          email_template_id: data.email_template_id,
          notes: data.notes,
          time_spent: data.time_spent,
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
