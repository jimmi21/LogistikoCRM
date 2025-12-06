import { useState, useMemo } from 'react';
import {
  useObligations,
  useCreateObligation,
  useDeleteObligation,
  useObligationTypes,
  useBulkCreateObligations,
  useBulkUpdateObligations,
  useBulkDeleteObligations,
  exportObligationsToExcel,
  useGenerateMonthlyObligations,
} from '../hooks/useObligations';
import { useCompleteAndNotify, useBulkCompleteWithNotify, useSendObligationNotice } from '../hooks/useEmail';
import { useUploadToObligation } from '../hooks/useDocuments';
import type { GenerateMonthResult, Client } from '../types';
import { useClients } from '../hooks/useClients';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import { Modal, ConfirmDialog, ObligationForm, Button } from '../components';
import { DocumentUploadModal } from '../components/DocumentUploadModal';
import { SendEmailModal } from '../components/SendEmailModal';
import { CompleteObligationModal } from '../components/CompleteObligationModal';
import {
  FileText, AlertCircle, RefreshCw, Filter, Plus, Edit2, Trash2,
  Download, CheckSquare, Square, Users, Calendar, CalendarPlus, CheckCircle, X,
  Paperclip, Mail
} from 'lucide-react';
import type { Obligation, ObligationFormData, ObligationStatus, BulkObligationFormData } from '../types';

// Greek labels for obligation statuses
const STATUS_LABELS: Record<ObligationStatus, string> = {
  pending: 'Εκκρεμεί',
  in_progress: 'Σε εξέλιξη',
  completed: 'Ολοκληρώθηκε',
  overdue: 'Εκπρόθεσμη',
  cancelled: 'Ακυρώθηκε',
};

// Status badge colors
const STATUS_COLORS: Record<ObligationStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-800',
};

const MONTHS = [
  { value: 1, label: 'Ιανουάριος' },
  { value: 2, label: 'Φεβρουάριος' },
  { value: 3, label: 'Μάρτιος' },
  { value: 4, label: 'Απρίλιος' },
  { value: 5, label: 'Μάιος' },
  { value: 6, label: 'Ιούνιος' },
  { value: 7, label: 'Ιούλιος' },
  { value: 8, label: 'Αύγουστος' },
  { value: 9, label: 'Σεπτέμβριος' },
  { value: 10, label: 'Οκτώβριος' },
  { value: 11, label: 'Νοέμβριος' },
  { value: 12, label: 'Δεκέμβριος' },
];

const currentYear = new Date().getFullYear();
const YEARS = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i);

interface Filters {
  status: string;
  client: number | null;
  type: string;
  month: number | null;
  year: number | null;
  deadline_from: string;
  deadline_to: string;
}

