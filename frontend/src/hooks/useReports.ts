import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';

export type ReportPeriod = 'today' | 'week' | 'month' | 'quarter' | 'year' | 'all';

interface ObligationByType {
  obligation_type__name: string;
  obligation_type__code: string;
  count: number;
}

interface MonthlyActivity {
  month: string;
  month_num: number;
  year: number;
  count: number;
}

interface Comparison {
  clients_change: number;
  completed_change: number;
}

interface ReportsStats {
  period: ReportPeriod;
  total_clients: number;
  completed_obligations: number;
  pending_obligations: number;
  overdue_obligations: number;
  obligations_by_type: ObligationByType[];
  monthly_activity: MonthlyActivity[];
  completion_rate: number;
  comparison: Comparison;
  generated_at: string;
}

interface ExportInfo {
  name: string;
  type: string;
  description: string;
  formats: string[];
}

interface ReportsExport {
  available_exports: ExportInfo[];
  current_request: {
    type: string;
    format: string;
    period: string;
  };
}

const REPORTS_KEY = 'reports';

export function useReportsStats(period: ReportPeriod = 'month') {
  return useQuery({
    queryKey: [REPORTS_KEY, 'stats', period],
    queryFn: async () => {
      const response = await apiClient.get<ReportsStats>(`/api/reports/stats/?period=${period}`);
      return response.data;
    },
    staleTime: 30000, // 30 seconds
    retry: 1,
  });
}

export function useReportsExport() {
  return useQuery({
    queryKey: [REPORTS_KEY, 'export'],
    queryFn: async () => {
      const response = await apiClient.get<ReportsExport>('/api/reports/export/');
      return response.data;
    },
    staleTime: 60000, // 1 minute
  });
}
