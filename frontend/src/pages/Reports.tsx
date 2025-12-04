import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Calendar,
  Download,
  Filter,
  Users,
  ClipboardList,
} from 'lucide-react';
import { Button } from '../components';

export default function Reports() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Αναφορές</h1>
          <p className="text-gray-500 mt-1">Στατιστικά και αναλύσεις</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary">
            <Filter size={18} className="mr-2" />
            Φίλτρα
          </Button>
          <Button>
            <Download size={18} className="mr-2" />
            Εξαγωγή
          </Button>
        </div>
      </div>

      {/* Date Range Selector */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="flex items-center gap-2">
            <Calendar size={18} className="text-gray-400" />
            <span className="text-sm text-gray-600">Περίοδος:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-lg font-medium">
              Σήμερα
            </button>
            <button className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
              Εβδομάδα
            </button>
            <button className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
              Μήνας
            </button>
            <button className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
              Τρίμηνο
            </button>
            <button className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
              Έτος
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users size={24} className="text-blue-600" />
            </div>
            <div className="flex items-center gap-1 text-green-600 text-sm">
              <TrendingUp size={16} />
              <span>+12%</span>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-1">Συνολικοί πελάτες</p>
          <p className="text-2xl font-bold text-gray-900">248</p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <ClipboardList size={24} className="text-green-600" />
            </div>
            <div className="flex items-center gap-1 text-green-600 text-sm">
              <TrendingUp size={16} />
              <span>+8%</span>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-1">Ολοκληρωμένες</p>
          <p className="text-2xl font-bold text-gray-900">1,245</p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <ClipboardList size={24} className="text-yellow-600" />
            </div>
            <div className="flex items-center gap-1 text-red-600 text-sm">
              <TrendingDown size={16} />
              <span>-3%</span>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-1">Σε εκκρεμότητα</p>
          <p className="text-2xl font-bold text-gray-900">67</p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <ClipboardList size={24} className="text-red-600" />
            </div>
            <div className="flex items-center gap-1 text-red-600 text-sm">
              <TrendingUp size={16} />
              <span>+2</span>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-1">Εκπρόθεσμες</p>
          <p className="text-2xl font-bold text-gray-900">5</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Obligations by Type */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Υποχρεώσεις ανά τύπο</h3>
          <div className="space-y-4">
            {[
              { type: 'ΦΠΑ', count: 450, color: 'bg-blue-500' },
              { type: 'ΑΠΔ', count: 380, color: 'bg-green-500' },
              { type: 'ΕΝΦΙΑ', count: 120, color: 'bg-yellow-500' },
              { type: 'Ε1', count: 95, color: 'bg-purple-500' },
              { type: 'Ε3', count: 85, color: 'bg-pink-500' },
              { type: 'ΜΥΦ', count: 115, color: 'bg-orange-500' },
            ].map((item) => (
              <div key={item.type}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{item.type}</span>
                  <span className="text-gray-900 font-medium">{item.count}</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.color} rounded-full transition-all`}
                    style={{ width: `${(item.count / 450) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Monthly Activity */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Μηνιαία δραστηριότητα</h3>
          <div className="flex items-end justify-between h-48 gap-2">
            {[
              { month: 'Ιαν', value: 65 },
              { month: 'Φεβ', value: 78 },
              { month: 'Μαρ', value: 82 },
              { month: 'Απρ', value: 95 },
              { month: 'Μαι', value: 88 },
              { month: 'Ιουν', value: 72 },
              { month: 'Ιουλ', value: 85 },
              { month: 'Αυγ', value: 45 },
              { month: 'Σεπ', value: 92 },
              { month: 'Οκτ', value: 98 },
              { month: 'Νοε', value: 100 },
              { month: 'Δεκ', value: 75 },
            ].map((item) => (
              <div key={item.month} className="flex-1 flex flex-col items-center gap-2">
                <div
                  className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                  style={{ height: `${item.value}%` }}
                />
                <span className="text-xs text-gray-500">{item.month}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Διαθέσιμες αναφορές</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {[
            { name: 'Αναφορά πελατών', description: 'Πλήρης λίστα πελατών με στοιχεία επικοινωνίας', icon: Users },
            { name: 'Αναφορά υποχρεώσεων', description: 'Κατάσταση υποχρεώσεων ανά μήνα', icon: ClipboardList },
            { name: 'Οικονομική αναφορά', description: 'Έσοδα και στατιστικά χρεώσεων', icon: TrendingUp },
            { name: 'Αναφορά απόδοσης', description: 'Χρόνοι ολοκλήρωσης και KPIs', icon: BarChart3 },
          ].map((report, index) => (
            <div key={index} className="flex items-center justify-between p-4 hover:bg-gray-50">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                  <report.icon size={20} className="text-gray-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{report.name}</p>
                  <p className="text-sm text-gray-500">{report.description}</p>
                </div>
              </div>
              <Button variant="secondary" size="sm">
                <Download size={16} className="mr-2" />
                Λήψη
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
