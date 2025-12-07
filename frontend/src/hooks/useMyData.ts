import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';

// =============================================================================
// TYPES
// =============================================================================

export interface MyDataClient {
  id: number;
  afm: string;
  company_name?: string;
  eponimia?: string;
}

export interface VATCategoryBreakdown {
  vat_category: number;
  vat_rate: number;
  vat_rate_display: string;
  net_value: string;
  vat_amount: string;
  count: number;
}

export interface VATPeriodSummary {
  year: number;
  month: number;
  income_net: string;
  income_vat: string;
  income_gross: string;
  income_count: number;
  expense_net: string;
  expense_vat: string;
  expense_gross: string;
  expense_count: number;
  net_difference: string;
  vat_difference: string;
}

export interface ClientVATDetail {
  client: {
    afm: string;
    name: string;
  };
  credentials: {
    has_credentials: boolean;
    is_verified: boolean;
    last_sync: string | null;
  };
  period: {
    year: number;
    month: number;
  };
  summary: VATPeriodSummary;
  income_by_category: VATCategoryBreakdown[];
  expense_by_category: VATCategoryBreakdown[];
}

export interface MyDataCredentials {
  id: number;
  client: number;
  client_name?: string;
  client_afm?: string;
  is_sandbox: boolean;
  is_active: boolean;
  is_verified: boolean;
  has_credentials: boolean;
  last_sync_at: string | null;
  last_vat_sync_at: string | null;
}

export interface TrendDataPoint {
  year: number;
  month: number;
  month_name: string;
  income_net: string;
  income_vat: string;
  income_count: number;
  expense_net: string;
  expense_vat: string;
  expense_count: number;
  vat_balance: string;
}

export interface TrendData {
  afm: string | null;
  months_count: number;
  data: TrendDataPoint[];
}

export interface DashboardOverview {
  period: {
    year: number;
    month: number;
  };
  overview: {
    total_clients: number;
    clients_with_credentials: number;
    verified_credentials: number;
    total_income_net: string;
    total_income_vat: string;
    total_expense_net: string;
    total_expense_vat: string;
  };
  clients: Array<{
    client_afm: string;
    client_name: string;
    has_credentials: boolean;
    is_verified: boolean;
    last_sync: string | null;
    current_period: VATPeriodSummary;
  }>;
}

export interface SyncResult {
  success: boolean;
  message?: string;
  error?: string;
  vat_result?: string;
  records_synced?: number;
}

// =============================================================================
// QUERY KEYS
// =============================================================================

const MYDATA_KEY = 'mydata';

// =============================================================================
// HOOKS
// =============================================================================

/**
 * Get list of clients with myDATA credentials
 */
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export function useMyDataClients() {
  return useQuery({
    queryKey: [MYDATA_KEY, 'clients'],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedResponse<MyDataCredentials> | MyDataCredentials[]>('/api/mydata/credentials/');
      // Handle both paginated and non-paginated responses
      if (Array.isArray(response.data)) {
        return response.data;
      }
      return response.data.results || [];
    },
    staleTime: 60000, // 1 minute
  });
}

/**
 * Get VAT detail for a specific client and period
 */
export function useClientVATDetail(afm: string | null, year?: number, month?: number) {
  return useQuery({
    queryKey: [MYDATA_KEY, 'client', afm, year, month],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (year) params.append('year', year.toString());
      if (month) params.append('month', month.toString());

      const url = params.toString()
        ? `/api/mydata/client/${afm}/?${params.toString()}`
        : `/api/mydata/client/${afm}/`;

      const response = await apiClient.get<ClientVATDetail>(url);
      return response.data;
    },
    enabled: !!afm,
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Get period summary for a client
 */
export function useVATSummary(afm: string | null, year?: number, month?: number) {
  return useQuery({
    queryKey: [MYDATA_KEY, 'summary', afm, year, month],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (afm) params.append('afm', afm);
      if (year) params.append('year', year.toString());
      if (month) params.append('month', month.toString());

      const response = await apiClient.get<VATPeriodSummary>(`/api/mydata/records/summary/?${params.toString()}`);
      return response.data;
    },
    enabled: !!afm,
    staleTime: 30000,
  });
}

/**
 * Get monthly trend data
 */
export function useVATTrend(afm?: string, monthsCount = 6) {
  return useQuery({
    queryKey: [MYDATA_KEY, 'trend', afm, monthsCount],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (afm) params.append('afm', afm);
      params.append('months', monthsCount.toString());

      const response = await apiClient.get<TrendData>(`/api/mydata/trend/?${params.toString()}`);
      return response.data;
    },
    staleTime: 60000,
  });
}

