import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useClients } from '../hooks/useClients';
import { ArrowLeft, Users, Search, AlertCircle, RefreshCw } from 'lucide-react';

export default function Clients() {
  const [searchTerm, setSearchTerm] = useState('');
  const { data, isLoading, isError, error, refetch } = useClients();

  // Filter clients by name (onoma) or AFM
  const filteredClients = useMemo(() => {
    if (!data?.results) return [];
    if (!searchTerm.trim()) return data.results;

    const term = searchTerm.toLowerCase().trim();
    return data.results.filter(
      (client) =>
        client.onoma.toLowerCase().includes(term) ||
        client.afm.includes(term)
    );
  }, [data?.results, searchTerm]);

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
                <Users className="w-6 h-6 text-blue-600 mr-3" />
                <h1 className="text-2xl font-bold text-gray-900">Πελάτες</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Box */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Αναζήτηση με επωνυμία ή ΑΦΜ..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
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
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Φόρτωση πελατών...</p>
          </div>
        )}

        {/* Clients Table */}
        {!isLoading && !isError && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <p className="text-sm text-gray-500">
                {filteredClients.length} {filteredClients.length === 1 ? 'πελάτης' : 'πελάτες'}
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
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredClients.map((client) => (
                      <tr key={client.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-blue-600 font-medium text-sm">
                                {client.onoma.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {client.onoma}
                              </div>
                              {!client.is_active && (
                                <span className="inline-flex px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded">
                                  Ανενεργός
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="font-mono text-sm text-gray-900">{client.afm}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {client.phone || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {client.email || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
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
    </div>
  );
}
