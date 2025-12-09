import { useState, useEffect } from 'react';
import {
  FileText,
  TrendingUp,
  TrendingDown,
  Calendar,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  Clock,
  Users,
  Euro,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { Button, VATPeriodCalculator } from '../components';
import { mydataApi, type MyDataDashboardResponse, type TrendData } from '../api/client';

// VAT category labels
const VAT_CATEGORIES: Record<number, string> = {
  1: '24%',
  2: '13%',
  3: '6%',
  4: '17%',
  5: '9%',
  6: '4%',
  7: '0%',
  8: 'Απαλλαγή',
};

// Greek month names
const MONTHS = [
  'Ιανουάριος', 'Φεβρουάριος', 'Μάρτιος', 'Απρίλιος',
  'Μάιος', 'Ιούνιος', 'Ιούλιος', 'Αύγουστος',
  'Σεπτέμβριος', 'Οκτώβριος', 'Νοέμβριος', 'Δεκέμβριος'
];

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('el-GR', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
}

export default function MyData() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [dashboard, setDashboard] = useState<MyDataDashboardResponse | null>(null);
  const [trendData, setTrendData] = useState<TrendData[]>([]);

  // Period selection
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  // Fetch dashboard data
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashboardData, trend] = await Promise.all([
        mydataApi.getDashboard(year, month),
        mydataApi.getTrend(6),
      ]);
      setDashboard(dashboardData);
      setTrendData(trend);
    } catch (err) {
      console.error('Error fetching myDATA:', err);
      setError('Σφάλμα φόρτωσης δεδομένων myDATA');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [year, month]);

  // Navigate months
  const goToPreviousMonth = () => {
    if (month === 1) {
      setMonth(12);
      setYear(year - 1);
    } else {
      setMonth(month - 1);
    }
  };

  const goToNextMonth = () => {
    if (month === 12) {
      setMonth(1);
      setYear(year + 1);
    } else {
      setMonth(month + 1);
    }
  };

  // Sync all clients
  const handleSyncAll = async () => {
    setSyncing(true);
    try {
      // Get all credentials and sync them
      const credentials = await mydataApi.credentials.getAll();
      for (const cred of credentials.results || credentials) {
        try {
          await mydataApi.credentials.sync(cred.id, year, month);
        } catch (e) {
          console.error(`Failed to sync credential ${cred.id}:`, e);
        }
      }
      // Refresh dashboard
      await fetchData();
    } catch (err) {
      console.error('Sync error:', err);
      setError('Σφάλμα κατά τον συγχρονισμό');
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-red-700">{error}</p>
        <Button onClick={fetchData} className="mt-4">
          Δοκιμή ξανά
        </Button>
      </div>
    );
  }

  const totals = dashboard?.totals || {
    income_total: 0,
    income_vat: 0,
    expense_total: 0,
    expense_vat: 0,
    vat_due: 0,
    record_count: 0,
  };

  const syncStatus = dashboard?.sync_status || {
    total_clients: 0,
    synced_clients: 0,
    pending_clients: 0,
    failed_clients: 0,
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">myDATA - ΦΠΑ</h1>
          <p className="text-gray-500 mt-1">Δεδομένα από ΑΑΔΕ Ηλεκτρονικά Βιβλία</p>
        </div>
        <Button onClick={handleSyncAll} disabled={syncing}>
          <RefreshCw size={18} className={`mr-2 ${syncing ? 'animate-spin' : ''}`} />
          {syncing ? 'Συγχρονισμός...' : 'Συγχρονισμός όλων'}
        </Button>
      </div>

      {/* Period Selector */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <button
            onClick={goToPreviousMonth}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronLeft size={20} className="text-gray-600" />
          </button>
          <div className="flex items-center gap-2">
            <Calendar size={20} className="text-blue-600" />
            <span className="text-lg font-semibold text-gray-900">
              {MONTHS[month - 1]} {year}
            </span>
          </div>
          <button
            onClick={goToNextMonth}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={year === now.getFullYear() && month === now.getMonth() + 1}
          >
            <ChevronRight size={20} className="text-gray-600" />
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Εκροές (Income) */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <ArrowUpRight size={24} className="text-green-600" />
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">ΦΠΑ Εκροών</p>
              <p className="text-sm font-semibold text-green-600">{formatCurrency(totals.income_vat)}</p>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-1">Εκροές (Πωλήσεις)</p>
          <p className="text-2xl font-bold text-gray-900">{formatCurrency(totals.income_total)}</p>
        </div>

        {/* Εισροές (Expenses) */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <ArrowDownRight size={24} className="text-red-600" />
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">ΦΠΑ Εισροών</p>
              <p className="text-sm font-semibold text-red-600">{formatCurrency(totals.expense_vat)}</p>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-1">Εισροές (Αγορές)</p>
          <p className="text-2xl font-bold text-gray-900">{formatCurrency(totals.expense_total)}</p>
        </div>

        {/* ΦΠΑ προς απόδοση */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
              totals.vat_due >= 0 ? 'bg-yellow-100' : 'bg-blue-100'
            }`}>
              <Euro size={24} className={totals.vat_due >= 0 ? 'text-yellow-600' : 'text-blue-600'} />
            </div>
            {totals.vat_due >= 0 ? (
              <TrendingUp size={20} className="text-yellow-600" />
            ) : (
              <TrendingDown size={20} className="text-blue-600" />
            )}
          </div>
          <p className="text-sm text-gray-500 mb-1">
            {totals.vat_due >= 0 ? 'ΦΠΑ προς Απόδοση' : 'ΦΠΑ προς Επιστροφή'}
          </p>
          <p className={`text-2xl font-bold ${totals.vat_due >= 0 ? 'text-yellow-600' : 'text-blue-600'}`}>
            {formatCurrency(Math.abs(totals.vat_due))}
          </p>
        </div>

        {/* Sync Status */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users size={24} className="text-blue-600" />
            </div>
            <div className="flex items-center gap-1">
              <CheckCircle size={16} className="text-green-500" />
              <span className="text-sm text-green-600">{syncStatus.synced_clients}</span>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-1">Πελάτες</p>
          <p className="text-2xl font-bold text-gray-900">{syncStatus.total_clients}</p>
          {syncStatus.pending_clients > 0 && (
            <p className="text-xs text-yellow-600 mt-1">
              <Clock size={12} className="inline mr-1" />
              {syncStatus.pending_clients} εκκρεμούν
            </p>
          )}
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* VAT Trend */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Εξέλιξη ΦΠΑ (6 μήνες)</h3>
          {trendData.length > 0 ? (
            <div className="flex items-end justify-between h-48 gap-2">
              {trendData.map((item, index) => {
                const maxValue = Math.max(...trendData.map(d => Math.max(d.income, d.expense)));
                const incomeHeight = maxValue > 0 ? (item.income / maxValue) * 100 : 0;
                const expenseHeight = maxValue > 0 ? (item.expense / maxValue) * 100 : 0;
                return (
                  <div key={index} className="flex-1 flex flex-col items-center gap-1">
                    <div className="w-full flex gap-0.5 items-end h-40">
                      <div
                        className="flex-1 bg-green-500 rounded-t transition-all hover:bg-green-600"
                        style={{ height: `${incomeHeight}%` }}
                        title={`Εκροές: ${formatCurrency(item.income)}`}
                      />
                      <div
                        className="flex-1 bg-red-400 rounded-t transition-all hover:bg-red-500"
                        style={{ height: `${expenseHeight}%` }}
                        title={`Εισροές: ${formatCurrency(item.expense)}`}
                      />
                    </div>
                    <span className="text-xs text-gray-500">{item.period}</span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-gray-400">
              Δεν υπάρχουν δεδομένα
            </div>
          )}
          <div className="flex justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded" />
              <span className="text-sm text-gray-600">Εκροές</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-400 rounded" />
              <span className="text-sm text-gray-600">Εισροές</span>
            </div>
          </div>
        </div>

        {/* VAT by Category */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">ΦΠΑ ανά Κατηγορία</h3>
          <div className="space-y-4">
            {Object.entries(VAT_CATEGORIES).map(([cat, label]) => {
              const categoryNum = parseInt(cat);
              // Find data for this category from all clients
              let categoryVat = 0;
              dashboard?.clients?.forEach(client => {
                client.by_category?.forEach(bc => {
                  if (bc.vat_category === categoryNum) {
                    categoryVat += bc.total_vat;
                  }
                });
              });

              const maxVat = totals.income_vat + totals.expense_vat || 1;
              const percentage = (categoryVat / maxVat) * 100;

              if (categoryVat === 0) return null;

              return (
                <div key={cat}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">ΦΠΑ {label}</span>
                    <span className="text-gray-900 font-medium">{formatCurrency(categoryVat)}</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full transition-all"
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Clients Table */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Πελάτες - ΦΠΑ Μήνα</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Πελάτης</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">ΑΦΜ</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase">Εκροές</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase">Εισροές</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase">ΦΠΑ</th>
                <th className="text-center px-6 py-3 text-xs font-medium text-gray-500 uppercase">Κατάσταση</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {dashboard?.clients && dashboard.clients.length > 0 ? (
                dashboard.clients.map((client, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <FileText size={16} className="text-blue-600" />
                        </div>
                        <span className="font-medium text-gray-900">{client.client_name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600 font-mono">{client.afm}</td>
                    <td className="px-6 py-4 text-right text-green-600 font-medium">
                      {formatCurrency(client.summary?.income_total || 0)}
                    </td>
                    <td className="px-6 py-4 text-right text-red-600 font-medium">
                      {formatCurrency(client.summary?.expense_total || 0)}
                    </td>
                    <td className="px-6 py-4 text-right font-bold">
                      <span className={client.summary?.vat_due >= 0 ? 'text-yellow-600' : 'text-blue-600'}>
                        {formatCurrency(Math.abs(client.summary?.vat_due || 0))}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      {client.has_credentials ? (
                        client.last_sync ? (
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                            <CheckCircle size={12} />
                            Ενημερωμένο
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                            <Clock size={12} />
                            Εκκρεμεί
                          </span>
                        )
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          <AlertCircle size={12} />
                          Χωρίς credentials
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    <FileText size={48} className="mx-auto mb-4 text-gray-300" />
                    <p>Δεν υπάρχουν δεδομένα για αυτή την περίοδο</p>
                    <p className="text-sm mt-2">Προσθέστε credentials για τους πελάτες σας στις Ρυθμίσεις</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* VAT Period Calculator */}
      <VATPeriodCalculator />
    </div>
  );
}
