import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type {
  EmailTemplate,
  EmailTemplateFormData,
  EmailLog,
  EmailLogFilters,
  ScheduledEmail,
  ScheduledEmailFilters,
  ScheduledEmailFormData,
  EmailAutomationRule,
  EmailAutomationRuleFormData,
  SendEmailData,
  SendBulkEmailData,
  PreviewEmailData,
  EmailPreviewResult,
  SendEmailResult,
  EmailVariable,
  PaginatedResponse,
} from '../types';

// Query keys
const EMAIL_TEMPLATES_KEY = 'email-templates';
const SCHEDULED_EMAILS_KEY = 'scheduled-emails';
const EMAIL_AUTOMATIONS_KEY = 'email-automations';
const EMAIL_LOGS_KEY = 'email-logs';
const EMAIL_VARIABLES_KEY = 'email-variables';

// ============================================
// EMAIL TEMPLATES HOOKS
// ============================================

interface EmailTemplateParams {
  is_active?: boolean;
  search?: string;
}

export function useEmailTemplates(params?: EmailTemplateParams) {
  return useQuery({
    queryKey: [EMAIL_TEMPLATES_KEY, params],
    queryFn: async () => {
      const response = await apiClient.get<EmailTemplate[]>('/api/v1/email-templates/', {
        params,
      });
      return response.data;
    },
  });
}

export function useEmailTemplate(id: number) {
  return useQuery({
    queryKey: [EMAIL_TEMPLATES_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<EmailTemplate>(`/api/v1/email-templates/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateEmailTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: EmailTemplateFormData) => {
      const response = await apiClient.post<EmailTemplate>('/api/v1/email-templates/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_TEMPLATES_KEY] });
    },
  });
}

export function useUpdateEmailTemplate(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<EmailTemplateFormData>) => {
      const response = await apiClient.patch<EmailTemplate>(`/api/v1/email-templates/${id}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_TEMPLATES_KEY] });
    },
  });
}

export function useDeleteEmailTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/v1/email-templates/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_TEMPLATES_KEY] });
    },
  });
}

export function useDuplicateEmailTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await apiClient.post<{ message: string; template: EmailTemplate }>(
        `/api/v1/email-templates/${id}/duplicate/`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_TEMPLATES_KEY] });
    },
  });
}

export function useEmailVariables() {
  return useQuery({
    queryKey: [EMAIL_VARIABLES_KEY],
    queryFn: async () => {
      const response = await apiClient.get<{ variables: EmailVariable[] }>(
        '/api/v1/email-templates/variables/'
      );
      return response.data.variables;
    },
    staleTime: 60 * 60 * 1000, // Cache for 1 hour
  });
}

export function usePreviewEmailTemplate(id: number) {
  return useMutation({
    mutationFn: async (data: { client_id?: number; obligation_id?: number }) => {
      const response = await apiClient.post<EmailPreviewResult>(
        `/api/v1/email-templates/${id}/preview/`,
        data
      );
      return response.data;
    },
  });
}

// ============================================
// SCHEDULED EMAILS HOOKS
// ============================================

export function useScheduledEmails(filters?: ScheduledEmailFilters) {
  return useQuery({
    queryKey: [SCHEDULED_EMAILS_KEY, filters],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedResponse<ScheduledEmail>>(
        '/api/v1/scheduled-emails/',
        { params: filters }
      );
      return response.data;
    },
  });
}

export function useScheduledEmail(id: number) {
  return useQuery({
    queryKey: [SCHEDULED_EMAILS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<ScheduledEmail>(`/api/v1/scheduled-emails/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateScheduledEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ScheduledEmailFormData) => {
      const response = await apiClient.post<ScheduledEmail>('/api/v1/scheduled-emails/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULED_EMAILS_KEY] });
    },
  });
}

export function useCancelScheduledEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await apiClient.delete<{ message: string; id: number }>(
        `/api/v1/scheduled-emails/${id}/`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULED_EMAILS_KEY] });
    },
  });
}

export function useSendScheduledNow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await apiClient.post<{ message: string; email: ScheduledEmail }>(
        `/api/v1/scheduled-emails/${id}/send-now/`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULED_EMAILS_KEY] });
      queryClient.invalidateQueries({ queryKey: [EMAIL_LOGS_KEY] });
    },
  });
}

// ============================================
// EMAIL AUTOMATION RULES HOOKS
// ============================================

export function useEmailAutomations() {
  return useQuery({
    queryKey: [EMAIL_AUTOMATIONS_KEY],
    queryFn: async () => {
      const response = await apiClient.get<EmailAutomationRule[]>('/api/v1/email-automations/');
      return response.data;
    },
  });
}

export function useEmailAutomation(id: number) {
  return useQuery({
    queryKey: [EMAIL_AUTOMATIONS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<EmailAutomationRule>(`/api/v1/email-automations/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateEmailAutomation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: EmailAutomationRuleFormData) => {
      const response = await apiClient.post<EmailAutomationRule>('/api/v1/email-automations/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_AUTOMATIONS_KEY] });
    },
  });
}

export function useUpdateEmailAutomation(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<EmailAutomationRuleFormData>) => {
      const response = await apiClient.patch<EmailAutomationRule>(
        `/api/v1/email-automations/${id}/`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_AUTOMATIONS_KEY] });
    },
  });
}

export function useDeleteEmailAutomation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/v1/email-automations/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_AUTOMATIONS_KEY] });
    },
  });
}

export function useToggleEmailAutomation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await apiClient.post<{ message: string; rule: EmailAutomationRule }>(
        `/api/v1/email-automations/${id}/toggle/`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_AUTOMATIONS_KEY] });
    },
  });
}

// ============================================
// EMAIL LOGS HOOKS
// ============================================

export function useEmailLogs(filters?: EmailLogFilters) {
  return useQuery({
    queryKey: [EMAIL_LOGS_KEY, filters],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedResponse<EmailLog>>('/api/v1/email-logs/', {
        params: filters,
      });
      return response.data;
    },
  });
}

export function useEmailLog(id: number) {
  return useQuery({
    queryKey: [EMAIL_LOGS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<EmailLog>(`/api/v1/email-logs/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}

// ============================================
// EMAIL ACTIONS HOOKS
// ============================================

export function useSendEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: SendEmailData) => {
      const response = await apiClient.post<SendEmailResult>('/api/v1/emails/send/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_LOGS_KEY] });
    },
  });
}

export function useSendBulkEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: SendBulkEmailData) => {
      const response = await apiClient.post<SendEmailResult>('/api/v1/emails/send-bulk/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMAIL_LOGS_KEY] });
      queryClient.invalidateQueries({ queryKey: [SCHEDULED_EMAILS_KEY] });
    },
  });
}

export function usePreviewEmail() {
  return useMutation({
    mutationFn: async (data: PreviewEmailData) => {
      const response = await apiClient.post<EmailPreviewResult>('/api/v1/emails/preview/', data);
      return response.data;
    },
  });
}
