import { useState } from 'react';
import {
  Send,
  FileText,
  Clock,
  Zap,
  History,
  Plus,
  Edit2,
  Trash2,
  Copy,
  Play,
  Power,
  Eye,
  X,
  Search,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { Button, Modal, ConfirmDialog } from '../components';
import { EmailComposer, TemplateForm, AutomationForm } from '../components/email';
import {
  useEmailTemplates,
  useCreateEmailTemplate,
  useUpdateEmailTemplate,
  useDeleteEmailTemplate,
  useDuplicateEmailTemplate,
  useEmailVariables,
  useScheduledEmails,
  useCancelScheduledEmail,
  useSendScheduledNow,
  useEmailAutomations,
  useCreateEmailAutomation,
  useUpdateEmailAutomation,
  useDeleteEmailAutomation,
  useToggleEmailAutomation,
  useEmailLogs,
  useSendEmail,
} from '../hooks/useEmails';
import type {
  EmailTemplate,
  EmailTemplateFormData,
  ScheduledEmail,
  ScheduledEmailStatus,
  EmailAutomationRule,
  EmailAutomationRuleFormData,
  EmailLog,
  EmailLogStatus,
  SendEmailData,
} from '../types';

type TabType = 'compose' | 'templates' | 'scheduled' | 'automations' | 'history';

const TABS: { id: TabType; label: string; icon: React.ReactNode }[] = [
  { id: 'compose', label: 'Σύνθεση', icon: <Send size={18} /> },
  { id: 'templates', label: 'Πρότυπα', icon: <FileText size={18} /> },
  { id: 'scheduled', label: 'Προγραμματισμένα', icon: <Clock size={18} /> },
  { id: 'automations', label: 'Αυτοματισμοί', icon: <Zap size={18} /> },
  { id: 'history', label: 'Ιστορικό', icon: <History size={18} /> },
];

// Status badges
const getStatusBadge = (status: ScheduledEmailStatus | EmailLogStatus) => {
  const styles: Record<string, { bg: string; text: string; icon: React.ReactNode }> = {
    pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: <Clock size={14} /> },
    sent: { bg: 'bg-green-100', text: 'text-green-800', icon: <CheckCircle size={14} /> },
    failed: { bg: 'bg-red-100', text: 'text-red-800', icon: <XCircle size={14} /> },
    cancelled: { bg: 'bg-gray-100', text: 'text-gray-800', icon: <X size={14} /> },
  };

  const labels: Record<string, string> = {
    pending: 'Εκκρεμεί',
    sent: 'Στάλθηκε',
    failed: 'Απέτυχε',
    cancelled: 'Ακυρώθηκε',
  };

  const style = styles[status] || styles.pending;

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${style.bg} ${style.text}`}>
      {style.icon}
      {labels[status] || status}
    </span>
  );
};

export default function Emails() {
  const [activeTab, setActiveTab] = useState<TabType>('compose');

  // Template state
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);
  const [deletingTemplateId, setDeletingTemplateId] = useState<number | null>(null);

  // Automation state
  const [isAutomationModalOpen, setIsAutomationModalOpen] = useState(false);
  const [editingAutomation, setEditingAutomation] = useState<EmailAutomationRule | null>(null);
  const [deletingAutomationId, setDeletingAutomationId] = useState<number | null>(null);

  // Scheduled state
  const [scheduledStatusFilter, setScheduledStatusFilter] = useState<ScheduledEmailStatus | ''>('');
  const [scheduledPage, setScheduledPage] = useState(1);
  const [cancellingId, setCancellingId] = useState<number | null>(null);

  // History state
  const [historyStatusFilter, setHistoryStatusFilter] = useState<EmailLogStatus | ''>('');
  const [historySearch, setHistorySearch] = useState('');
  const [historyPage, setHistoryPage] = useState(1);
  const [viewingEmail, setViewingEmail] = useState<EmailLog | null>(null);

  // Queries
  const { data: templates, isLoading: templatesLoading } = useEmailTemplates();
  const { data: variables } = useEmailVariables();
  const { data: scheduledData, isLoading: scheduledLoading } = useScheduledEmails({
    status: scheduledStatusFilter || undefined,
    page: scheduledPage,
    page_size: 15,
  });
  const { data: automations, isLoading: automationsLoading } = useEmailAutomations();
  const { data: historyData, isLoading: historyLoading } = useEmailLogs({
    status: historyStatusFilter || undefined,
    search: historySearch || undefined,
    page: historyPage,
    page_size: 15,
  });

  // Mutations
  const createTemplate = useCreateEmailTemplate();
  const updateTemplate = useUpdateEmailTemplate(editingTemplate?.id || 0);
  const deleteTemplate = useDeleteEmailTemplate();
  const duplicateTemplate = useDuplicateEmailTemplate();

  const createAutomation = useCreateEmailAutomation();
  const updateAutomation = useUpdateEmailAutomation(editingAutomation?.id || 0);
  const deleteAutomation = useDeleteEmailAutomation();
  const toggleAutomation = useToggleEmailAutomation();

  const cancelScheduled = useCancelScheduledEmail();
  const sendNow = useSendScheduledNow();

  const sendEmail = useSendEmail();

  // Handlers
  const handleCreateTemplate = () => {
    setEditingTemplate(null);
    setIsTemplateModalOpen(true);
  };

  const handleEditTemplate = (template: EmailTemplate) => {
    setEditingTemplate(template);
    setIsTemplateModalOpen(true);
  };

  const handleTemplateSubmit = async (data: EmailTemplateFormData) => {
    try {
      if (editingTemplate) {
        await updateTemplate.mutateAsync(data);
      } else {
        await createTemplate.mutateAsync(data);
      }
      setIsTemplateModalOpen(false);
      setEditingTemplate(null);
    } catch (error) {
      console.error('Error saving template:', error);
    }
  };

  const handleDeleteTemplate = async () => {
    if (deletingTemplateId) {
      await deleteTemplate.mutateAsync(deletingTemplateId);
      setDeletingTemplateId(null);
    }
  };

  const handleDuplicateTemplate = async (id: number) => {
    await duplicateTemplate.mutateAsync(id);
  };

  const handleCreateAutomation = () => {
    setEditingAutomation(null);
    setIsAutomationModalOpen(true);
  };

  const handleEditAutomation = (automation: EmailAutomationRule) => {
    setEditingAutomation(automation);
    setIsAutomationModalOpen(true);
  };

  const handleAutomationSubmit = async (data: EmailAutomationRuleFormData) => {
    try {
      if (editingAutomation) {
        await updateAutomation.mutateAsync(data);
      } else {
        await createAutomation.mutateAsync(data);
      }
      setIsAutomationModalOpen(false);
      setEditingAutomation(null);
    } catch (error) {
      console.error('Error saving automation:', error);
    }
  };

  const handleDeleteAutomation = async () => {
    if (deletingAutomationId) {
      await deleteAutomation.mutateAsync(deletingAutomationId);
      setDeletingAutomationId(null);
    }
  };

  const handleToggleAutomation = async (id: number) => {
    await toggleAutomation.mutateAsync(id);
  };

  const handleCancelScheduled = async () => {
    if (cancellingId) {
      await cancelScheduled.mutateAsync(cancellingId);
      setCancellingId(null);
    }
  };

  const handleSendNow = async (id: number) => {
    await sendNow.mutateAsync(id);
  };

  const handleSendEmail = async (data: SendEmailData & { schedule_at?: string }) => {
    await sendEmail.mutateAsync(data);
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('el-GR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Email</h1>
          <p className="text-gray-500 mt-1">Διαχείριση email και αυτοματοποιήσεις</p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-4 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg border border-gray-200">
        {/* Compose Tab */}
        {activeTab === 'compose' && (
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Σύνθεση Email</h2>
            <EmailComposer
              onSend={handleSendEmail}
              isLoading={sendEmail.isPending}
            />
          </div>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Πρότυπα Email</h2>
              <Button onClick={handleCreateTemplate}>
                <Plus size={18} className="mr-2" />
                Νέο Πρότυπο
              </Button>
            </div>

            {templatesLoading ? (
              <div className="text-center py-8 text-gray-500">Φόρτωση...</div>
            ) : templates && templates.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {templates.map((template: EmailTemplate) => (
                  <div
                    key={template.id}
                    className={`border rounded-lg p-4 hover:border-blue-300 transition-colors ${
                      !template.is_active ? 'opacity-60' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-medium text-gray-900">{template.name}</h3>
                        {template.obligation_type_name && (
                          <span className="inline-block mt-1 px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded">
                            {template.obligation_type_name}
                          </span>
                        )}
                      </div>
                      <span
                        className={`w-2 h-2 rounded-full ${
                          template.is_active ? 'bg-green-500' : 'bg-gray-300'
                        }`}
                        title={template.is_active ? 'Ενεργό' : 'Ανενεργό'}
                      />
                    </div>
                    <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                      {template.description || template.subject}
                    </p>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleEditTemplate(template)}
                        className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                        title="Επεξεργασία"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        onClick={() => handleDuplicateTemplate(template.id)}
                        className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
                        title="Αντιγραφή"
                      >
                        <Copy size={16} />
                      </button>
                      <button
                        onClick={() => setDeletingTemplateId(template.id)}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="Διαγραφή"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <FileText size={48} className="mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Δεν υπάρχουν πρότυπα
                </h3>
                <p className="text-gray-500 mb-4">
                  Δημιουργήστε το πρώτο σας πρότυπο email
                </p>
                <Button onClick={handleCreateTemplate}>
                  <Plus size={18} className="mr-2" />
                  Νέο Πρότυπο
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Scheduled Tab */}
        {activeTab === 'scheduled' && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Προγραμματισμένα Email</h2>
              <select
                value={scheduledStatusFilter}
                onChange={(e) => {
                  setScheduledStatusFilter(e.target.value as ScheduledEmailStatus | '');
                  setScheduledPage(1);
                }}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Όλες οι καταστάσεις</option>
                <option value="pending">Εκκρεμεί</option>
                <option value="sent">Στάλθηκε</option>
                <option value="failed">Απέτυχε</option>
                <option value="cancelled">Ακυρώθηκε</option>
              </select>
            </div>

            {scheduledLoading ? (
              <div className="text-center py-8 text-gray-500">Φόρτωση...</div>
            ) : scheduledData && scheduledData.results.length > 0 ? (
              <>
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                          Παραλήπτης
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                          Θέμα
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                          Προγραμματισμός
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                          Κατάσταση
                        </th>
                        <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                          Ενέργειες
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {scheduledData.results.map((scheduled: ScheduledEmail) => (
                        <tr key={scheduled.id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4">
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                {scheduled.recipients_display || scheduled.recipient_name}
                              </p>
                              {scheduled.client_name && (
                                <p className="text-xs text-gray-500">{scheduled.client_name}</p>
                              )}
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <p className="text-sm text-gray-900 line-clamp-1">
                              {scheduled.subject}
                            </p>
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-600">
                            {formatDateTime(scheduled.send_at)}
                          </td>
                          <td className="py-3 px-4">
                            {getStatusBadge(scheduled.status)}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <div className="flex items-center justify-end gap-2">
                              {scheduled.status === 'pending' && (
                                <>
                                  <button
                                    onClick={() => handleSendNow(scheduled.id)}
                                    className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
                                    title="Αποστολή τώρα"
                                  >
                                    <Play size={16} />
                                  </button>
                                  <button
                                    onClick={() => setCancellingId(scheduled.id)}
                                    className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                                    title="Ακύρωση"
                                  >
                                    <X size={16} />
                                  </button>
                                </>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {scheduledData.count > 15 && (
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm text-gray-500">
                      Σύνολο: {scheduledData.count} εγγραφές
                    </p>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setScheduledPage((p) => Math.max(1, p - 1))}
                        disabled={!scheduledData.previous}
                      >
                        <ChevronLeft size={16} />
                      </Button>
                      <span className="text-sm text-gray-600">
                        Σελίδα {scheduledPage}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setScheduledPage((p) => p + 1)}
                        disabled={!scheduledData.next}
                      >
                        <ChevronRight size={16} />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <Clock size={48} className="mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Δεν υπάρχουν προγραμματισμένα email
                </h3>
                <p className="text-gray-500">
                  Τα προγραμματισμένα email θα εμφανιστούν εδώ
                </p>
              </div>
            )}
          </div>
        )}

        {/* Automations Tab */}
        {activeTab === 'automations' && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Κανόνες Αυτοματοποίησης</h2>
              <Button onClick={handleCreateAutomation}>
                <Plus size={18} className="mr-2" />
                Νέος Κανόνας
              </Button>
            </div>

            {automationsLoading ? (
              <div className="text-center py-8 text-gray-500">Φόρτωση...</div>
            ) : automations && automations.length > 0 ? (
              <div className="space-y-3">
                {automations.map((automation: EmailAutomationRule) => (
                  <div
                    key={automation.id}
                    className={`border rounded-lg p-4 ${
                      automation.is_active ? 'border-gray-200' : 'border-gray-100 bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <h3 className="font-medium text-gray-900">{automation.name}</h3>
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                              automation.is_active
                                ? 'bg-green-100 text-green-700'
                                : 'bg-gray-100 text-gray-600'
                            }`}
                          >
                            {automation.is_active ? 'Ενεργός' : 'Ανενεργός'}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span>Trigger: {automation.trigger_display}</span>
                          <span>Πρότυπο: {automation.template_name}</span>
                          <span>Χρόνος: {automation.timing_display}</span>
                          {automation.filter_types_count ? (
                            <span>{automation.filter_types_count} τύποι υποχρεώσεων</span>
                          ) : (
                            <span>Όλοι οι τύποι</span>
                          )}
                        </div>
                        {automation.description && (
                          <p className="mt-2 text-sm text-gray-500">
                            {automation.description}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={() => handleToggleAutomation(automation.id)}
                          className={`p-1.5 rounded transition-colors ${
                            automation.is_active
                              ? 'text-green-600 hover:bg-green-50'
                              : 'text-gray-400 hover:bg-gray-100'
                          }`}
                          title={automation.is_active ? 'Απενεργοποίηση' : 'Ενεργοποίηση'}
                        >
                          <Power size={18} />
                        </button>
                        <button
                          onClick={() => handleEditAutomation(automation)}
                          className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                          title="Επεξεργασία"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button
                          onClick={() => setDeletingAutomationId(automation.id)}
                          className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                          title="Διαγραφή"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Zap size={48} className="mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Δεν υπάρχουν κανόνες αυτοματοποίησης
                </h3>
                <p className="text-gray-500 mb-4">
                  Δημιουργήστε κανόνες για αυτόματη αποστολή email
                </p>
                <Button onClick={handleCreateAutomation}>
                  <Plus size={18} className="mr-2" />
                  Νέος Κανόνας
                </Button>
              </div>
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Ιστορικό Email</h2>
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={historySearch}
                    onChange={(e) => {
                      setHistorySearch(e.target.value);
                      setHistoryPage(1);
                    }}
                    placeholder="Αναζήτηση..."
                    className="pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  />
                </div>
                <select
                  value={historyStatusFilter}
                  onChange={(e) => {
                    setHistoryStatusFilter(e.target.value as EmailLogStatus | '');
                    setHistoryPage(1);
                  }}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                >
                  <option value="">Όλες</option>
                  <option value="sent">Απεστάλη</option>
                  <option value="failed">Αποτυχία</option>
                  <option value="pending">Αναμονή</option>
                </select>
              </div>
            </div>

            {historyLoading ? (
              <div className="text-center py-8 text-gray-500">Φόρτωση...</div>
            ) : historyData && historyData.results.length > 0 ? (
              <>
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                          Ημ/νία
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                          Παραλήπτης
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                          Πελάτης
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                          Θέμα
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                          Κατάσταση
                        </th>
                        <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                          Ενέργειες
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {historyData.results.map((log: EmailLog) => (
                        <tr key={log.id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4 text-sm text-gray-600">
                            {formatDateTime(log.sent_at)}
                          </td>
                          <td className="py-3 px-4">
                            <p className="text-sm text-gray-900">{log.recipient_email}</p>
                          </td>
                          <td className="py-3 px-4">
                            <p className="text-sm text-gray-600">
                              {log.client_name || '-'}
                            </p>
                          </td>
                          <td className="py-3 px-4">
                            <p className="text-sm text-gray-900 line-clamp-1 max-w-xs">
                              {log.subject}
                            </p>
                          </td>
                          <td className="py-3 px-4">
                            {getStatusBadge(log.status)}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <button
                              onClick={() => setViewingEmail(log)}
                              className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                              title="Προβολή"
                            >
                              <Eye size={16} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {historyData.count > 15 && (
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm text-gray-500">
                      Σύνολο: {historyData.count} εγγραφές
                    </p>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setHistoryPage((p) => Math.max(1, p - 1))}
                        disabled={!historyData.previous}
                      >
                        <ChevronLeft size={16} />
                      </Button>
                      <span className="text-sm text-gray-600">
                        Σελίδα {historyPage}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setHistoryPage((p) => p + 1)}
                        disabled={!historyData.next}
                      >
                        <ChevronRight size={16} />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <History size={48} className="mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Δεν υπάρχει ιστορικό email
                </h3>
                <p className="text-gray-500">
                  Τα απεσταλμένα email θα εμφανιστούν εδώ
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Template Modal */}
      <Modal
        isOpen={isTemplateModalOpen}
        onClose={() => {
          setIsTemplateModalOpen(false);
          setEditingTemplate(null);
        }}
        title={editingTemplate ? 'Επεξεργασία Προτύπου' : 'Νέο Πρότυπο Email'}
        size="lg"
      >
        <TemplateForm
          template={editingTemplate}
          variables={variables || []}
          onSubmit={handleTemplateSubmit}
          onCancel={() => {
            setIsTemplateModalOpen(false);
            setEditingTemplate(null);
          }}
          isLoading={createTemplate.isPending || updateTemplate.isPending}
        />
      </Modal>

      {/* Automation Modal */}
      <Modal
        isOpen={isAutomationModalOpen}
        onClose={() => {
          setIsAutomationModalOpen(false);
          setEditingAutomation(null);
        }}
        title={editingAutomation ? 'Επεξεργασία Κανόνα' : 'Νέος Κανόνας Αυτοματοποίησης'}
        size="lg"
      >
        <AutomationForm
          automation={editingAutomation}
          onSubmit={handleAutomationSubmit}
          onCancel={() => {
            setIsAutomationModalOpen(false);
            setEditingAutomation(null);
          }}
          isLoading={createAutomation.isPending || updateAutomation.isPending}
        />
      </Modal>

      {/* Email Detail Modal */}
      <Modal
        isOpen={!!viewingEmail}
        onClose={() => setViewingEmail(null)}
        title="Λεπτομέρειες Email"
        size="lg"
      >
        {viewingEmail && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Παραλήπτης</p>
                <p className="font-medium">{viewingEmail.recipient_email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Ημ/νία Αποστολής</p>
                <p className="font-medium">{formatDateTime(viewingEmail.sent_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Κατάσταση</p>
                {getStatusBadge(viewingEmail.status)}
              </div>
              <div>
                <p className="text-sm text-gray-500">Πελάτης</p>
                <p className="font-medium">{viewingEmail.client_name || '-'}</p>
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-500 mb-1">Θέμα</p>
              <p className="font-medium">{viewingEmail.subject}</p>
            </div>

            <div>
              <p className="text-sm text-gray-500 mb-1">Κείμενο</p>
              <div
                className="p-4 bg-gray-50 rounded-lg border border-gray-200 prose max-w-none text-sm"
                dangerouslySetInnerHTML={{ __html: viewingEmail.body.replace(/\n/g, '<br>') }}
              />
            </div>

            {viewingEmail.error_message && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-700">
                  <strong>Σφάλμα:</strong> {viewingEmail.error_message}
                </p>
              </div>
            )}

            <div className="flex justify-end pt-4 border-t border-gray-200">
              <Button variant="secondary" onClick={() => setViewingEmail(null)}>
                Κλείσιμο
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Delete Template Confirmation */}
      <ConfirmDialog
        isOpen={!!deletingTemplateId}
        onClose={() => setDeletingTemplateId(null)}
        onConfirm={handleDeleteTemplate}
        title="Διαγραφή Προτύπου"
        message="Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το πρότυπο; Η ενέργεια δεν μπορεί να αναιρεθεί."
        confirmText="Διαγραφή"
        isLoading={deleteTemplate.isPending}
      />

      {/* Delete Automation Confirmation */}
      <ConfirmDialog
        isOpen={!!deletingAutomationId}
        onClose={() => setDeletingAutomationId(null)}
        onConfirm={handleDeleteAutomation}
        title="Διαγραφή Κανόνα"
        message="Είστε σίγουροι ότι θέλετε να διαγράψετε αυτόν τον κανόνα αυτοματοποίησης;"
        confirmText="Διαγραφή"
        isLoading={deleteAutomation.isPending}
      />

      {/* Cancel Scheduled Email Confirmation */}
      <ConfirmDialog
        isOpen={!!cancellingId}
        onClose={() => setCancellingId(null)}
        onConfirm={handleCancelScheduled}
        title="Ακύρωση Email"
        message="Είστε σίγουροι ότι θέλετε να ακυρώσετε αυτό το προγραμματισμένο email;"
        confirmText="Ακύρωση Email"
        isLoading={cancelScheduled.isPending}
      />
    </div>
  );
}