export default function Obligations() {
  const [page, setPage] = useState(1);
  const pageSize = 100;

  // Filters state
  const [filters, setFilters] = useState<Filters>({
    status: 'all',
    client: null,
    type: '',
    month: null,
    year: null,
    deadline_from: '',
    deadline_to: '',
  });
  const [showFilters, setShowFilters] = useState(false);

  // Selection state for bulk operations
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [selectAll, setSelectAll] = useState(false);

  // Modal state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isBulkCreateModalOpen, setIsBulkCreateModalOpen] = useState(false);
  const [isBulkDeleteDialogOpen, setIsBulkDeleteDialogOpen] = useState(false);
  const [isGenerateMonthModalOpen, setIsGenerateMonthModalOpen] = useState(false);
  const [generateResult, setGenerateResult] = useState<GenerateMonthResult | null>(null);
  const [selectedObligation, setSelectedObligation] = useState<Obligation | null>(null);

  // New modal states for complete, upload, email
  const [isCompleteModalOpen, setIsCompleteModalOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);
  const [isBulkCompleteNotifyDialogOpen, setIsBulkCompleteNotifyDialogOpen] = useState(false);

  // Bulk create form state
  const [bulkCreateForm, setBulkCreateForm] = useState<BulkObligationFormData>({
    client_ids: [],
    obligation_type: 0,
    month: new Date().getMonth() + 1,
    year: currentYear,
  });

  // Build query params
  const queryParams = useMemo(() => {
    const params: Record<string, string | number> = { page, page_size: pageSize };
    if (filters.status !== 'all') params.status = filters.status;
    if (filters.client) params.client = filters.client;
    if (filters.type) params.type = filters.type;
    if (filters.month) params.month = filters.month;
    if (filters.year) params.year = filters.year;
    if (filters.deadline_from) params.deadline_from = filters.deadline_from;
    if (filters.deadline_to) params.deadline_to = filters.deadline_to;
    return params;
  }, [page, pageSize, filters]);

  const { data, isLoading, isError, error, refetch } = useObligations(queryParams);
  const { data: clientsData } = useClients({ page_size: 1000 });
  const { data: obligationTypes } = useObligationTypes();
  const createMutation = useCreateObligation();
  const deleteMutation = useDeleteObligation();
  const bulkCreateMutation = useBulkCreateObligations();
  const bulkUpdateMutation = useBulkUpdateObligations();
  const bulkDeleteMutation = useBulkDeleteObligations();
  const generateMonthMutation = useGenerateMonthlyObligations();
  const completeAndNotifyMutation = useCompleteAndNotify();
  const bulkCompleteNotifyMutation = useBulkCompleteWithNotify();
  const sendObligationNoticeMutation = useSendObligationNotice();
  const uploadToObligationMutation = useUploadToObligation();
  const queryClient = useQueryClient();

  // Update obligation mutation
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<ObligationFormData> }) => {
      const response = await apiClient.patch<Obligation>(`/api/v1/obligations/${id}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['obligations'] });
    },
  });

  const obligations = data?.results || [];
  const clients = clientsData?.results || [];

  // Format date for display
  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '-';
    return date.toLocaleDateString('el-GR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  // Selection handlers
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(obligations.map((o) => o.id)));
    }
    setSelectAll(!selectAll);
  };

  const handleSelectOne = (id: number) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
    setSelectAll(newSelected.size === obligations.length);
  };

  // CRUD handlers
  const handleCreate = (formData: ObligationFormData) => {
    createMutation.mutate(formData, {
      onSuccess: () => {
        setIsCreateModalOpen(false);
        // invalidateQueries in hook triggers automatic refetch
      },
    });
  };

  const handleEdit = (obligation: Obligation) => {
    setSelectedObligation(obligation);
    setIsEditModalOpen(true);
  };

  const handleUpdate = (formData: ObligationFormData) => {
    if (!selectedObligation) return;
    updateMutation.mutate(
      { id: selectedObligation.id, data: formData },
      {
        onSuccess: () => {
          setIsEditModalOpen(false);
          setSelectedObligation(null);
          // invalidateQueries in hook triggers automatic refetch
        },
      }
    );
  };

  const handleDeleteClick = (obligation: Obligation) => {
    setSelectedObligation(obligation);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (!selectedObligation) return;
    deleteMutation.mutate(selectedObligation.id, {
      onSuccess: () => {
        setIsDeleteDialogOpen(false);
        setSelectedObligation(null);
        // invalidateQueries in hook triggers automatic refetch
      },
    });
  };

  // Bulk operations handlers
  const handleBulkCreate = () => {
    if (bulkCreateForm.client_ids.length === 0 || !bulkCreateForm.obligation_type) return;

    bulkCreateMutation.mutate(bulkCreateForm, {
      onSuccess: () => {
        setIsBulkCreateModalOpen(false);
        setBulkCreateForm({
          client_ids: [],
          obligation_type: 0,
          month: new Date().getMonth() + 1,
          year: currentYear,
        });
        // invalidateQueries in hook triggers automatic refetch
      },
    });
  };

  const handleBulkComplete = () => {
    if (selectedIds.size === 0) return;
    bulkUpdateMutation.mutate(
      { obligation_ids: Array.from(selectedIds), status: 'completed' },
      {
        onSuccess: () => {
          setSelectedIds(new Set());
          setSelectAll(false);
          // invalidateQueries in hook triggers automatic refetch
        },
      }
    );
  };

  const handleBulkDeleteConfirm = () => {
    if (selectedIds.size === 0) return;
    bulkDeleteMutation.mutate(Array.from(selectedIds), {
      onSuccess: () => {
        setIsBulkDeleteDialogOpen(false);
        setSelectedIds(new Set());
        setSelectAll(false);
        // invalidateQueries in hook triggers automatic refetch
      },
    });
  };

  // New handlers for complete, upload, email
  const handleCompleteClick = (obligation: Obligation) => {
    setSelectedObligation(obligation);
    setIsCompleteModalOpen(true);
  };

  const handleUploadClick = (obligation: Obligation) => {
    setSelectedObligation(obligation);
    setIsUploadModalOpen(true);
  };

  const handleEmailClick = (obligation: Obligation) => {
    setSelectedObligation(obligation);
    setIsEmailModalOpen(true);
  };

  const handleCompleteAndNotify = async (data: {
    file?: File | null;
    documentId?: number | null;
    sendEmail: boolean;
    emailTemplateId?: number | null;
    notes: string;
    timeSpent?: number | null;
  }) => {
    if (!selectedObligation) return;
    await completeAndNotifyMutation.mutateAsync({
      obligationId: selectedObligation.id,
      data: {
        file: data.file,
        document_id: data.documentId,
        send_email: data.sendEmail,
        email_template_id: data.emailTemplateId,
        notes: data.notes,
        time_spent: data.timeSpent,
      },
    });
    setIsCompleteModalOpen(false);
    setSelectedObligation(null);
    // invalidateQueries in hook triggers automatic refetch
  };

  const handleUploadDocument = async (data: {
    file: File;
    category: string;
    description: string;
    sendEmail: boolean;
  }) => {
    if (!selectedObligation) return;
    await uploadToObligationMutation.mutateAsync({
      obligationId: selectedObligation.id,
      file: data.file,
      description: data.description,
    });
    if (data.sendEmail) {
      await sendObligationNoticeMutation.mutateAsync({
        obligation_id: selectedObligation.id,
        template_type: 'completion',
        include_attachment: true,
      });
    }
    setIsUploadModalOpen(false);
    setSelectedObligation(null);
    // invalidateQueries in hook triggers automatic refetch
  };

  const handleSendEmail = async (data: {
    subject: string;
    body: string;
    templateId?: number;
    attachmentIds: number[];
  }) => {
    if (!selectedObligation) return;
    const client = clients.find((c) => c.id === selectedObligation.client);
    if (!client?.email) return;

    await sendObligationNoticeMutation.mutateAsync({
      obligation_id: selectedObligation.id,
      template_type: 'completion',
      template_id: data.templateId,
      attachment_ids: data.attachmentIds,
    });
    setIsEmailModalOpen(false);
    setSelectedObligation(null);
  };

  const handleBulkCompleteWithNotify = async (sendNotifications: boolean) => {
    if (selectedIds.size === 0) return;
    await bulkCompleteNotifyMutation.mutateAsync({
      obligation_ids: Array.from(selectedIds),
      send_notifications: sendNotifications,
    });
    setIsBulkCompleteNotifyDialogOpen(false);
    setSelectedIds(new Set());
    setSelectAll(false);
    // invalidateQueries in hook triggers automatic refetch
  };

  // Helper to get client for selected obligation
  const getSelectedClient = (): Client | undefined => {
    if (!selectedObligation) return undefined;
    return clients.find((c) => c.id === selectedObligation.client);
  };

  // Export handler
  const [isExporting, setIsExporting] = useState(false);
  const handleExport = async () => {
    setIsExporting(true);
    try {
      await exportObligationsToExcel(queryParams);
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setIsExporting(false);
    }
  };

  // Filter handlers
  const handleFilterChange = <K extends keyof Filters>(key: K, value: Filters[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
    setSelectedIds(new Set());
    setSelectAll(false);
  };

  const resetFilters = () => {
    setFilters({
      status: 'all',
      client: null,
      type: '',
      month: null,
      year: null,
      deadline_from: '',
      deadline_to: '',
    });
    setPage(1);
  };

  // Bulk create client selection
  const toggleClientSelection = (clientId: number) => {
    const newIds = [...bulkCreateForm.client_ids];
    const idx = newIds.indexOf(clientId);
    if (idx > -1) {
      newIds.splice(idx, 1);
    } else {
      newIds.push(clientId);
    }
    setBulkCreateForm((prev) => ({ ...prev, client_ids: newIds }));
  };

  const selectAllClients = () => {
    const allIds = clients.map((c) => c.id);
    setBulkCreateForm((prev) => ({ ...prev, client_ids: allIds }));
  };

  const deselectAllClients = () => {
    setBulkCreateForm((prev) => ({ ...prev, client_ids: [] }));
  };

  const hasMore = data?.next !== null;
  const totalCount = data?.count || 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-yellow-100 rounded-lg">
            <FileText className="w-6 h-6 text-yellow-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Υποχρεώσεις</h1>
            <p className="text-sm text-gray-500">{totalCount} συνολικά</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="secondary" onClick={() => setIsGenerateMonthModalOpen(true)}>
            <CalendarPlus className="w-4 h-4 mr-2" />
            Δημιουργία Μήνα
          </Button>
          <Button variant="secondary" onClick={() => setIsBulkCreateModalOpen(true)}>
            <Users className="w-4 h-4 mr-2" />
            Μαζική Δημιουργία
          </Button>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Νέα Υποχρέωση
          </Button>
        </div>
      </div>

      {/* Filter Controls */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
          {/* Quick filters row */}
          <div className="flex items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center text-gray-600">
                <Filter className="w-5 h-5 mr-2" />
                <span className="font-medium">Κατάσταση:</span>
              </div>
              <div className="flex gap-2">
                {[
                  { value: 'all', label: 'Όλες', className: 'bg-gray-800 text-white' },
                  { value: 'pending', label: 'Εκκρεμείς', className: 'bg-yellow-500 text-white' },
                  { value: 'completed', label: 'Ολοκληρωμένες', className: 'bg-green-500 text-white' },
                  { value: 'overdue', label: 'Εκπρόθεσμες', className: 'bg-red-500 text-white' },
                ].map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => handleFilterChange('status', opt.value)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      filters.status === opt.value
                        ? opt.className
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                onClick={() => setShowFilters(!showFilters)}
                size="sm"
              >
                <Filter className="w-4 h-4 mr-1" />
                {showFilters ? 'Απόκρυψη' : 'Περισσότερα'}
              </Button>
              <Button variant="secondary" onClick={handleExport} isLoading={isExporting} size="sm">
                <Download className="w-4 h-4 mr-1" />
                Εξαγωγή Excel
              </Button>
            </div>
          </div>

          {/* Extended filters */}
          {showFilters && (
            <div className="border-t border-gray-200 pt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              {/* Client filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Πελάτης</label>
                <select
                  value={filters.client || ''}
                  onChange={(e) => handleFilterChange('client', e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="">Όλοι</option>
                  {clients.map((client) => (
                    <option key={client.id} value={client.id}>
                      {client.eponimia}
                    </option>
                  ))}
                </select>
              </div>

              {/* Type filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Τύπος</label>
                <select
                  value={filters.type}
                  onChange={(e) => handleFilterChange('type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="">Όλοι</option>
                  {obligationTypes?.map((type) => (
                    <option key={type.id} value={type.code}>
                      {type.code} - {type.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Month filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Μήνας</label>
                <select
                  value={filters.month || ''}
                  onChange={(e) => handleFilterChange('month', e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="">Όλοι</option>
                  {MONTHS.map((m) => (
                    <option key={m.value} value={m.value}>
                      {m.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Year filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Έτος</label>
                <select
                  value={filters.year || ''}
                  onChange={(e) => handleFilterChange('year', e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="">Όλα</option>
                  {YEARS.map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
              </div>

              {/* Deadline from */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Προθεσμία από</label>
                <input
                  type="date"
                  value={filters.deadline_from}
                  onChange={(e) => handleFilterChange('deadline_from', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>

              {/* Deadline to */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Προθεσμία έως</label>
                <input
                  type="date"
                  value={filters.deadline_to}
                  onChange={(e) => handleFilterChange('deadline_to', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>

              {/* Reset filters */}
              <div className="flex items-end col-span-2 md:col-span-2">
                <Button variant="secondary" onClick={resetFilters} size="sm">
                  Καθαρισμός Φίλτρων
                </Button>
              </div>
            </div>
          )}
        </div>

      {/* Bulk Actions Bar */}
      {selectedIds.size > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center justify-between">
            <span className="text-blue-800 font-medium">
              {selectedIds.size} επιλεγμένα
            </span>
            <div className="flex items-center gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={handleBulkComplete}
                isLoading={bulkUpdateMutation.isPending}
              >
                <CheckSquare className="w-4 h-4 mr-1" />
                Ολοκλήρωση
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setIsBulkCompleteNotifyDialogOpen(true)}
                isLoading={bulkCompleteNotifyMutation.isPending}
              >
                <Mail className="w-4 h-4 mr-1" />
                Ολοκλήρωση + Email
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => setIsBulkDeleteDialogOpen(true)}
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Διαγραφή
              </Button>
            <button
              onClick={() => {
                setSelectedIds(new Set());
                setSelectAll(false);
              }}
              className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              title="Ακύρωση επιλογής"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Error Banner */}
      {isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <span className="text-red-700">
                Σφάλμα φόρτωσης: {error instanceof Error ? error.message : 'Άγνωστο σφάλμα'}
              </span>
            </div>
            <Button variant="secondary" size="sm" onClick={() => refetch()}>
              <RefreshCw className="w-4 h-4 mr-1" />
              Επανάληψη
            </Button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Φόρτωση υποχρεώσεων...</p>
        </div>
      )}

      {/* Obligations Table */}
      {!isLoading && !isError && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <p className="text-sm text-gray-500">
                {obligations.length} από {totalCount} υποχρεώσεις
              </p>
            </div>

            {obligations.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                Δεν βρέθηκαν υποχρεώσεις με τα επιλεγμένα φίλτρα.
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left">
                          <button
                            onClick={handleSelectAll}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            {selectAll ? (
                              <CheckSquare className="w-5 h-5" />
                            ) : (
                              <Square className="w-5 h-5" />
                            )}
                          </button>
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Πελάτης
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Τύπος
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Περίοδος
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Προθεσμία
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Κατάσταση
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Ενέργειες
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {obligations.map((obligation) => (
                        <tr key={obligation.id} className={`hover:bg-gray-50 ${selectedIds.has(obligation.id) ? 'bg-blue-50' : ''}`}>
                          <td className="px-4 py-4">
                            <button
                              onClick={() => handleSelectOne(obligation.id)}
                              className="text-gray-400 hover:text-gray-600"
                            >
                              {selectedIds.has(obligation.id) ? (
                                <CheckSquare className="w-5 h-5 text-blue-600" />
                              ) : (
                                <Square className="w-5 h-5" />
                              )}
                            </button>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              {obligation.client_name || `Πελάτης #${obligation.client}`}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex px-2 py-1 text-sm font-medium bg-gray-100 text-gray-800 rounded">
                              {obligation.type_name || obligation.type_code || obligation.obligation_type}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {String(obligation.month).padStart(2, '0')}/{obligation.year}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(obligation.deadline)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                                STATUS_COLORS[obligation.status]
                              }`}
                            >
                              {STATUS_LABELS[obligation.status]}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end gap-1">
                              {/* Complete button - only show for non-completed */}
                              {obligation.status !== 'completed' && (
                                <button
                                  onClick={() => handleCompleteClick(obligation)}
                                  className="text-green-600 hover:text-green-900 p-1.5 hover:bg-green-50 rounded"
                                  title="Ολοκλήρωση"
                                >
                                  <CheckCircle className="w-4 h-4" />
                                </button>
                              )}
                              {/* Attach document button */}
                              <button
                                onClick={() => handleUploadClick(obligation)}
                                className="text-purple-600 hover:text-purple-900 p-1.5 hover:bg-purple-50 rounded"
                                title="Επισύναψη εγγράφου"
                              >
                                <Paperclip className="w-4 h-4" />
                              </button>
                              {/* Send email button */}
                              <button
                                onClick={() => handleEmailClick(obligation)}
                                className="text-blue-600 hover:text-blue-900 p-1.5 hover:bg-blue-50 rounded"
                                title="Αποστολή email"
                              >
                                <Mail className="w-4 h-4" />
                              </button>
                              {/* Edit button */}
                              <button
                                onClick={() => handleEdit(obligation)}
                                className="text-gray-600 hover:text-gray-900 p-1.5 hover:bg-gray-100 rounded"
                                title="Επεξεργασία"
                              >
                                <Edit2 className="w-4 h-4" />
                              </button>
                              {/* Delete button */}
                              <button
                                onClick={() => handleDeleteClick(obligation)}
                                className="text-red-600 hover:text-red-900 p-1.5 hover:bg-red-50 rounded"
                                title="Διαγραφή"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Load More / Pagination */}
                {hasMore && (
                  <div className="px-6 py-4 border-t border-gray-200 text-center">
                    <Button variant="secondary" onClick={() => setPage((p) => p + 1)}>
                      Φόρτωση περισσότερων ({obligations.length} από {totalCount})
                    </Button>
                  </div>
                )}
            </>
          )}
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Νέα Υποχρέωση"
        size="lg"
      >
        <ObligationForm
          clients={clients}
          onSubmit={handleCreate}
          onCancel={() => setIsCreateModalOpen(false)}
          isLoading={createMutation.isPending}
        />
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedObligation(null);
        }}
        title="Επεξεργασία Υποχρέωσης"
        size="lg"
      >
        <ObligationForm
          obligation={selectedObligation}
          clients={clients}
          onSubmit={handleUpdate}
          onCancel={() => {
            setIsEditModalOpen(false);
            setSelectedObligation(null);
          }}
          isLoading={updateMutation.isPending}
        />
      </Modal>

      {/* Bulk Create Modal */}
      <Modal
        isOpen={isBulkCreateModalOpen}
        onClose={() => setIsBulkCreateModalOpen(false)}
        title="Μαζική Δημιουργία Υποχρεώσεων"
        size="xl"
      >
        <div className="space-y-4">
          {/* Obligation Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Τύπος Υποχρέωσης *
            </label>
            <select
              value={bulkCreateForm.obligation_type}
              onChange={(e) =>
                setBulkCreateForm((prev) => ({ ...prev, obligation_type: Number(e.target.value) }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value={0}>-- Επιλέξτε τύπο --</option>
              {obligationTypes?.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.code} - {type.name}
                </option>
              ))}
            </select>
          </div>

          {/* Period */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Μήνας</label>
              <select
                value={bulkCreateForm.month}
                onChange={(e) =>
                  setBulkCreateForm((prev) => ({ ...prev, month: Number(e.target.value) }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                {MONTHS.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Έτος</label>
              <select
                value={bulkCreateForm.year}
                onChange={(e) =>
                  setBulkCreateForm((prev) => ({ ...prev, year: Number(e.target.value) }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                {YEARS.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Client Selection */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Πελάτες ({bulkCreateForm.client_ids.length} επιλεγμένοι) *
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={selectAllClients}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  Επιλογή όλων
                </button>
                <button
                  type="button"
                  onClick={deselectAllClients}
                  className="text-xs text-gray-600 hover:text-gray-800"
                >
                  Αποεπιλογή όλων
                </button>
              </div>
            </div>
            <div className="border border-gray-300 rounded-md max-h-60 overflow-y-auto">
              {clients.map((client) => (
                <label
                  key={client.id}
                  className="flex items-center px-3 py-2 hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={bulkCreateForm.client_ids.includes(client.id)}
                    onChange={() => toggleClientSelection(client.id)}
                    className="mr-3"
                  />
                  <span className="text-sm">
                    {client.eponimia} ({client.afm})
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsBulkCreateModalOpen(false)}
            >
              Ακύρωση
            </Button>
            <Button
              type="button"
              variant="primary"
              onClick={handleBulkCreate}
              isLoading={bulkCreateMutation.isPending}
              disabled={bulkCreateForm.client_ids.length === 0 || !bulkCreateForm.obligation_type}
            >
              <Calendar className="w-4 h-4 mr-2" />
              Δημιουργία για {bulkCreateForm.client_ids.length} πελάτες
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false);
          setSelectedObligation(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Διαγραφή Υποχρέωσης"
        message={`Είστε σίγουροι ότι θέλετε να διαγράψετε την υποχρέωση για ${selectedObligation?.client_name || 'τον πελάτη'};`}
        confirmText="Διαγραφή"
        cancelText="Ακύρωση"
        isLoading={deleteMutation.isPending}
        variant="danger"
      />

      {/* Bulk Delete Confirmation */}
      <ConfirmDialog
        isOpen={isBulkDeleteDialogOpen}
        onClose={() => setIsBulkDeleteDialogOpen(false)}
        onConfirm={handleBulkDeleteConfirm}
        title="Διαγραφή Επιλεγμένων Υποχρεώσεων"
        message={`Είστε σίγουροι ότι θέλετε να διαγράψετε ${selectedIds.size} υποχρεώσεις;`}
        confirmText="Διαγραφή"
        cancelText="Ακύρωση"
        isLoading={bulkDeleteMutation.isPending}
        variant="danger"
      />

      {/* Generate Month Modal */}
      <GenerateMonthModal
        isOpen={isGenerateMonthModalOpen}
        onClose={() => {
          setIsGenerateMonthModalOpen(false);
          setGenerateResult(null);
        }}
        clients={clients}
        onGenerate={async (data) => {
          const result = await generateMonthMutation.mutateAsync(data);
          setGenerateResult(result);
          // invalidateQueries in hook triggers automatic refetch
        }}
        isLoading={generateMonthMutation.isPending}
        result={generateResult}
      />

      {/* Complete Obligation Modal */}
      <CompleteObligationModal
        isOpen={isCompleteModalOpen}
        onClose={() => {
          setIsCompleteModalOpen(false);
          setSelectedObligation(null);
        }}
        obligation={selectedObligation}
        clientName={getSelectedClient()?.eponimia || ''}
        clientEmail={getSelectedClient()?.email || undefined}
        onComplete={handleCompleteAndNotify}
        isLoading={completeAndNotifyMutation.isPending}
      />

      {/* Document Upload Modal */}
      <DocumentUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => {
          setIsUploadModalOpen(false);
          setSelectedObligation(null);
        }}
        onUpload={handleUploadDocument}
        clientName={getSelectedClient()?.eponimia}
        obligationType={selectedObligation?.type_name || selectedObligation?.type_code}
        isLoading={uploadToObligationMutation.isPending}
      />

      {/* Send Email Modal */}
      <SendEmailModal
        isOpen={isEmailModalOpen}
        onClose={() => {
          setIsEmailModalOpen(false);
          setSelectedObligation(null);
        }}
        onSend={handleSendEmail}
        clientName={getSelectedClient()?.eponimia || ''}
        clientEmail={getSelectedClient()?.email || ''}
        obligationId={selectedObligation?.id}
        isLoading={sendObligationNoticeMutation.isPending}
      />

      {/* Bulk Complete with Notifications Dialog */}
      <ConfirmDialog
        isOpen={isBulkCompleteNotifyDialogOpen}
        onClose={() => setIsBulkCompleteNotifyDialogOpen(false)}
        onConfirm={() => handleBulkCompleteWithNotify(true)}
        title="Ολοκλήρωση με Email"
        message={`Θέλετε να ολοκληρώσετε ${selectedIds.size} υποχρεώσεις και να στείλετε email ειδοποίησης στους πελάτες;`}
        confirmText="Ολοκλήρωση & Αποστολή"
        cancelText="Ακύρωση"
        isLoading={bulkCompleteNotifyMutation.isPending}
      />
    </div>
  );
}

// ============================================
// GENERATE MONTH MODAL COMPONENT
// ============================================
interface GenerateMonthModalProps {
  isOpen: boolean;
  onClose: () => void;
  clients: Array<{ id: number; eponimia: string; afm: string }>;
  onGenerate: (data: { month: number; year: number; client_ids?: number[] }) => Promise<void>;
  isLoading: boolean;
  result: GenerateMonthResult | null;
}

function GenerateMonthModal({
  isOpen,
  onClose,
  clients,
  onGenerate,
  isLoading,
  result,
}: GenerateMonthModalProps) {
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;

  const [month, setMonth] = useState(currentMonth);
  const [year, setYear] = useState(currentYear);
  const [useAllClients, setUseAllClients] = useState(true);
  const [selectedClientIds, setSelectedClientIds] = useState<number[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter clients by search
  const filteredClients = clients.filter(
    (c) =>
      c.eponimia.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.afm.includes(searchTerm)
  );

  // Toggle client selection
  const toggleClient = (clientId: number) => {
    if (selectedClientIds.includes(clientId)) {
      setSelectedClientIds(selectedClientIds.filter((id) => id !== clientId));
    } else {
      setSelectedClientIds([...selectedClientIds, clientId]);
    }
  };

  // Select all filtered clients
  const selectAll = () => {
    setSelectedClientIds(filteredClients.map((c) => c.id));
  };

  // Deselect all
  const deselectAll = () => {
    setSelectedClientIds([]);
  };

  // Handle submit
  const handleSubmit = async () => {
    await onGenerate({
      month,
      year,
      client_ids: useAllClients ? undefined : selectedClientIds,
    });
  };

  // Reset form when modal closes
  const handleClose = () => {
    setMonth(currentMonth);
    setYear(currentYear);
    setUseAllClients(true);
    setSelectedClientIds([]);
    setSearchTerm('');
    onClose();
  };

  if (!isOpen) return null;

  // Show result view if we have a result
  if (result) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg w-full max-w-lg mx-4 max-h-[90vh] overflow-hidden flex flex-col">
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center">
              <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900">Ολοκληρώθηκε</h2>
            </div>
            <button onClick={handleClose} className="p-2 hover:bg-gray-100 rounded-lg">
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>
          <div className="p-6 space-y-4 overflow-y-auto">
            {/* Summary */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-2xl font-bold text-green-700">{result.created_count}</p>
                <p className="text-sm text-green-600">Δημιουργήθηκαν</p>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4">
                <p className="text-2xl font-bold text-yellow-700">{result.skipped_count}</p>
                <p className="text-sm text-yellow-600">Παραλείφθηκαν</p>
              </div>
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-2xl font-bold text-blue-700">{result.clients_processed}</p>
                <p className="text-sm text-blue-600">Πελάτες</p>
              </div>
            </div>

            {/* Details */}
            {result.details && result.details.length > 0 && (
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Λεπτομέρειες</h3>
                <div className="border rounded-lg max-h-60 overflow-y-auto divide-y">
                  {result.details.map((detail) => (
                    <div key={detail.client_id} className="p-3 text-sm">
                      <p className="font-medium text-gray-900">{detail.client_name}</p>
                      {detail.created.length > 0 && (
                        <p className="text-green-600 text-xs mt-1">
                          Δημιουργήθηκαν: {detail.created.join(', ')}
                        </p>
                      )}
                      {detail.skipped.length > 0 && (
                        <p className="text-yellow-600 text-xs mt-1">
                          Παραλείφθηκαν: {detail.skipped.join(', ')}
                        </p>
                      )}
                      {detail.note && (
                        <p className="text-gray-500 text-xs mt-1">{detail.note}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          <div className="p-4 border-t bg-gray-50">
            <Button onClick={handleClose} className="w-full">
              Κλείσιμο
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-lg mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center">
            <CalendarPlus className="w-6 h-6 text-yellow-600 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">Δημιουργία Υποχρεώσεων Μήνα</h2>
          </div>
          <button onClick={handleClose} className="p-2 hover:bg-gray-100 rounded-lg" disabled={isLoading}>
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>
        <div className="p-4 space-y-4 overflow-y-auto">
          {/* Period Selection */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Μήνας</label>
              <select
                value={month}
                onChange={(e) => setMonth(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                disabled={isLoading}
              >
                {MONTHS.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Έτος</label>
              <select
                value={year}
                onChange={(e) => setYear(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                disabled={isLoading}
              >
                {YEARS.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Client Selection Mode */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Πελάτες</label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  checked={useAllClients}
                  onChange={() => setUseAllClients(true)}
                  className="h-4 w-4 text-blue-600"
                  disabled={isLoading}
                />
                <span className="text-sm text-gray-700">Όλοι οι ενεργοί πελάτες</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  checked={!useAllClients}
                  onChange={() => setUseAllClients(false)}
                  className="h-4 w-4 text-blue-600"
                  disabled={isLoading}
                />
                <span className="text-sm text-gray-700">Επιλεγμένοι πελάτες</span>
              </label>
            </div>
          </div>

          {/* Client List (if not all) */}
          {!useAllClients && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">
                  Επιλέξτε πελάτες ({selectedClientIds.length} επιλεγμένοι)
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={selectAll}
                    className="text-xs text-blue-600 hover:text-blue-800"
                    disabled={isLoading}
                  >
                    Επιλογή όλων
                  </button>
                  <button
                    type="button"
                    onClick={deselectAll}
                    className="text-xs text-gray-600 hover:text-gray-800"
                    disabled={isLoading}
                  >
                    Αποεπιλογή όλων
                  </button>
                </div>
              </div>

              {/* Search */}
              <input
                type="text"
                placeholder="Αναζήτηση πελάτη..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md mb-2"
                disabled={isLoading}
              />

              {/* Client List */}
              <div className="border border-gray-300 rounded-md max-h-48 overflow-y-auto">
                {filteredClients.length === 0 ? (
                  <div className="p-4 text-center text-gray-500 text-sm">
                    Δεν βρέθηκαν πελάτες
                  </div>
                ) : (
                  filteredClients.map((client) => (
                    <label
                      key={client.id}
                      className="flex items-center px-3 py-2 hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedClientIds.includes(client.id)}
                        onChange={() => toggleClient(client.id)}
                        className="mr-3 h-4 w-4 text-blue-600 rounded"
                        disabled={isLoading}
                      />
                      <span className="text-sm">
                        {client.eponimia}{' '}
                        <span className="text-gray-500">({client.afm})</span>
                      </span>
                    </label>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm text-blue-700">
              Θα δημιουργηθούν υποχρεώσεις βάσει του προφίλ κάθε πελάτη.
              Υποχρεώσεις που υπάρχουν ήδη θα παραλειφθούν.
            </p>
          </div>
        </div>
        <div className="flex gap-3 p-4 border-t bg-gray-50">
          <Button variant="secondary" onClick={handleClose} disabled={isLoading}>
            Ακύρωση
          </Button>
          <Button
            onClick={handleSubmit}
            isLoading={isLoading}
            disabled={isLoading || (!useAllClients && selectedClientIds.length === 0)}
            className="flex-1"
          >
            <CalendarPlus className="w-4 h-4 mr-2" />
            Δημιουργία
          </Button>
        </div>
      </div>
    </div>
  );
}
