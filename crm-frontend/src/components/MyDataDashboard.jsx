import React, { useState, useEffect } from 'react';
import {
    FileText,
    TrendingUp,
    TrendingDown,
    RefreshCw,
    CheckCircle,
    XCircle,
    AlertCircle,
    Calendar,
    ChevronLeft,
    ChevronRight,
    Building2,
    Receipt,
    Wallet,
    ArrowUpRight,
    ArrowDownRight,
    Loader2
} from 'lucide-react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    LineChart,
    Line,
    Legend
} from 'recharts';
import { mydataAPI } from '../services/api';

// Greek month names
const MONTHS = [
    'Ιανουάριος', 'Φεβρουάριος', 'Μάρτιος', 'Απρίλιος',
    'Μάιος', 'Ιούνιος', 'Ιούλιος', 'Αύγουστος',
    'Σεπτέμβριος', 'Οκτώβριος', 'Νοέμβριος', 'Δεκέμβριος'
];

// VAT category colors
const VAT_COLORS = {
    1: '#3b82f6', // 24% - Blue
    2: '#8b5cf6', // 13% - Purple
    3: '#10b981', // 6% - Green
    4: '#f59e0b', // 17% - Amber
    5: '#ef4444', // 9% - Red
    6: '#06b6d4', // 4% - Cyan
    7: '#6b7280', // 0% - Gray
    8: '#9ca3af', // No VAT - Light gray
};

// Format currency
const formatCurrency = (value) => {
    const num = parseFloat(value) || 0;
    return new Intl.NumberFormat('el-GR', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 2,
    }).format(num);
};

