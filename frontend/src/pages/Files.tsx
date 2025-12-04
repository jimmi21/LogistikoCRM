import { FolderOpen, Upload, Search, Filter } from 'lucide-react';
import { Button } from '../components';

export default function Files() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Αρχεία</h1>
          <p className="text-gray-500 mt-1">Διαχείριση εγγράφων και αρχείων πελατών</p>
        </div>
        <Button>
          <Upload size={18} className="mr-2" />
          Μεταφόρτωση
        </Button>
      </div>

      {/* Search and Filter Bar */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Αναζήτηση αρχείων..."
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Filter size={18} />
            <span>Φίλτρα</span>
          </button>
        </div>
      </div>

      {/* Empty State */}
      <div className="bg-white rounded-lg border border-gray-200 p-12">
        <div className="text-center">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FolderOpen size={32} className="text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Διαχείριση Αρχείων
          </h3>
          <p className="text-gray-500 max-w-md mx-auto mb-6">
            Εδώ θα μπορείτε να διαχειρίζεστε όλα τα αρχεία και τα έγγραφα των πελατών σας.
            Η λειτουργία αυτή βρίσκεται υπό ανάπτυξη.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button variant="secondary">Μάθετε περισσότερα</Button>
            <Button>
              <Upload size={18} className="mr-2" />
              Μεταφόρτωση αρχείου
            </Button>
          </div>
        </div>
      </div>

      {/* Feature Preview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-4">
            <FolderOpen size={20} className="text-green-600" />
          </div>
          <h4 className="font-semibold text-gray-900 mb-2">Οργάνωση φακέλων</h4>
          <p className="text-sm text-gray-500">
            Αυτόματη δημιουργία φακέλων ανά πελάτη και τύπο υποχρέωσης
          </p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <Search size={20} className="text-purple-600" />
          </div>
          <h4 className="font-semibold text-gray-900 mb-2">Αναζήτηση</h4>
          <p className="text-sm text-gray-500">
            Γρήγορη αναζήτηση αρχείων με full-text search
          </p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
            <Upload size={20} className="text-orange-600" />
          </div>
          <h4 className="font-semibold text-gray-900 mb-2">Drag & Drop</h4>
          <p className="text-sm text-gray-500">
            Εύκολη μεταφόρτωση αρχείων με drag and drop
          </p>
        </div>
      </div>
    </div>
  );
}
