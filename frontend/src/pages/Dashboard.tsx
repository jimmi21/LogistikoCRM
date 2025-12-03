import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useDashboardStats } from '../hooks/useDashboard';
import { LayoutDashboard, Users, FileText, LogOut, AlertCircle, RefreshCw, ArrowRight } from 'lucide-react';

export default function Dashboard() {
  const { logout } = useAuthStore();
  const { data: stats, isLoading, isError, error, refetch } = useDashboardStats();

  const renderStatValue = (value: number | undefined) => {
    if (isLoading) return '...';
    if (isError || value === undefined) return '-';
    return value;
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            LogistikoCRM
          </h1>
          <button
            onClick={logout}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Αποσύνδεση
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800">
            Καλώς ήρθατε στο LogistikoCRM
          </h2>
          <p className="text-gray-600 mt-1">
            Διαχειριστείτε πελάτες και υποχρεώσεις εύκολα και γρήγορα.
          </p>
        </div>

        {/* Error Banner */}
        {isError && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                <span className="text-red-700">
                  Σφάλμα φόρτωσης δεδομένων: {error instanceof Error ? error.message : 'Άγνωστο σφάλμα'}
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

        {/* Quick Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100 text-blue-600">
                <Users className="w-6 h-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Πελάτες</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {renderStatValue(stats?.total_clients)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-yellow-100 text-yellow-600">
                <FileText className="w-6 h-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Εκκρεμείς Υποχρεώσεις</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {renderStatValue(stats?.total_obligations_pending)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100 text-green-600">
                <LayoutDashboard className="w-6 h-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Ολοκληρώθηκαν (μήνας)</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {renderStatValue(stats?.total_obligations_completed_this_month)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Γρήγορες Ενέργειες
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link
              to="/clients"
              className="flex items-center justify-between p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <div className="flex items-center">
                <Users className="w-5 h-5 text-blue-600 mr-3" />
                <span className="text-blue-900 font-medium">Διαχείριση Πελατών</span>
              </div>
              <ArrowRight className="w-5 h-5 text-blue-600" />
            </Link>
            <Link
              to="/obligations"
              className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors"
            >
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-yellow-600 mr-3" />
                <span className="text-yellow-900 font-medium">Διαχείριση Υποχρεώσεων</span>
              </div>
              <ArrowRight className="w-5 h-5 text-yellow-600" />
            </Link>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Πρόσφατη Δραστηριότητα
          </h3>
          {isLoading ? (
            <p className="text-gray-500">Φόρτωση...</p>
          ) : stats?.upcoming_deadlines && stats.upcoming_deadlines.length > 0 ? (
            <div className="space-y-3">
              <p className="text-sm text-gray-600 mb-2">
                Επερχόμενες προθεσμίες (επόμενες 7 ημέρες):
              </p>
              {stats.upcoming_deadlines.slice(0, 5).map((deadline) => (
                <div
                  key={deadline.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">{deadline.client_name}</p>
                    <p className="text-sm text-gray-500">
                      {deadline.type} - {deadline.type_code}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{deadline.deadline}</p>
                    <p className={`text-sm ${deadline.days_until <= 2 ? 'text-red-600' : 'text-gray-500'}`}>
                      {deadline.days_until === 0
                        ? 'Σήμερα'
                        : deadline.days_until === 1
                        ? 'Αύριο'
                        : `Σε ${deadline.days_until} ημέρες`}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">
              Δεν υπάρχουν επερχόμενες προθεσμίες τις επόμενες 7 ημέρες.
            </p>
          )}
        </div>
      </main>
    </div>
  );
}
