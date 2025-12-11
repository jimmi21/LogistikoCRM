/**
 * BulkAssignModal.tsx
 * Modal for bulk assigning obligation types and profiles to multiple clients
 */

import { useState, useMemo } from 'react';
import { Users, Package, CheckSquare, Square, Search, X, AlertCircle } from 'lucide-react';
import { Modal } from './Modal';
import { Button } from './Button';
import { useClients } from '../hooks/useClients';
import { useObligationTypes, useObligationProfiles } from '../hooks/useObligations';
import { useBulkAssignObligations } from '../hooks/useClientDetails';
import type { Client, ObligationType, ObligationProfileBundle } from '../types';

interface BulkAssignModalProps {
  isOpen: boolean;
  onClose: () => void;
  preselectedClientIds?: number[];
}

type AssignMode = 'add' | 'replace';

export function BulkAssignModal({
  isOpen,
  onClose,
  preselectedClientIds = [],
}: BulkAssignModalProps) {
  // State
  const [selectedClientIds, setSelectedClientIds] = useState<Set<number>>(
    new Set(preselectedClientIds)
  );
  const [selectedProfileIds, setSelectedProfileIds] = useState<Set<number>>(new Set());
  const [selectedTypeIds, setSelectedTypeIds] = useState<Set<number>>(new Set());
  const [mode, setMode] = useState<AssignMode>('add');
  const [clientSearch, setClientSearch] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Queries
  const { data: clientsData } = useClients({ page_size: 1000, is_active: true });
  const { data: obligationTypes = [] } = useObligationTypes();
  const { data: profiles = [] } = useObligationProfiles();

  // Mutation
  const bulkAssignMutation = useBulkAssignObligations();

  // Filtered clients
  const clients = clientsData?.results || [];
  const filteredClients = useMemo(() => {
    if (!clientSearch.trim()) return clients;
    const search = clientSearch.toLowerCase();
    return clients.filter(
      (c) =>
        c.eponimia.toLowerCase().includes(search) ||
        c.afm.includes(search)
    );
  }, [clients, clientSearch]);

  // Standalone types (not in any profile)
  const standaloneTypes = useMemo(() => {
    const profileTypeIds = new Set<number>();
    profiles.forEach((p) => {
      p.obligation_types.forEach((t) => profileTypeIds.add(t.id));
    });
    return obligationTypes.filter((t) => !profileTypeIds.has(t.id) && t.is_active);
  }, [obligationTypes, profiles]);

  // Handlers
  const toggleClient = (clientId: number) => {
    setSelectedClientIds((prev) => {
      const next = new Set(prev);
      if (next.has(clientId)) {
        next.delete(clientId);
      } else {
        next.add(clientId);
      }
      return next;
    });
  };

  const toggleAllClients = () => {
    if (selectedClientIds.size === filteredClients.length) {
      setSelectedClientIds(new Set());
    } else {
      setSelectedClientIds(new Set(filteredClients.map((c) => c.id)));
    }
  };

  const toggleProfile = (profileId: number) => {
    setSelectedProfileIds((prev) => {
      const next = new Set(prev);
      if (next.has(profileId)) {
        next.delete(profileId);
      } else {
        next.add(profileId);
      }
      return next;
    });
  };

  const toggleType = (typeId: number) => {
    setSelectedTypeIds((prev) => {
      const next = new Set(prev);
      if (next.has(typeId)) {
        next.delete(typeId);
      } else {
        next.add(typeId);
      }
      return next;
    });
  };

  const handleSubmit = async () => {
    if (selectedClientIds.size === 0) {
      setError('Επιλέξτε τουλάχιστον έναν πελάτη.');
      return;
    }
    if (selectedProfileIds.size === 0 && selectedTypeIds.size === 0) {
      setError('Επιλέξτε τουλάχιστον ένα προφίλ ή τύπο υποχρέωσης.');
      return;
    }

    try {
      await bulkAssignMutation.mutateAsync({
        client_ids: Array.from(selectedClientIds),
        obligation_profile_ids: Array.from(selectedProfileIds),
        obligation_type_ids: Array.from(selectedTypeIds),
        mode,
      });
      handleClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Σφάλμα κατά την ανάθεση');
    }
  };

  const handleClose = () => {
    setSelectedClientIds(new Set(preselectedClientIds));
    setSelectedProfileIds(new Set());
    setSelectedTypeIds(new Set());
    setMode('add');
    setClientSearch('');
    setError(null);
    onClose();
  };

  const isValid = selectedClientIds.size > 0 && (selectedProfileIds.size > 0 || selectedTypeIds.size > 0);

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Μαζική Ανάθεση Υποχρεώσεων"
      size="xl"
    >
      <div className="space-y-5">
        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <span className="text-sm text-red-700">{error}</span>
            <button onClick={() => setError(null)} className="ml-auto">
              <X className="w-4 h-4 text-red-500" />
            </button>
          </div>
        )}

        {/* Success message from mutation */}
        {bulkAssignMutation.isSuccess && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <span className="text-sm text-green-700">
              {bulkAssignMutation.data?.message}
            </span>
          </div>
        )}

        {/* Mode selection */}
        <div className="bg-gray-50 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Τρόπος Ανάθεσης
          </label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="mode"
                value="add"
                checked={mode === 'add'}
                onChange={() => setMode('add')}
                className="w-4 h-4 text-blue-600"
              />
              <span className="text-sm text-gray-700">
                <strong>Προσθήκη</strong> - Προσθέτει στις υπάρχουσες υποχρεώσεις
              </span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="mode"
                value="replace"
                checked={mode === 'replace'}
                onChange={() => setMode('replace')}
                className="w-4 h-4 text-blue-600"
              />
              <span className="text-sm text-gray-700">
                <strong>Αντικατάσταση</strong> - Αντικαθιστά όλες τις υποχρεώσεις
              </span>
            </label>
          </div>
          {mode === 'replace' && (
            <p className="mt-2 text-xs text-amber-600">
              Προσοχή: Αυτό θα αντικαταστήσει όλες τις υπάρχουσες υποχρεώσεις των επιλεγμένων πελατών!
            </p>
          )}
        </div>

        {/* Two-column layout */}
        <div className="grid grid-cols-2 gap-4">
          {/* Left: Client selection */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-gray-900 flex items-center gap-2">
                <Users className="w-4 h-4" />
                Πελάτες ({selectedClientIds.size} επιλεγμένοι)
              </h3>
              <button
                onClick={toggleAllClients}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                {selectedClientIds.size === filteredClients.length ? 'Αποεπιλογή όλων' : 'Επιλογή όλων'}
              </button>
            </div>

            {/* Search */}
            <div className="relative mb-3">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={clientSearch}
                onChange={(e) => setClientSearch(e.target.value)}
                placeholder="Αναζήτηση (επωνυμία ή ΑΦΜ)..."
                className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Client list */}
            <div className="max-h-64 overflow-y-auto space-y-1">
              {filteredClients.map((client) => (
                <label
                  key={client.id}
                  className={`flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-gray-50 ${
                    selectedClientIds.has(client.id) ? 'bg-blue-50' : ''
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedClientIds.has(client.id)}
                    onChange={() => toggleClient(client.id)}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {client.eponimia}
                    </p>
                    <p className="text-xs text-gray-500">{client.afm}</p>
                  </div>
                </label>
              ))}
              {filteredClients.length === 0 && (
                <p className="text-sm text-gray-500 text-center py-4">
                  Δεν βρέθηκαν πελάτες
                </p>
              )}
            </div>
          </div>

          {/* Right: Profiles and Types selection */}
          <div className="space-y-4">
            {/* Profiles */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 flex items-center gap-2 mb-3">
                <Package className="w-4 h-4" />
                Προφίλ Υποχρεώσεων ({selectedProfileIds.size} επιλεγμένα)
              </h3>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {profiles.map((profile) => (
                  <label
                    key={profile.id}
                    className={`flex items-start gap-2 p-2 rounded cursor-pointer hover:bg-gray-50 ${
                      selectedProfileIds.has(profile.id) ? 'bg-green-50' : ''
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedProfileIds.has(profile.id)}
                      onChange={() => toggleProfile(profile.id)}
                      className="w-4 h-4 text-green-600 rounded mt-0.5"
                    />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {profile.name}
                      </p>
                      {profile.description && (
                        <p className="text-xs text-gray-500 truncate">
                          {profile.description}
                        </p>
                      )}
                      <p className="text-xs text-gray-400">
                        {profile.obligation_types.length} υποχρεώσεις
                      </p>
                    </div>
                  </label>
                ))}
                {profiles.length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-2">
                    Δεν υπάρχουν διαθέσιμα προφίλ
                  </p>
                )}
              </div>
            </div>

            {/* Standalone Types */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 flex items-center gap-2 mb-3">
                <CheckSquare className="w-4 h-4" />
                Μεμονωμένες Υποχρεώσεις ({selectedTypeIds.size} επιλεγμένες)
              </h3>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {standaloneTypes.map((type) => (
                  <label
                    key={type.id}
                    className={`flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-gray-50 ${
                      selectedTypeIds.has(type.id) ? 'bg-purple-50' : ''
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedTypeIds.has(type.id)}
                      onChange={() => toggleType(type.id)}
                      className="w-4 h-4 text-purple-600 rounded"
                    />
                    <span className="text-sm text-gray-900">{type.name}</span>
                  </label>
                ))}
                {standaloneTypes.length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-2">
                    Όλες οι υποχρεώσεις ανήκουν σε προφίλ
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Summary */}
        {isValid && (
          <div className="bg-blue-50 rounded-lg p-3 text-sm text-blue-700">
            Θα ανατεθούν{' '}
            {selectedProfileIds.size > 0 && (
              <strong>{selectedProfileIds.size} προφίλ</strong>
            )}
            {selectedProfileIds.size > 0 && selectedTypeIds.size > 0 && ' και '}
            {selectedTypeIds.size > 0 && (
              <strong>{selectedTypeIds.size} υποχρεώσεις</strong>
            )}{' '}
            σε <strong>{selectedClientIds.size} πελάτες</strong>
            {mode === 'replace' && (
              <span className="text-amber-600"> (αντικατάσταση υπαρχόντων)</span>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          <Button variant="secondary" onClick={handleClose} disabled={bulkAssignMutation.isPending}>
            Ακύρωση
          </Button>
          <Button
            onClick={handleSubmit}
            isLoading={bulkAssignMutation.isPending}
            disabled={!isValid || bulkAssignMutation.isPending}
            className="flex-1"
          >
            <Users className="w-4 h-4 mr-2" />
            Ανάθεση σε {selectedClientIds.size} πελάτες
          </Button>
        </div>
      </div>
    </Modal>
  );
}

export default BulkAssignModal;
