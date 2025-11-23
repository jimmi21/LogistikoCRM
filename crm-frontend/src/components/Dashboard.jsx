import React, { useState } from 'react';
import { LayoutDashboard, Users, Calendar, CheckSquare, Bell, Search, Plus, TrendingUp, DollarSign, AlertCircle, ChevronRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const mockStats = {
    totalClients: 127,
    activeObligations: 45,
    completedThisMonth: 82,
    revenue: 45230
};

const mockRecentObligations = [
    { id: 1, client: 'Acme Corp', type: 'ΦΠΑ', dueDate: '2025-10-15', status: 'pending', priority: 'high' },
    { id: 2, client: 'Tech Solutions', type: 'Μισθοδοσία', dueDate: '2025-10-12', status: 'in_progress', priority: 'medium' },
    { id: 3, client: 'Green Energy SA', type: 'ΕΝΦΙΑ', dueDate: '2025-10-20', status: 'pending', priority: 'low' },
    { id: 4, client: 'Marketing Plus', type: 'Φορολογική Δήλωση', dueDate: '2025-10-18', status: 'completed', priority: 'high' },
    { id: 5, client: 'Retail Store', type: 'ΦΠΑ', dueDate: '2025-10-25', status: 'pending', priority: 'medium' },
];

const monthlyData = [
    { month: 'Μάι', completed: 65, pending: 12 },
    { month: 'Ιούν', completed: 78, pending: 15 },
    { month: 'Ιούλ', completed: 82, pending: 10 },
    { month: 'Αύγ', completed: 71, pending: 18 },
    { month: 'Σεπ', completed: 89, pending: 8 },
    { month: 'Οκτ', completed: 82, pending: 45 },
];

const obligationTypeData = [
    { name: 'ΦΠΑ', value: 35, color: '#3b82f6' },
    { name: 'Μισθοδοσία', value: 28, color: '#8b5cf6' },
    { name: 'ΕΝΦΙΑ', value: 20, color: '#10b981' },
    { name: 'Άλλα', value: 17, color: '#f59e0b' },
];

const CRMDashboard = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedStatus, setSelectedStatus] = useState('all');

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'bg-green-100 text-green-800';
            case 'in_progress': return 'bg-blue-100 text-blue-800';
            case 'pending': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'high': return 'text-red-600';
            case 'medium': return 'text-yellow-600';
            case 'low': return 'text-green-600';
            default: return 'text-gray-600';
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case 'completed': return 'Ολοκληρωμένο';
            case 'in_progress': return 'Σε εξέλιξη';
            case 'pending': return 'Εκκρεμεί';
            default: return status;
        }
    };

    return (
        <div className="flex min-h-screen bg-gray-50">
            {/* Sidebar - Fixed */}
            <div className="fixed left-0 top-0 h-screen w-64 bg-white border-r border-gray-200 flex flex-col">
                <div className="p-6 border-b border-gray-200">
                    <h1 className="text-2xl font-bold text-gray-900">CRM System</h1>
                    <p className="text-sm text-gray-500 mt-1">Accounting Suite</p>
                </div>

                <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                    {[
                        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
                        { id: 'clients', label: 'Πελάτες', icon: Users },
                        { id: 'tasks', label: 'Εργασίες', icon: CheckSquare },
                        { id: 'calendar', label: 'Ημερολόγιο', icon: Calendar },
                    ].map((item) => {
                        const Icon = item.icon;
                        return (
                            <button
                                key={item.id}
                                onClick={() => setActiveTab(item.id)}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${activeTab === item.id
                                        ? 'bg-blue-50 text-blue-700 font-medium'
                                        : 'text-gray-700 hover:bg-gray-50'
                                    }`}
                            >
                                <Icon size={20} />
                                <span>{item.label}</span>
                            </button>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-gray-200">
                    <div className="flex items-center gap-3 px-4 py-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                            JD
                        </div>
                        <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">John Doe</p>
                            <p className="text-xs text-gray-500">Λογιστής</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content - With left margin for sidebar */}
            <div className="flex-1 ml-64">
                <div className="p-8 max-w-7xl">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
                            <p className="text-gray-500 mt-1">Καλωσήρθες πίσω! Ορίστε μια επισκόπηση των δραστηριοτήτων σου.</p>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type="text"
                                    placeholder="Αναζήτηση..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
                                />
                            </div>
                            <button className="p-2 rounded-lg hover:bg-gray-100 relative">
                                <Bell size={20} className="text-gray-600" />
                                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                            </button>
                            <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                                <Plus size={20} />
                                Νέα Εργασία
                            </button>
                        </div>
                    </div>

                    {/* Stats Cards */}
                    <div className="grid grid-cols-4 gap-6 mb-8">
                        <div className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-blue-50 rounded-lg">
                                    <Users className="text-blue-600" size={24} />
                                </div>
                                <span className="text-green-600 text-sm font-medium">+12%</span>
                            </div>
                            <h3 className="text-gray-500 text-sm font-medium mb-1">Συνολικοί Πελάτες</h3>
                            <p className="text-3xl font-bold text-gray-900">{mockStats.totalClients}</p>
                        </div>

                        <div className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-yellow-50 rounded-lg">
                                    <AlertCircle className="text-yellow-600" size={24} />
                                </div>
                                <span className="text-yellow-600 text-sm font-medium">Εκκρεμείς</span>
                            </div>
                            <h3 className="text-gray-500 text-sm font-medium mb-1">Ενεργές Υποχρεώσεις</h3>
                            <p className="text-3xl font-bold text-gray-900">{mockStats.activeObligations}</p>
                        </div>

                        <div className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-green-50 rounded-lg">
                                    <CheckSquare className="text-green-600" size={24} />
                                </div>
                                <span className="text-green-600 text-sm font-medium">+8%</span>
                            </div>
                            <h3 className="text-gray-500 text-sm font-medium mb-1">Ολοκληρωμένα (Μήνας)</h3>
                            <p className="text-3xl font-bold text-gray-900">{mockStats.completedThisMonth}</p>
                        </div>

                        <div className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-purple-50 rounded-lg">
                                    <DollarSign className="text-purple-600" size={24} />
                                </div>
                                <span className="text-green-600 text-sm font-medium">+15%</span>
                            </div>
                            <h3 className="text-gray-500 text-sm font-medium mb-1">Έσοδα Μήνα</h3>
                            <p className="text-3xl font-bold text-gray-900">€{mockStats.revenue.toLocaleString()}</p>
                        </div>
                    </div>

                    {/* Charts Section */}
                    <div className="grid grid-cols-3 gap-6 mb-8">
                        <div className="col-span-2 bg-white rounded-xl p-6 border border-gray-200">
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-lg font-semibold text-gray-900">Μηνιαία Απόδοση</h3>
                                <select className="px-3 py-1 border border-gray-300 rounded-lg text-sm">
                                    <option>Τελευταίοι 6 μήνες</option>
                                    <option>Τελευταίοι 12 μήνες</option>
                                </select>
                            </div>
                            <ResponsiveContainer width="100%" height={280}>
                                <BarChart data={monthlyData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                    <XAxis dataKey="month" stroke="#94a3b8" />
                                    <YAxis stroke="#94a3b8" />
                                    <Tooltip />
                                    <Bar dataKey="completed" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                                    <Bar dataKey="pending" fill="#f59e0b" radius={[8, 8, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="bg-white rounded-xl p-6 border border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900 mb-6">Τύποι Υποχρεώσεων</h3>
                            <ResponsiveContainer width="100%" height={200}>
                                <PieChart>
                                    <Pie
                                        data={obligationTypeData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {obligationTypeData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                </PieChart>
                            </ResponsiveContainer>
                            <div className="mt-4 space-y-2">
                                {obligationTypeData.map((item) => (
                                    <div key={item.name} className="flex items-center justify-between text-sm">
                                        <div className="flex items-center gap-2">
                                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                                            <span className="text-gray-700">{item.name}</span>
                                        </div>
                                        <span className="font-semibold text-gray-900">{item.value}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Recent Obligations Table */}
                    <div className="bg-white rounded-xl border border-gray-200">
                        <div className="p-6 border-b border-gray-200">
                            <div className="flex items-center justify-between">
                                <h3 className="text-lg font-semibold text-gray-900">Πρόσφατες Υποχρεώσεις</h3>
                                <div className="flex gap-2">
                                    {['all', 'pending', 'in_progress', 'completed'].map((status) => (
                                        <button
                                            key={status}
                                            onClick={() => setSelectedStatus(status)}
                                            className={`px-3 py-1 rounded-lg text-sm transition-colors ${selectedStatus === status
                                                    ? 'bg-blue-100 text-blue-700 font-medium'
                                                    : 'text-gray-600 hover:bg-gray-100'
                                                }`}
                                        >
                                            {status === 'all' ? 'Όλα' : getStatusText(status)}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-50 border-b border-gray-200">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Πελάτης
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Τύπος
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Προθεσμία
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Προτεραιότητα
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Κατάσταση
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Ενέργειες
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {mockRecentObligations.map((obligation) => (
                                        <tr key={obligation.id} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="flex items-center">
                                                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-sm font-semibold mr-3">
                                                        {obligation.client.charAt(0)}
                                                    </div>
                                                    <span className="text-sm font-medium text-gray-900">{obligation.client}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                                                {obligation.type}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                                                {obligation.dueDate}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`text-sm font-medium ${getPriorityColor(obligation.priority)}`}>
                                                    {obligation.priority === 'high' ? 'Υψηλή' : obligation.priority === 'medium' ? 'Μεσαία' : 'Χαμηλή'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(obligation.status)}`}>
                                                    {getStatusText(obligation.status)}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <button className="text-blue-600 hover:text-blue-800 font-medium text-sm flex items-center gap-1">
                                                    Προβολή
                                                    <ChevronRight size={16} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CRMDashboard;