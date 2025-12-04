import { Link } from 'react-router-dom';
import { useDashboardStats } from '../hooks/useDashboard';
import { Users, FileText, AlertCircle, RefreshCw, ArrowRight, Clock, TrendingUp } from 'lucide-react';
import { Button } from '../components';

export default function Dashboard() {
  const { data: stats, isLoading, isError, error, refetch } = useDashboardStats();

  const renderStatValue = (value: number | undefined) => {
    if (isLoading) return '...';
    if (isError || value === undefined) return '-';
    return value;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Καλώς ήρθατε στο LogistikoCRM</h1>
        <p className="text-gray-600 mt-1">
          Διαχειριστείτε πελάτες και υποχρεώσεις εύκολα και γρήγορα.
        </p>
      </div>

      {/* Error Banner */}
      {isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <span className="text-red-700">
                Σφάλμα φόρτωσης δεδομένων: {error instanceof Error ? error.message : 'Άγνωστο σφάλμα'}
              </span>
            </div>
            <Button variant="secondary" size="sm" onClick={() => refetch()}>
              <RefreshCw className="w-4 h-4 mr-1" />
              Επανάληψη
            </Button>
          </div>
        </div>
      )}

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-blue-100">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Πελάτες</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {renderStatValue(stats?.total_clients)}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-yellow-100">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Εκκρεμείς</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {renderStatValue(stats?.total_obligations_pending)}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-green-100">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Ολοκληρώθηκαν</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {renderStatValue(stats?.total_obligations_completed_this_month)}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-red-100">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Εκπρόθεσμες</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {renderStatValue(stats?.overdue_count)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Γρήγορες Ενέργειες</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            to="/clients"
            className="flex items-center justify-between p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors group"
          >
            <div className="flex items-center">
              <Users className="w-5 h-5 text-blue-600 mr-3" />
              <span className="text-blue-900 font-medium">Διαχείριση Πελατών</span>
            </div>
            <ArrowRight className="w-5 h-5 text-blue-600 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link
            to="/obligations"
            className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors group"
          >
            <div className="flex items-center">
              <FileText className="w-5 h-5 text-yellow-600 mr-3" />
              <span className="text-yellow-900 font-medium">Διαχείριση Υποχρεώσεων</span>
            </div>
            <ArrowRight className="w-5 h-5 text-yellow-600 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Επερχόμενες Προθεσμίες</h3>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : stats?.upcoming_deadlines && stats.upcoming_deadlines.length > 0 ? (
          <div className="space-y-3">
            <p className="text-sm text-gray-600 mb-2">
              Προθεσμίες τις επόμενες 7 ημέρες:
            </p>
            {stats.upcoming_deadlines.slice(0, 5).map((deadline) => (
              <div
                key={deadline.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div>
                  <p className="font-medium text-gray-900">{deadline.client_name}</p>
                  <p className="text-sm text-gray-500">
                    {deadline.type} - {deadline.type_code}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{deadline.deadline}</p>
                  <p className={`text-sm font-medium ${
                    deadline.days_until <= 2 ? 'text-red-600' : 'text-gray-500'
                  }`}>
                    {deadline.days_until === 0
                      ? 'Σήμερα!'
                      : deadline.days_until === 1
                      ? 'Αύριο'
                      : `Σε ${deadline.days_until} ημέρες`}
                  </p>
                </div>
              </div>
            ))}
            {stats.upcoming_deadlines.length > 5 && (
              <Link
                to="/obligations"
                className="block text-center text-sm text-blue-600 hover:text-blue-700 font-medium py-2"
              >
                Προβολή όλων ({stats.upcoming_deadlines.length} προθεσμίες)
              </Link>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">
            Δεν υπάρχουν επερχόμενες προθεσμίες τις επόμενες 7 ημέρες.
          </p>
        )}
      </div>
    </div>
  );
}
