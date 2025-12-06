import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  User,
  Users,
  Bell,
  Shield,
  Globe,
  Database,
  Mail,
  Phone,
  Save,
  FileText,
  ChevronRight,
} from 'lucide-react';
import { Button } from '../components';
import { useAuthStore } from '../stores/authStore';

type SettingsTab = 'profile' | 'notifications' | 'security' | 'integrations';

export default function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const { user } = useAuthStore();

  const tabs = [
    { id: 'profile' as const, label: 'Προφίλ', icon: User },
    { id: 'notifications' as const, label: 'Ειδοποιήσεις', icon: Bell },
    { id: 'security' as const, label: 'Ασφάλεια', icon: Shield },
    { id: 'integrations' as const, label: 'Ενσωματώσεις', icon: Database },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Ρυθμίσεις</h1>
        <p className="text-gray-500 mt-1">Διαχείριση λογαριασμού και προτιμήσεων</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar Tabs */}
        <div className="lg:w-64 flex-shrink-0">
          <nav className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-700 border-l-2 border-blue-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <tab.icon size={18} />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'profile' && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Στοιχεία προφίλ</h3>

              {/* Avatar */}
              <div className="flex items-center gap-4 mb-6 pb-6 border-b border-gray-200">
                <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-3xl text-white font-bold">
                    {user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'Χ'}
                  </span>
                </div>
                <div>
                  <Button variant="secondary" size="sm">Αλλαγή φωτογραφίας</Button>
                  <p className="text-xs text-gray-500 mt-1">JPG, PNG έως 5MB</p>
                </div>
              </div>

              {/* Form */}
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Όνομα</label>
                    <input
                      type="text"
                      defaultValue={user?.first_name || ''}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Επώνυμο</label>
                    <input
                      type="text"
                      defaultValue={user?.last_name || ''}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    defaultValue={user?.email || ''}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Όνομα χρήστη</label>
                  <input
                    type="text"
                    defaultValue={user?.username || ''}
                    disabled
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">Το όνομα χρήστη δεν μπορεί να αλλάξει</p>
                </div>

                <div className="pt-4">
                  <Button>
                    <Save size={18} className="mr-2" />
                    Αποθήκευση αλλαγών
                  </Button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Ρυθμίσεις ειδοποιήσεων</h3>

              <div className="space-y-4">
                {[
                  { title: 'Email υπενθυμίσεων', desc: 'Λήψη email για επερχόμενες υποχρεώσεις', enabled: true },
                  { title: 'Email για εκπρόθεσμες', desc: 'Ειδοποίηση όταν μια υποχρέωση καθυστερεί', enabled: true },
                  { title: 'Νέα αρχεία', desc: 'Ειδοποίηση όταν προστίθεται νέο αρχείο', enabled: false },
                  { title: 'Αναπάντητες κλήσεις', desc: 'Ειδοποίηση για αναπάντητες κλήσεις', enabled: true },
                  { title: 'Εβδομαδιαία σύνοψη', desc: 'Αναφορά προόδου κάθε Δευτέρα', enabled: false },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{item.title}</p>
                      <p className="text-sm text-gray-500">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked={item.enabled} />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                ))}
              </div>

              <div className="pt-6">
                <Button>
                  <Save size={18} className="mr-2" />
                  Αποθήκευση ρυθμίσεων
                </Button>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Αλλαγή κωδικού</h3>

                <div className="space-y-4 max-w-md">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Τρέχων κωδικός</label>
                    <input
                      type="password"
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Νέος κωδικός</label>
                    <input
                      type="password"
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Επιβεβαίωση νέου κωδικού</label>
                    <input
                      type="password"
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <Button>Αλλαγή κωδικού</Button>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Συνδεδεμένες συνεδρίες</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                        <Globe size={18} className="text-green-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Τρέχουσα συνεδρία</p>
                        <p className="text-xs text-gray-500">Chrome · Linux · Athens, GR</p>
                      </div>
                    </div>
                    <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded">Ενεργή</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'integrations' && (
            <div className="space-y-6">
              {/* Quick Links */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Obligation Settings */}
                <Link
                  to="/settings/obligations"
                  className="block bg-white rounded-lg border border-gray-200 p-6 hover:border-blue-300 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FileText size={24} className="text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">Υποχρεώσεις</h3>
                        <p className="text-sm text-gray-500">Τύποι, προφίλ, ομάδες</p>
                      </div>
                    </div>
                    <ChevronRight className="text-gray-400" size={20} />
                  </div>
                </Link>

                {/* User Management - Only for staff/superuser */}
                {user?.is_staff && (
                  <Link
                    to="/settings/users"
                    className="block bg-white rounded-lg border border-gray-200 p-6 hover:border-purple-300 hover:shadow-md transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                          <Users size={24} className="text-purple-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">Χρήστες</h3>
                          <p className="text-sm text-gray-500">Διαχείριση λογαριασμών</p>
                        </div>
                      </div>
                      <ChevronRight className="text-gray-400" size={20} />
                    </div>
                  </Link>
                )}
              </div>

              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Ενσωματώσεις</h3>

                <div className="space-y-4">
                {[
                  {
                    name: 'Fritz!Box VoIP',
                    desc: 'Σύνδεση με τηλεφωνικό κέντρο Fritz!Box',
                    icon: Phone,
                    status: 'connected'
                  },
                  {
                    name: 'Zadarma',
                    desc: 'Cloud PBX και click-to-call',
                    icon: Phone,
                    status: 'disconnected'
                  },
                  {
                    name: 'SMTP Email',
                    desc: 'Αποστολή email μέσω SMTP server',
                    icon: Mail,
                    status: 'connected'
                  },
                  {
                    name: 'MyData ΑΑΔΕ',
                    desc: 'Σύνδεση με την πλατφόρμα myDATA',
                    icon: Database,
                    status: 'disconnected'
                  },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                        <item.icon size={24} className="text-gray-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{item.name}</p>
                        <p className="text-sm text-gray-500">{item.desc}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {item.status === 'connected' ? (
                        <>
                          <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded">Συνδεδεμένο</span>
                          <Button variant="secondary" size="sm">Ρυθμίσεις</Button>
                        </>
                      ) : (
                        <Button size="sm">Σύνδεση</Button>
                      )}
                    </div>
                  </div>
                ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
