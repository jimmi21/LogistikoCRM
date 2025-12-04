import { Phone, PhoneIncoming, PhoneOutgoing, PhoneMissed, Search, Filter } from 'lucide-react';
import { Button } from '../components';

// Mock data for demonstration
const recentCalls = [
  { id: 1, type: 'incoming', number: '+30 210 1234567', client: 'ΕΤΑΙΡΕΙΑ Α.Ε.', duration: '3:45', time: '10:30', date: '04/12/2025' },
  { id: 2, type: 'outgoing', number: '+30 697 8901234', client: 'ΕΠΙΧΕΙΡΗΣΗ ΕΠΕ', duration: '5:12', time: '09:15', date: '04/12/2025' },
  { id: 3, type: 'missed', number: '+30 211 5678901', client: 'Άγνωστος', duration: '-', time: '08:42', date: '04/12/2025' },
];

export default function Calls() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Κλήσεις</h1>
          <p className="text-gray-500 mt-1">Ιστορικό κλήσεων και VoIP ενσωμάτωση</p>
        </div>
        <Button>
          <Phone size={18} className="mr-2" />
          Νέα κλήση
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <PhoneIncoming size={20} className="text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Εισερχόμενες</p>
              <p className="text-xl font-bold text-gray-900">24</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <PhoneOutgoing size={20} className="text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Εξερχόμενες</p>
              <p className="text-xl font-bold text-gray-900">18</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <PhoneMissed size={20} className="text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Αναπάντητες</p>
              <p className="text-xl font-bold text-gray-900">5</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Phone size={20} className="text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Σήμερα</p>
              <p className="text-xl font-bold text-gray-900">12</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Αναζήτηση με αριθμό ή πελάτη..."
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Filter size={18} />
            <span>Φίλτρα</span>
          </button>
        </div>
      </div>

      {/* Calls Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Τύπος
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Αριθμός
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Πελάτης
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Διάρκεια
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ημ/νία
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {recentCalls.map((call) => (
                <tr key={call.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    {call.type === 'incoming' && (
                      <div className="flex items-center gap-2 text-green-600">
                        <PhoneIncoming size={18} />
                        <span className="text-sm">Εισερχόμενη</span>
                      </div>
                    )}
                    {call.type === 'outgoing' && (
                      <div className="flex items-center gap-2 text-blue-600">
                        <PhoneOutgoing size={18} />
                        <span className="text-sm">Εξερχόμενη</span>
                      </div>
                    )}
                    {call.type === 'missed' && (
                      <div className="flex items-center gap-2 text-red-600">
                        <PhoneMissed size={18} />
                        <span className="text-sm">Αναπάντητη</span>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{call.number}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{call.client}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{call.duration}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {call.date} {call.time}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Info Banner */}
        <div className="px-6 py-4 bg-blue-50 border-t border-blue-100">
          <p className="text-sm text-blue-700">
            <strong>Σημείωση:</strong> Για πλήρη λειτουργικότητα VoIP, απαιτείται ρύθμιση
            σύνδεσης με Fritz!Box ή Zadarma. Επικοινωνήστε με τον διαχειριστή.
          </p>
        </div>
      </div>
    </div>
  );
}
