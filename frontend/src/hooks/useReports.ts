import { useQuery, useMutation } from '@tanstack/react-query';
import { useState, useCallback } from 'react';
import apiClient from '../api/client';

export type ReportPeriod = 'today' | 'week' | 'month' | 'quarter' | 'year' | 'all';
export type ExportType = 'clients' | 'obligations' | 'financial' | 'performance';
export type ExportFormat = 'csv' | 'xlsx' | 'pdf';

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

export type ExportType = 'clients' | 'obligations' | 'financial' | 'performance' | 'vat_summary' | 'client_statement';
export type ExportFormat = 'csv' | 'xlsx' | 'pdf';

interface DownloadExportParams {
  type: ExportType;
  format?: ExportFormat;
  period?: ReportPeriod;
  clientId?: number;
  year?: number;
  month?: number;
}

/**
 * Download a report export file
 * Triggers browser download of the generated file
 */
export async function downloadReportExport({
  type,
  format = 'xlsx',
  period = 'month',
  clientId,
  year,
  month,
}: DownloadExportParams): Promise<void> {
  const params = new URLSearchParams({
    type,
    format,
    period,
    download: 'true',
  });

  if (clientId) params.append('client_id', clientId.toString());
  if (year) params.append('year', year.toString());
  if (month) params.append('month', month.toString());

  const response = await apiClient.get(`/api/reports/export/?${params.toString()}`, {
    responseType: 'blob',
  });

  // Extract filename from Content-Disposition header or generate one
  const contentDisposition = response.headers['content-disposition'];
  let filename = `${type}_report.${format}`;

  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1].replace(/['"]/g, '');
    }
  }

  // Create blob and trigger download
  const blob = new Blob([response.data], {
    type: response.headers['content-type'] || 'application/octet-stream',
  });

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
