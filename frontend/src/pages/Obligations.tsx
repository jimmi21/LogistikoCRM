import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useObligations, useCreateObligation, useDeleteObligation } from '../hooks/useObligations';
import { useClients } from '../hooks/useClients';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import { Modal, ConfirmDialog, ObligationForm, Button } from '../components';
import { ArrowLeft, FileText, AlertCircle, RefreshCw, Filter, Plus, Edit2, Trash2 } from 'lucide-react';
import type { Obligation, ObligationFormData, ObligationStatus } from '../types';

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

type StatusFilter = 'all' | 'pending' | 'completed';

export default function Obligations() {
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [page, setPage] = useState(1);
  const pageSize = 100; // Increased page size

  // Modal state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedObligation, setSelectedObligation] = useState<Obligation | null>(null);

  const { data, isLoading, isError, error, refetch } = useObligations({ page, page_size: pageSize });
  const { data: clientsData } = useClients({ page_size: 1000 }); // Fetch all clients for dropdown
  const createMutation = useCreateObligation();
  const deleteMutation = useDeleteObligation();
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

  // Filter obligations by status
  const filteredObligations = useMemo(() => {
    if (!data?.results) return [];
    if (statusFilter === 'all') return data.results;

    return data.results.filter((obligation) => obligation.status === statusFilter);
  }, [data?.results, statusFilter]);

  // Format date for display (handles null/undefined/invalid dates)
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

  // Handlers
  const handleCreate = (formData: ObligationFormData) => {
    createMutation.mutate(formData, {
      onSuccess: () => {
        setIsCreateModalOpen(false);
        refetch();
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
          refetch();
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
        refetch();
      },
    });
  };

  const handleLoadMore = () => {
    setPage((prev) => prev + 1);
  };

  const hasMore = data?.next !== null;
  const totalCount = data?.count || 0;
  const loadedCount = data?.results?.length || 0;
  const clients = clientsData?.results || [];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Link
                to="/"
                className="mr-4 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center">
                <FileText className="w-6 h-6 text-yellow-600 mr-3" />
                <h1 className="text-2xl font-bold text-gray-900">Υποχρεώσεις</h1>
              </div>
            </div>
            <Button onClick={() => setIsCreateModalOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Νέα Υποχρέωση
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filter Controls */}
        <div className="mb-6 bg-white rounded-lg shadow p-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center text-gray-600">
              <Filter className="w-5 h-5 mr-2" />
              <span className="font-medium">Φίλτρο κατάστασης:</span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setStatusFilter('all')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === 'all'
                    ? 'bg-gray-800 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Όλες
              </button>
              <button
                onClick={() => setStatusFilter('pending')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === 'pending'
                    ? 'bg-yellow-500 text-white'
                    : 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100'
                }`}
              >
                Εκκρεμείς
              </button>
              <button
                onClick={() => setStatusFilter('completed')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === 'completed'
                    ? 'bg-green-500 text-white'
                    : 'bg-green-50 text-green-700 hover:bg-green-100'
                }`}
              >
                Ολοκληρωμένες
              </button>
            </div>
          </div>
        </div>

        {/* Error Banner */}
        {isError && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                <span className="text-red-700">
                  Σφάλμα φόρτωσης: {error instanceof Error ? error.message : 'Άγνωστο σφάλμα'}
                </span>
              </div>
              <button
                onClick={() => refetch()}
                className="inline-flex items-center px-3 py-1 text-sm font-medium text-red-700 bg-red-100 rounded hover:bg-red-200"
              >
                <RefreshCw className="w-4 h-4 mr-1" />
                Επανάληψη
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Φόρτωση υποχρεώσεων...</p>
          </div>
        )}

        {/* Obligations Table */}
        {!isLoading && !isError && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <p className="text-sm text-gray-500">
                {filteredObligations.length} από {totalCount} υποχρεώσεις
                {statusFilter !== 'all' && ` (${STATUS_LABELS[statusFilter as ObligationStatus]})`}
              </p>
            </div>

            {filteredObligations.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                {statusFilter !== 'all'
                  ? `Δεν υπάρχουν υποχρεώσεις με κατάσταση "${STATUS_LABELS[statusFilter as ObligationStatus]}".`
                  : 'Δεν υπάρχουν υποχρεώσεις.'}
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Πελάτης
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Τύπος
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
                      {filteredObligations.map((obligation) => (
                        <tr key={obligation.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              {obligation.client_name || `Πελάτης #${obligation.client}`}
                            </div>
                            <div className="text-xs text-gray-500">
                              Περίοδος: {obligation.month}/{obligation.year}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex px-2 py-1 text-sm font-medium bg-gray-100 text-gray-800 rounded">
                              {obligation.obligation_type}
                            </span>
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
                            <button
                              onClick={() => handleEdit(obligation)}
                              className="text-blue-600 hover:text-blue-900 mr-3 p-1 hover:bg-blue-50 rounded"
                              title="Επεξεργασία"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteClick(obligation)}
                              className="text-red-600 hover:text-red-900 p-1 hover:bg-red-50 rounded"
                              title="Διαγραφή"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Load More */}
                {hasMore && statusFilter === 'all' && (
                  <div className="px-6 py-4 border-t border-gray-200 text-center">
                    <Button variant="secondary" onClick={handleLoadMore}>
                      Φόρτωση περισσότερων ({loadedCount} από {totalCount})
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Back to Dashboard Link */}
        <div className="mt-6">
          <Link
            to="/"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Επιστροφή στην Αρχική
          </Link>
        </div>
      </main>

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

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false);
          setSelectedObligation(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Διαγραφή Υποχρέωσης"
        message={`Είστε σίγουροι ότι θέλετε να διαγράψετε την υποχρέωση ${selectedObligation?.obligation_type} για ${selectedObligation?.client_name || 'τον πελάτη'};`}
        confirmText="Διαγραφή"
        cancelText="Ακύρωση"
        isLoading={deleteMutation.isPending}
        variant="danger"
      />
    </div>
  );
}
