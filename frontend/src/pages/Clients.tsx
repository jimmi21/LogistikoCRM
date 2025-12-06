import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useClients, useCreateClient, useDeleteClient } from '../hooks/useClients';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import { Modal, ConfirmDialog, ClientForm, Button } from '../components';
import { Users, Search, AlertCircle, RefreshCw, Plus, Edit2, Trash2, Eye } from 'lucide-react';
import type { Client, ClientFormData } from '../types';

export default function Clients() {
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 100;

  // Modal state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);

  const { data, isLoading, isError, error, refetch } = useClients({ page, page_size: pageSize });
  const createMutation = useCreateClient();
  const deleteMutation = useDeleteClient();
  const queryClient = useQueryClient();

  // Update client mutation
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<ClientFormData> }) => {
      const response = await apiClient.patch<Client>(`/api/v1/clients/${id}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });

  // Filter clients by name (eponimia) or AFM
  const filteredClients = useMemo(() => {
    if (!data?.results) return [];
    if (!searchTerm.trim()) return data.results;

    const term = searchTerm.toLowerCase().trim();
    return data.results.filter(
      (client) =>
        (client.eponimia?.toLowerCase() || '').includes(term) ||
        (client.afm || '').includes(term)
    );
  }, [data?.results, searchTerm]);

  // Handlers
  const handleCreate = (formData: ClientFormData) => {
    createMutation.mutate(formData, {
      onSuccess: () => {
        setIsCreateModalOpen(false);
        // invalidateQueries in hook triggers automatic refetch
      },
    });
  };

  const handleEdit = (client: Client) => {
    setSelectedClient(client);
    setIsEditModalOpen(true);
  };

  const handleUpdate = (formData: ClientFormData) => {
    if (!selectedClient) return;
    updateMutation.mutate(
      { id: selectedClient.id, data: formData },
      {
        onSuccess: () => {
          setIsEditModalOpen(false);
          setSelectedClient(null);
          // invalidateQueries in hook triggers automatic refetch
        },
      }
    );
  };

  const handleDeleteClick = (client: Client) => {
    setSelectedClient(client);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (!selectedClient) return;
    deleteMutation.mutate(selectedClient.id, {
      onSuccess: () => {
        setIsDeleteDialogOpen(false);
        setSelectedClient(null);
        // invalidateQueries in hook triggers automatic refetch
      },
    });
  };

  const handleLoadMore = () => {
    setPage((prev) => prev + 1);
  };

  const hasMore = data?.next !== null;
  const totalCount = data?.count || 0;
  const loadedCount = data?.results?.length || 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Users className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Πελάτες</h1>
            <p className="text-sm text-gray-500">{totalCount} συνολικά</p>
          </div>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Νέος Πελάτης
        </Button>
      </div>

      {/* Search Box */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Αναζήτηση με επωνυμία ή ΑΦΜ..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

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
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Φόρτωση πελατών...</p>
        </div>
      )}

      {/* Clients Table */}
      {!isLoading && !isError && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <p className="text-sm text-gray-600">
              {filteredClients.length} από {totalCount} πελάτες
              {searchTerm && ` (φίλτρο: "${searchTerm}")`}
            </p>
          </div>

          {filteredClients.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              {searchTerm
                ? 'Δεν βρέθηκαν πελάτες με αυτά τα κριτήρια αναζήτησης.'
                : 'Δεν υπάρχουν πελάτες.'}
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Επωνυμία
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        ΑΦΜ
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Τηλέφωνο
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Ενέργειες
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredClients.map((client) => (
                      <tr key={client.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Link to={`/clients/${client.id}`} className="flex items-center group">
                            <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                              <span className="text-blue-600 font-medium text-sm">
                                {(client.eponimia || 'Π').charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                                {client.eponimia}
                              </div>
                              {client.is_active === false && (
                                <span className="inline-flex px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded">
                                  Ανενεργός
                                </span>
                              )}
                            </div>
                          </Link>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="font-mono text-sm text-gray-900">{client.afm}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {client.kinito_tilefono || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {client.email || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <Link
                            to={`/clients/${client.id}`}
                            className="text-gray-600 hover:text-gray-900 mr-3 p-1.5 hover:bg-gray-50 rounded-lg transition-colors inline-block"
                            title="Προβολή"
                          >
                            <Eye className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleEdit(client)}
                            className="text-blue-600 hover:text-blue-900 mr-3 p-1.5 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Επεξεργασία"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteClick(client)}
                            className="text-red-600 hover:text-red-900 p-1.5 hover:bg-red-50 rounded-lg transition-colors"
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
              {hasMore && !searchTerm && (
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

      {/* Create Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Νέος Πελάτης"
      >
        <ClientForm
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
          setSelectedClient(null);
        }}
        title="Επεξεργασία Πελάτη"
      >
        <ClientForm
          client={selectedClient}
          onSubmit={handleUpdate}
          onCancel={() => {
            setIsEditModalOpen(false);
            setSelectedClient(null);
          }}
          isLoading={updateMutation.isPending}
        />
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false);
          setSelectedClient(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Διαγραφή Πελάτη"
        message={`Είστε σίγουροι ότι θέλετε να διαγράψετε τον πελάτη "${selectedClient?.eponimia}";`}
        confirmText="Διαγραφή"
        cancelText="Ακύρωση"
        isLoading={deleteMutation.isPending}
        variant="danger"
      />
    </div>
  );
}
