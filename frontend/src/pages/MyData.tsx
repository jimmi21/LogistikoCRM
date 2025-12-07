import { useState, useMemo } from 'react';
import {
  RefreshCw, ChevronLeft, ChevronRight, AlertCircle, CheckCircle,
  TrendingUp, TrendingDown, Minus, Info, Building2, Calendar
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell
} from 'recharts';
import { Button } from '../components';
import {
  useMyDataClients,
  useClientVATDetail,
  useVATTrend,
  useSyncVAT,
  formatCurrency,
  formatVATResult,
  getVATResultColor,
  getVATResultBg,
  getVATResultLabel,
  GREEK_MONTHS,
  getMonthName,
} from '../hooks/useMyData';

// VAT category colors for charts
const VAT_COLORS: Record<number, string> = {
  1: '#3B82F6', // 24% - blue
  2: '#10B981', // 13% - green
  3: '#F59E0B', // 6% - amber
  4: '#8B5CF6', // 17% - purple
  5: '#EC4899', // 9% - pink
  6: '#06B6D4', // 4% - cyan
  7: '#6B7280', // 0% - gray
  8: '#9CA3AF', // χωρίς - light gray
};

export default function MyData() {
  const today = new Date();
  const [selectedClientId, setSelectedClientId] = useState<number | null>(null);
  const [selectedAfm, setSelectedAfm] = useState<string | null>(null);
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);

  // Queries
  const { data: clients, isLoading: loadingClients } = useMyDataClients();
  const { data: clientDetail, isLoading: loadingDetail, refetch: refetchDetail } = useClientVATDetail(selectedAfm, year, month);
  const { data: trendData } = useVATTrend(selectedAfm || undefined, 6);

  // Mutations
  const syncMutation = useSyncVAT();

  // Find selected client details
  const selectedClient = useMemo(() => {
    if (!clients || !selectedClientId) return null;
    return clients.find(c => c.id === selectedClientId);
  }, [clients, selectedClientId]);

  // Handle client selection
  const handleClientChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value ? Number(e.target.value) : null;
    setSelectedClientId(id);

    const client = clients?.find(c => c.id === id);
    setSelectedAfm(client?.client_afm || null);
  };

  // Handle month navigation
  const handlePrevMonth = () => {
    if (month === 1) {
      setMonth(12);
      setYear(y => y - 1);
    } else {
      setMonth(m => m - 1);
    }
  };

  const handleNextMonth = () => {
    if (month === 12) {
      setMonth(1);
      setYear(y => y + 1);
    } else {
      setMonth(m => m + 1);
    }
  };

  // Handle sync
  const handleSync = async () => {
    if (!selectedClientId) return;
    await syncMutation.mutateAsync({
      credentialsId: selectedClientId,
      year,
      month,
    });
    refetchDetail();
  };

  // Prepare chart data
  const incomeChartData = clientDetail?.income_by_category?.map(item => ({
    name: item.vat_rate_display,
    value: parseFloat(item.vat_amount),
    net: parseFloat(item.net_value),
    count: item.count,
    category: item.vat_category,
  })).filter(d => d.value > 0) || [];

  const expenseChartData = clientDetail?.expense_by_category?.map(item => ({
    name: item.vat_rate_display,
    value: parseFloat(item.vat_amount),
    net: parseFloat(item.net_value),
    count: item.count,
    category: item.vat_category,
  })).filter(d => d.value > 0) || [];

  // Prepare trend chart data
  const trendChartData = trendData?.data?.map(item => ({
    month: item.month_name,
    'ΦΠΑ Εκροών': parseFloat(item.income_vat),
    'ΦΠΑ Εισροών': parseFloat(item.expense_vat),
    'Διαφορά': parseFloat(item.vat_balance),
  })) || [];

  // VAT result
  const vatResult = clientDetail?.summary?.vat_difference;

  return (
    <div className="space-y-4">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Building2 className="w-7 h-7 text-blue-600" />
            myDATA - Αποτέλεσμα ΦΠΑ
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Παρακολούθηση ΦΠΑ από τα ηλεκτρονικά βιβλία ΑΑΔΕ
          </p>
        </div>
      </div>

      {/* Client & Period Selection */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Client Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Πελάτης
            </label>
            {loadingClients ? (
              <div className="h-10 bg-gray-100 rounded-lg animate-pulse" />
            ) : clients && clients.length > 0 ? (
              <select
                className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={selectedClientId || ''}
                onChange={handleClientChange}
              >
                <option value="">-- Επιλέξτε πελάτη --</option>
                {clients.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.client_name || c.client_afm} ({c.client_afm})
                    {!c.is_verified && ' ⚠️'}
                  </option>
                ))}
              </select>
            ) : (
              <div className="text-gray-500 text-sm p-2">
                Δεν υπάρχουν πελάτες με myDATA credentials.
                Προσθέστε από την καρτέλα πελάτη → Στοιχεία → myDATA ΑΑΔΕ.
              </div>
            )}
          </div>

          {/* Period Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Περίοδος
            </label>
            <div className="flex items-center gap-2">
              <button
                onClick={handlePrevMonth}
                className="p-2.5 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                title="Προηγούμενος μήνας"
              >
                <ChevronLeft size={20} />
              </button>
              <div className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-gray-50 rounded-lg">
                <Calendar size={16} className="text-gray-400" />
                <span className="font-medium">
                  {getMonthName(month)} {year}
                </span>
              </div>
              <button
                onClick={handleNextMonth}
                className="p-2.5 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                title="Επόμενος μήνας"
              >
                <ChevronRight size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* No Client Selected */}
      {!selectedClientId && (
        <div className="text-center py-16 bg-white rounded-lg border-2 border-dashed border-gray-200">
          <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">Επιλέξτε πελάτη για να δείτε τα δεδομένα ΦΠΑ</p>
        </div>
      )}

      {/* Client Selected - Show Data */}
      {selectedClientId && (
        <>
          {/* Credentials Warning */}
          {selectedClient && !selectedClient.is_verified && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium text-yellow-800">Credentials μη επιβεβαιωμένα</p>
                <p className="text-sm text-yellow-700 mt-1">
                  Τα credentials του πελάτη δεν έχουν επιβεβαιωθεί. Ελέγξτε τις ρυθμίσεις στο Django Admin.
                </p>
              </div>
            </div>
          )}

          {/* Main VAT Result Card */}
          <div className={`rounded-xl border-2 p-6 ${getVATResultBg(vatResult)}`}>
            <div className="text-center">
              <div className="text-sm font-medium text-gray-500 mb-1">
                ΑΠΟΤΕΛΕΣΜΑ ΦΠΑ
              </div>
              <div className="text-xs text-gray-400 mb-4">
                {getMonthName(month).toUpperCase()} {year}
              </div>

              {loadingDetail ? (
                <div className="py-8">
                  <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-2" />
                  <span className="text-gray-400">Φόρτωση...</span>
                </div>
              ) : (
                <>
                  {/* Main Amount */}
                  <div className={`text-5xl font-bold my-6 ${getVATResultColor(vatResult)}`}>
                    {formatVATResult(vatResult)}
                  </div>

                  {/* Result Label with Icon */}
                  <div className="flex items-center justify-center gap-2 text-xl">
                    {vatResult && parseFloat(vatResult) > 0 && (
                      <TrendingUp className="w-6 h-6 text-red-500" />
                    )}
                    {vatResult && parseFloat(vatResult) < 0 && (
                      <TrendingDown className="w-6 h-6 text-green-500" />
                    )}
                    {vatResult && parseFloat(vatResult) === 0 && (
                      <Minus className="w-6 h-6 text-gray-500" />
                    )}
                    <span className={getVATResultColor(vatResult)}>
                      {getVATResultLabel(vatResult)}
                    </span>
                  </div>

                  {/* Summary Stats */}
                  {clientDetail?.summary && (
                    <div className="grid grid-cols-2 gap-4 mt-8 pt-6 border-t border-current border-opacity-20">
                      <div className="text-center">
                        <p className="text-sm text-gray-500 mb-1">ΦΠΑ Εκροών</p>
                        <p className="text-lg font-semibold text-green-600">
                          {formatCurrency(clientDetail.summary.income_vat)}
                        </p>
                        <p className="text-xs text-gray-400">
                          {clientDetail.summary.income_count} εγγραφές
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-gray-500 mb-1">ΦΠΑ Εισροών</p>
                        <p className="text-lg font-semibold text-red-600">
                          {formatCurrency(clientDetail.summary.expense_vat)}
                        </p>
                        <p className="text-xs text-gray-400">
                          {clientDetail.summary.expense_count} εγγραφές
                        </p>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Sync Button & Last Update */}
              <div className="flex justify-between items-center mt-6 pt-4 border-t border-current border-opacity-20">
                <Button
                  onClick={handleSync}
                  disabled={syncMutation.isPending}
                  className="flex items-center gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${syncMutation.isPending ? 'animate-spin' : ''}`} />
                  {syncMutation.isPending ? 'Συγχρονισμός...' : 'Sync από myDATA'}
                </Button>

                <div className="text-xs text-gray-400 text-right">
                  {clientDetail?.credentials?.last_sync ? (
                    <>
                      Τελ. ενημέρωση:<br />
                      {new Date(clientDetail.credentials.last_sync).toLocaleString('el-GR')}
                    </>
                  ) : (
                    'Δεν έχει γίνει sync'
                  )}
                </div>
              </div>

              {/* Sync Error */}
              {syncMutation.isError && (
                <div className="mt-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded-lg text-sm">
                  Σφάλμα: {(syncMutation.error as Error)?.message || 'Άγνωστο σφάλμα'}
                </div>
              )}

              {/* Sync Success */}
              {syncMutation.isSuccess && (
                <div className="mt-4 p-3 bg-green-100 border border-green-300 text-green-700 rounded-lg text-sm flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Ο συγχρονισμός ολοκληρώθηκε επιτυχώς
                </div>
              )}
            </div>
          </div>

          {/* Charts Section */}
          {clientDetail && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Income by Category */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  ΦΠΑ Εκροών ανά Κατηγορία
                </h3>
                {incomeChartData.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={incomeChartData}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={2}
                          dataKey="value"
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          labelLine={false}
                        >
                          {incomeChartData.map((entry) => (
                            <Cell key={entry.category} fill={VAT_COLORS[entry.category]} />
                          ))}
                        </Pie>
                        <Tooltip
                          formatter={(value: number) => formatCurrency(value)}
                          labelFormatter={(name) => `ΦΠΑ ${name}`}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-400">
                    <div className="text-center">
                      <Info className="w-8 h-8 mx-auto mb-2" />
                      Δεν υπάρχουν δεδομένα εκροών
                    </div>
                  </div>
                )}
              </div>

              {/* Expense by Category */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <TrendingDown className="w-5 h-5 text-red-600" />
                  ΦΠΑ Εισροών ανά Κατηγορία
                </h3>
                {expenseChartData.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={expenseChartData}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={2}
                          dataKey="value"
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          labelLine={false}
                        >
                          {expenseChartData.map((entry) => (
                            <Cell key={entry.category} fill={VAT_COLORS[entry.category]} />
                          ))}
                        </Pie>
                        <Tooltip
                          formatter={(value: number) => formatCurrency(value)}
                          labelFormatter={(name) => `ΦΠΑ ${name}`}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-400">
                    <div className="text-center">
                      <Info className="w-8 h-8 mx-auto mb-2" />
                      Δεν υπάρχουν δεδομένα εισροών
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Monthly Trend Chart */}
          {trendChartData.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-blue-600" />
                Εξέλιξη ΦΠΑ (τελευταίοι 6 μήνες)
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={trendChartData}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`} />
                    <Tooltip
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Legend />
                    <Bar dataKey="ΦΠΑ Εκροών" fill="#22C55E" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="ΦΠΑ Εισροών" fill="#EF4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Πληροφορίες myDATA</p>
              <ul className="list-disc list-inside space-y-1 text-blue-700">
                <li>Τα δεδομένα προέρχονται από τα ηλεκτρονικά βιβλία της ΑΑΔΕ</li>
                <li>Θετικό αποτέλεσμα = ΦΠΑ για καταβολή (χρωστάτε)</li>
                <li>Αρνητικό αποτέλεσμα = ΦΠΑ προς επιστροφή/συμψηφισμό</li>
                <li>Τα δεδομένα είναι read-only - δεν γίνεται υποβολή στην ΑΑΔΕ</li>
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