// Format number
const formatNumber = (value) => {
    const num = parseFloat(value) || 0;
    return new Intl.NumberFormat('el-GR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(num);
};

// Stat Card Component
const StatCard = ({ title, value, subtitle, icon: Icon, trend, trendValue, color = 'blue' }) => {
    const colorClasses = {
        blue: 'bg-blue-50 text-blue-600',
        green: 'bg-green-50 text-green-600',
        red: 'bg-red-50 text-red-600',
        purple: 'bg-purple-50 text-purple-600',
        amber: 'bg-amber-50 text-amber-600',
    };

    return (
        <div className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
                    <Icon size={24} />
                </div>
                {trend && (
                    <span className={`text-sm font-medium flex items-center gap-1 ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                        {trend === 'up' ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                        {trendValue}
                    </span>
                )}
            </div>
            <h3 className="text-gray-500 text-sm font-medium mb-1">{title}</h3>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
    );
};

// Client Row Component
const ClientRow = ({ client, onSelect }) => {
    const { client_afm, client_name, is_verified, last_sync, current_period } = client;
    const vatBalance = parseFloat(current_period.vat_difference) || 0;

    return (
        <tr
            className="hover:bg-gray-50 cursor-pointer transition-colors"
            onClick={() => onSelect(client_afm)}
        >
            <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-sm font-semibold mr-3">
                        {client_name.charAt(0)}
                    </div>
                    <div>
                        <p className="text-sm font-medium text-gray-900">{client_name}</p>
                        <p className="text-xs text-gray-500">{client_afm}</p>
                    </div>
                </div>
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                {is_verified ? (
                    <span className="inline-flex items-center gap-1 text-green-600 text-sm">
                        <CheckCircle size={16} />
                        Ενεργό
                    </span>
                ) : (
                    <span className="inline-flex items-center gap-1 text-yellow-600 text-sm">
                        <AlertCircle size={16} />
                        Μη επιβεβ.
                    </span>
                )}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                <span className="text-green-600 font-medium">
                    {formatCurrency(current_period.income_net)}
                </span>
                <p className="text-xs text-gray-400">
                    ΦΠΑ: {formatCurrency(current_period.income_vat)}
                </p>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                <span className="text-red-600 font-medium">
                    {formatCurrency(current_period.expense_net)}
                </span>
                <p className="text-xs text-gray-400">
                    ΦΠΑ: {formatCurrency(current_period.expense_vat)}
                </p>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                <span className={`font-bold ${vatBalance >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {formatCurrency(vatBalance)}
                </span>
                <p className="text-xs text-gray-400">
                    {vatBalance >= 0 ? 'Πληρωτέο' : 'Πιστωτικό'}
                </p>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {last_sync ? new Date(last_sync).toLocaleDateString('el-GR') : '-'}
            </td>
        </tr>
    );
};

// Main Dashboard Component
const MyDataDashboard = ({ onBack }) => {
    // State
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [dashboardData, setDashboardData] = useState(null);
    const [trendData, setTrendData] = useState(null);
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
    const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
    const [selectedClient, setSelectedClient] = useState(null);
    const [syncing, setSyncing] = useState(false);

    // Fetch data
    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [dashboard, trend] = await Promise.all([
                mydataAPI.getDashboard(selectedYear, selectedMonth),
                mydataAPI.getTrend(null, 6),
            ]);
            setDashboardData(dashboard);
            setTrendData(trend);
        } catch (err) {
            console.error('Failed to fetch myDATA dashboard:', err);
            setError('Αποτυχία φόρτωσης δεδομένων');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [selectedYear, selectedMonth]);

    // Navigate months
    const navigateMonth = (direction) => {
        let newMonth = selectedMonth + direction;
        let newYear = selectedYear;

        if (newMonth < 1) {
            newMonth = 12;
            newYear -= 1;
        } else if (newMonth > 12) {
            newMonth = 1;
            newYear += 1;
        }

        setSelectedMonth(newMonth);
        setSelectedYear(newYear);
    };

    // Handle sync all
    const handleSyncAll = async () => {
        setSyncing(true);
        try {
            // TODO: Implement sync all functionality
            await fetchData();
        } catch (err) {
            console.error('Sync failed:', err);
        } finally {
            setSyncing(false);
        }
    };

    // Loading state
    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-96">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                <span className="ml-2 text-gray-600">Φόρτωση δεδομένων myDATA...</span>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-96">
                <XCircle className="w-12 h-12 text-red-500 mb-4" />
                <p className="text-gray-600 mb-4">{error}</p>
                <button
                    onClick={fetchData}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                    Επανάληψη
                </button>
            </div>
        );
    }

    const { overview, clients } = dashboardData || { overview: {}, clients: [] };

    // Calculate totals
    const totalIncomeVat = parseFloat(overview.total_income_vat) || 0;
    const totalExpenseVat = parseFloat(overview.total_expense_vat) || 0;
    const vatBalance = totalIncomeVat - totalExpenseVat;

    // Prepare chart data
    const vatCategoryData = [];
    const categoryTotals = {};

    clients.forEach(client => {
        client.income_by_category?.forEach(cat => {
            if (!categoryTotals[cat.vat_category]) {
                categoryTotals[cat.vat_category] = { income: 0, expense: 0 };
            }
            categoryTotals[cat.vat_category].income += parseFloat(cat.vat_amount) || 0;
        });
        client.expense_by_category?.forEach(cat => {
            if (!categoryTotals[cat.vat_category]) {
                categoryTotals[cat.vat_category] = { income: 0, expense: 0 };
            }
            categoryTotals[cat.vat_category].expense += parseFloat(cat.vat_amount) || 0;
        });
    });

    Object.entries(categoryTotals).forEach(([category, totals]) => {
        vatCategoryData.push({
            name: `${category === '8' ? 'Χωρίς ΦΠΑ' : category + '%'}`,
            income: totals.income,
            expense: totals.expense,
            color: VAT_COLORS[parseInt(category)] || '#6b7280',
        });
    });

    // Trend chart data
    const trendChartData = trendData?.data?.map(item => ({
        name: item.month_name,
        income: parseFloat(item.income_vat) || 0,
        expense: parseFloat(item.expense_vat) || 0,
        balance: parseFloat(item.vat_balance) || 0,
    })) || [];

    return (
        <div className="p-8 max-w-7xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                    {onBack && (
                        <button
                            onClick={onBack}
                            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                            <ChevronLeft size={24} />
                        </button>
                    )}
                    <div>
                        <h2 className="text-3xl font-bold text-gray-900">myDATA Dashboard</h2>
                        <p className="text-gray-500 mt-1">
                            Επισκόπηση ΦΠΑ από ΑΑΔΕ Ηλεκτρονικά Βιβλία
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    {/* Month Navigation */}
                    <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-3 py-2">
                        <button
                            onClick={() => navigateMonth(-1)}
                            className="p-1 hover:bg-gray-100 rounded"
                        >
                            <ChevronLeft size={18} />
                        </button>
                        <span className="min-w-32 text-center font-medium">
                            {MONTHS[selectedMonth - 1]} {selectedYear}
                        </span>
                        <button
                            onClick={() => navigateMonth(1)}
                            className="p-1 hover:bg-gray-100 rounded"
                        >
                            <ChevronRight size={18} />
                        </button>
                    </div>

                    {/* Sync Button */}
                    <button
                        onClick={handleSyncAll}
                        disabled={syncing}
                        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                    >
                        <RefreshCw size={20} className={syncing ? 'animate-spin' : ''} />
                        {syncing ? 'Συγχρονισμός...' : 'Ανανέωση'}
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-5 gap-4 mb-8">
                <StatCard
                    title="Πελάτες με myDATA"
                    value={`${overview.clients_with_credentials || 0} / ${overview.total_clients || 0}`}
                    subtitle="Με credentials"
                    icon={Building2}
                    color="blue"
                />
                <StatCard
                    title="Επιβεβαιωμένα"
                    value={overview.verified_credentials || 0}
                    subtitle="Verified credentials"
                    icon={CheckCircle}
                    color="green"
                />
                <StatCard
                    title="Εκροές (ΦΠΑ)"
                    value={formatCurrency(totalIncomeVat)}
                    subtitle="Έσοδα περιόδου"
                    icon={TrendingUp}
                    color="green"
                />
                <StatCard
                    title="Εισροές (ΦΠΑ)"
                    value={formatCurrency(totalExpenseVat)}
                    subtitle="Έξοδα περιόδου"
                    icon={TrendingDown}
                    color="red"
                />
                <StatCard
                    title="Υπόλοιπο ΦΠΑ"
                    value={formatCurrency(vatBalance)}
                    subtitle={vatBalance >= 0 ? 'Πληρωτέο' : 'Πιστωτικό'}
                    icon={Wallet}
                    color={vatBalance >= 0 ? 'red' : 'green'}
                />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-2 gap-6 mb-8">
                {/* Trend Chart */}
                <div className="bg-white rounded-xl p-6 border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        Εξέλιξη ΦΠΑ (6 μήνες)
                    </h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <LineChart data={trendChartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="name" stroke="#94a3b8" />
                            <YAxis stroke="#94a3b8" tickFormatter={(v) => `${(v/1000).toFixed(0)}k`} />
                            <Tooltip
                                formatter={(value) => formatCurrency(value)}
                                labelStyle={{ fontWeight: 'bold' }}
                            />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="income"
                                name="Εκροές"
                                stroke="#10b981"
                                strokeWidth={2}
                                dot={{ fill: '#10b981' }}
                            />
                            <Line
                                type="monotone"
                                dataKey="expense"
                                name="Εισροές"
                                stroke="#ef4444"
                                strokeWidth={2}
                                dot={{ fill: '#ef4444' }}
                            />
                            <Line
                                type="monotone"
                                dataKey="balance"
                                name="Υπόλοιπο"
                                stroke="#3b82f6"
                                strokeWidth={2}
                                strokeDasharray="5 5"
                                dot={{ fill: '#3b82f6' }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* VAT Category Chart */}
                <div className="bg-white rounded-xl p-6 border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        ΦΠΑ ανά Κατηγορία
                    </h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={vatCategoryData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="name" stroke="#94a3b8" />
                            <YAxis stroke="#94a3b8" tickFormatter={(v) => `${(v/1000).toFixed(0)}k`} />
                            <Tooltip formatter={(value) => formatCurrency(value)} />
                            <Legend />
                            <Bar dataKey="income" name="Εκροές" fill="#10b981" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="expense" name="Εισροές" fill="#ef4444" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Clients Table */}
            <div className="bg-white rounded-xl border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900">
                        Πελάτες - {MONTHS[selectedMonth - 1]} {selectedYear}
                    </h3>
                </div>

                {clients.length === 0 ? (
                    <div className="p-12 text-center">
                        <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-500">Δεν υπάρχουν πελάτες με myDATA credentials</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Πελάτης
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Κατάσταση
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Εκροές
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Εισροές
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Υπόλοιπο ΦΠΑ
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Τελ. Sync
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {clients.map((client) => (
                                    <ClientRow
                                        key={client.client_afm}
                                        client={client}
                                        onSelect={setSelectedClient}
                                    />
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MyDataDashboard;
