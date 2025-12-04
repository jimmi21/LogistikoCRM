import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Users, ClipboardList, X, Loader2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { clientsApi, obligationsApi } from '../../api/client';
import type { Client, Obligation } from '../../types';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type SearchResult =
  | { type: 'client'; data: Client }
  | { type: 'obligation'; data: Obligation };

export default function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Fetch clients
  const { data: clientsData, isLoading: clientsLoading } = useQuery({
    queryKey: ['search-clients', query],
    queryFn: () => clientsApi.getAll({ search: query, page_size: 5 }),
    enabled: isOpen && query.length >= 2,
    staleTime: 30000,
  });

  // Fetch obligations
  const { data: obligationsData, isLoading: obligationsLoading } = useQuery({
    queryKey: ['search-obligations', query],
    queryFn: () => obligationsApi.getAll({ search: query, page_size: 5 }),
    enabled: isOpen && query.length >= 2,
    staleTime: 30000,
  });

  const isLoading = clientsLoading || obligationsLoading;

  // Combine results
  const results: SearchResult[] = [];
  if (clientsData?.results) {
    clientsData.results.forEach((client: Client) => {
      results.push({ type: 'client', data: client });
    });
  }
  if (obligationsData?.results) {
    obligationsData.results.forEach((obligation: Obligation) => {
      results.push({ type: 'obligation', data: obligation });
    });
  }

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  // Reset selection when results change
  useEffect(() => {
    setSelectedIndex(0);
  }, [results.length]);

  // Navigate to result
  const navigateToResult = useCallback(
    (result: SearchResult) => {
      if (result.type === 'client') {
        navigate(`/clients?highlight=${result.data.id}`);
      } else {
        navigate(`/obligations?highlight=${result.data.id}`);
      }
      onClose();
    },
    [navigate, onClose]
  );

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          e.preventDefault();
          if (results[selectedIndex]) {
            navigateToResult(results[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex, navigateToResult, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] bg-black/50"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="w-full max-w-2xl bg-white rounded-xl shadow-2xl overflow-hidden">
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200">
          <Search size={20} className="text-gray-400 flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Αναζήτηση πελατών, υποχρεώσεων..."
            className="flex-1 text-lg outline-none placeholder-gray-400"
          />
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={18} className="text-gray-400" />
          </button>
        </div>

        {/* Results */}
        <div className="max-h-[60vh] overflow-y-auto">
          {query.length < 2 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <Search size={40} className="mx-auto mb-2 opacity-50" />
              <p>Πληκτρολογήστε τουλάχιστον 2 χαρακτήρες</p>
              <p className="text-sm text-gray-400 mt-1">
                Αναζήτηση με επωνυμία, ΑΦΜ ή τύπο υποχρέωσης
              </p>
            </div>
          ) : isLoading ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <Loader2 size={24} className="mx-auto mb-2 animate-spin" />
              <p>Αναζήτηση...</p>
            </div>
          ) : results.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <p>Δεν βρέθηκαν αποτελέσματα για "{query}"</p>
            </div>
          ) : (
            <div className="py-2">
              {/* Clients section */}
              {clientsData?.results && clientsData.results.length > 0 && (
                <div>
                  <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Πελάτες
                  </div>
                  {clientsData.results.map((client: Client, index: number) => {
                    const resultIndex = index;
                    return (
                      <button
                        key={`client-${client.id}`}
                        onClick={() => navigateToResult({ type: 'client', data: client })}
                        className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors ${
                          selectedIndex === resultIndex
                            ? 'bg-blue-50'
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <Users size={18} className="text-blue-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-900 truncate">
                            {client.eponimia}
                          </p>
                          <p className="text-sm text-gray-500">
                            ΑΦΜ: {client.afm}
                          </p>
                        </div>
                        {client.is_active === false && (
                          <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full">
                            Ανενεργός
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Obligations section */}
              {obligationsData?.results && obligationsData.results.length > 0 && (
                <div>
                  <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider border-t border-gray-100 mt-2">
                    Υποχρεώσεις
                  </div>
                  {obligationsData.results.map((obligation: Obligation, index: number) => {
                    const resultIndex = (clientsData?.results?.length || 0) + index;
                    const statusColors: Record<string, string> = {
                      pending: 'bg-yellow-100 text-yellow-700',
                      in_progress: 'bg-blue-100 text-blue-700',
                      completed: 'bg-green-100 text-green-700',
                      overdue: 'bg-red-100 text-red-700',
                      cancelled: 'bg-gray-100 text-gray-700',
                    };
                    return (
                      <button
                        key={`obligation-${obligation.id}`}
                        onClick={() =>
                          navigateToResult({ type: 'obligation', data: obligation })
                        }
                        className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors ${
                          selectedIndex === resultIndex
                            ? 'bg-blue-50'
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <ClipboardList size={18} className="text-purple-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-900 truncate">
                            {obligation.type_name || 'Υποχρέωση'} - {obligation.client_name}
                          </p>
                          <p className="text-sm text-gray-500">
                            {obligation.month}/{obligation.year} - Προθεσμία:{' '}
                            {new Date(obligation.deadline).toLocaleDateString('el-GR')}
                          </p>
                        </div>
                        <span
                          className={`px-2 py-0.5 text-xs rounded-full ${
                            statusColors[obligation.status] || 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          {obligation.status === 'pending' && 'Εκκρεμεί'}
                          {obligation.status === 'in_progress' && 'Σε εξέλιξη'}
                          {obligation.status === 'completed' && 'Ολοκληρώθηκε'}
                          {obligation.status === 'overdue' && 'Εκπρόθεσμη'}
                          {obligation.status === 'cancelled' && 'Ακυρώθηκε'}
                        </span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white border border-gray-200 rounded text-[10px]">
                  ↑↓
                </kbd>
                <span>Πλοήγηση</span>
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white border border-gray-200 rounded text-[10px]">
                  Enter
                </kbd>
                <span>Επιλογή</span>
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white border border-gray-200 rounded text-[10px]">
                  Esc
                </kbd>
                <span>Κλείσιμο</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
