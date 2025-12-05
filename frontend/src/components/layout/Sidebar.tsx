import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  ClipboardList,
  Calendar,
  FolderOpen,
  Phone,
  Ticket,
  Mail,
  BarChart3,
  Settings,
  X,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  to: string;
  icon: React.ReactNode;
  label: string;
}

const navItems: NavItem[] = [
  { to: '/', icon: <LayoutDashboard size={20} />, label: 'Πίνακας Ελέγχου' },
  { to: '/clients', icon: <Users size={20} />, label: 'Πελάτες' },
  { to: '/obligations', icon: <ClipboardList size={20} />, label: 'Υποχρεώσεις' },
  { to: '/calendar', icon: <Calendar size={20} />, label: 'Ημερολόγιο' },
  { to: '/files', icon: <FolderOpen size={20} />, label: 'Αρχεία' },
  { to: '/calls', icon: <Phone size={20} />, label: 'Κλήσεις' },
  { to: '/tickets', icon: <Ticket size={20} />, label: 'Αιτήματα' },
  { to: '/emails', icon: <Mail size={20} />, label: 'Αλληλογραφία' },
  { to: '/reports', icon: <BarChart3 size={20} />, label: 'Αναφορές' },
  { to: '/settings', icon: <Settings size={20} />, label: 'Ρυθμίσεις' },
];

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-64 bg-white border-r border-gray-200
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:z-auto
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo/Brand */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">LC</span>
            </div>
            <span className="text-lg font-semibold text-gray-900">LogistikoCRM</span>
          </div>
          {/* Mobile close button */}
          <button
            onClick={onClose}
            className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Κλείσιμο μενού"
          >
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
              end={item.to === '/'}
            >
              <span className="flex-shrink-0">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-400 text-center">
            LogistikoCRM v1.0
          </div>
        </div>
      </aside>
    </>
  );
}
