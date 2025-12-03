import { useAuthStore } from '../stores/authStore';
import { LayoutDashboard, Users, FileText, LogOut } from 'lucide-react';

export default function Dashboard() {
  const { logout } = useAuthStore();

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

        {/* Quick Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100 text-blue-600">
                <Users className="w-6 h-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Πελάτες</p>
                <p className="text-2xl font-semibold text-gray-900">-</p>
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
                <p className="text-2xl font-semibold text-gray-900">-</p>
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
                <p className="text-2xl font-semibold text-gray-900">-</p>
              </div>
            </div>
          </div>
        </div>

        {/* Placeholder for future content */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Πρόσφατη Δραστηριότητα
          </h3>
          <p className="text-gray-500">
            Η σελίδα είναι υπό κατασκευή. Σύντομα θα μπορείτε να δείτε πρόσφατες ενέργειες εδώ.
          </p>
        </div>
      </main>
    </div>
  );
}