/**
 * Get dashboard overview
 */
export function useMyDataDashboard(year?: number, month?: number) {
  return useQuery({
    queryKey: [MYDATA_KEY, 'dashboard', year, month],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (year) params.append('year', year.toString());
      if (month) params.append('month', month.toString());

      const url = params.toString()
        ? `/api/mydata/dashboard/?${params.toString()}`
        : '/api/mydata/dashboard/';

      const response = await apiClient.get<DashboardOverview>(url);
      return response.data;
    },
    staleTime: 30000,
  });
}

/**
 * Sync VAT data mutation
 */
export function useSyncVAT() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ credentialsId, year, month, days }: {
      credentialsId: number;
      year?: number;
      month?: number;
      days?: number;
    }) => {
      const response = await apiClient.post<SyncResult>(`/api/mydata/credentials/${credentialsId}/sync/`, {
        year,
        month,
        days: days || 30,
      });
      return response.data;
    },
    onSuccess: () => {
      // Invalidate all mydata queries to refresh data
      queryClient.invalidateQueries({ queryKey: [MYDATA_KEY] });
    },
  });
}

/**
 * Verify credentials mutation
 */
export function useVerifyCredentials() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (credentialsId: number) => {
      const response = await apiClient.post<{ success: boolean; is_verified: boolean; error?: string }>(
        `/api/mydata/credentials/${credentialsId}/verify/`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [MYDATA_KEY, 'clients'] });
    },
  });
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Format currency amount in Greek locale
 */
export function formatCurrency(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined) return '—';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return '—';

  return new Intl.NumberFormat('el-GR', {
    style: 'currency',
    currency: 'EUR',
    signDisplay: 'auto',
  }).format(num);
}

/**
 * Format VAT result with sign
 */
export function formatVATResult(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined) return '—';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return '—';

  return new Intl.NumberFormat('el-GR', {
    style: 'currency',
    currency: 'EUR',
    signDisplay: 'always',
  }).format(num);
}

/**
 * Get result color class based on amount
 */
export function getVATResultColor(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined) return 'text-gray-400';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return 'text-gray-400';

  if (num > 0) return 'text-red-600';   // Χρωστάω
  if (num < 0) return 'text-green-600'; // Επιστροφή
  return 'text-gray-600';
}

/**
 * Get result background class based on amount
 */
export function getVATResultBg(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined) return 'bg-gray-50 border-gray-200';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return 'bg-gray-50 border-gray-200';

  if (num > 0) return 'bg-red-50 border-red-200';
  if (num < 0) return 'bg-green-50 border-green-200';
  return 'bg-gray-50 border-gray-200';
}

/**
 * Get result label based on amount
 */
export function getVATResultLabel(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined) return 'Δεν υπάρχουν δεδομένα';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return 'Δεν υπάρχουν δεδομένα';

  if (num > 0) return 'ΦΠΑ για Καταβολή';
  if (num < 0) return 'ΦΠΑ προς Επιστροφή';
  return 'Μηδενικό Υπόλοιπο';
}

/**
 * Greek month names
 */
export const GREEK_MONTHS = [
  'Ιανουάριος', 'Φεβρουάριος', 'Μάρτιος', 'Απρίλιος',
  'Μάιος', 'Ιούνιος', 'Ιούλιος', 'Αύγουστος',
  'Σεπτέμβριος', 'Οκτώβριος', 'Νοέμβριος', 'Δεκέμβριος'
];

/**
 * Get month name in Greek
 */
export function getMonthName(month: number): string {
  return GREEK_MONTHS[month - 1] || '';
}
