import { useState, useRef, useCallback, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  User,
  FileText,
  Mail,
  Phone,
  Ticket,
  StickyNote,
  ChevronLeft,
  Save,
  Upload,
  Trash2,
  Download,
  Plus,
  AlertCircle,
  Clock,
  Calendar,
  Building,
  MapPin,
  CreditCard,
  Key,
  RefreshCw,
  PhoneIncoming,
  PhoneOutgoing,
  PhoneMissed,
  ExternalLink,
  Eye,
  X,
  ClipboardList,
  CheckCircle,
} from 'lucide-react';
import { Button } from '../components';
import {
  useClientFull,
  useClientDocuments,
  useClientObligations,
  useClientEmails,
  useClientCalls,
  useClientTickets,
  useUploadDocument,
  useDeleteDocument,
  useCreateTicket,
  useUpdateClientFull,
  useClientObligationProfile,
  useUpdateClientObligationProfile,
} from '../hooks/useClientDetails';
import { useObligationTypesGrouped } from '../hooks/useObligations';
import type { ClientFull, ClientDocument, VoIPTicket, ObligationGroup } from '../types';
import {
  DOCUMENT_CATEGORIES,
  TAXPAYER_TYPES,
  BOOK_CATEGORIES,
  LEGAL_FORMS,
  FREQUENCY_LABELS,
} from '../types';

// Tab type
type TabType = 'info' | 'obligations' | 'profile' | 'documents' | 'emails' | 'calls' | 'tickets' | 'notes';

// Tab configuration
const TABS: { id: TabType; label: string; icon: React.ElementType }[] = [
  { id: 'info', label: 'Στοιχεία', icon: User },
  { id: 'obligations', label: 'Υποχρεώσεις', icon: FileText },
  { id: 'profile', label: 'Προφίλ Υποχρεώσεων', icon: ClipboardList },
  { id: 'documents', label: 'Έγγραφα', icon: FileText },
  { id: 'emails', label: 'Email', icon: Mail },
  { id: 'calls', label: 'Κλήσεις', icon: Phone },
  { id: 'tickets', label: 'Tickets', icon: Ticket },
  { id: 'notes', label: 'Σημειώσεις', icon: StickyNote },
];

// Status badge colors
const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
  in_progress: 'bg-blue-100 text-blue-800',
  cancelled: 'bg-gray-100 text-gray-800',
};

// Status labels
const STATUS_LABELS: Record<string, string> = {
  pending: 'Εκκρεμεί',
  completed: 'Ολοκληρώθηκε',
  overdue: 'Καθυστερεί',
  in_progress: 'Σε εξέλιξη',
  cancelled: 'Ακυρώθηκε',
};

// Priority colors
const PRIORITY_COLORS: Record<string, string> = {
  low: 'bg-gray-100 text-gray-800',
  medium: 'bg-blue-100 text-blue-800',
  high: 'bg-orange-100 text-orange-800',
  urgent: 'bg-red-100 text-red-800',
};

export default function ClientDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const clientId = parseInt(id || '0', 10);

  const [activeTab, setActiveTab] = useState<TabType>('info');
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<Partial<ClientFull>>({});
  const [yearFilter, setYearFilter] = useState<number>(new Date().getFullYear());
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [ticketModalOpen, setTicketModalOpen] = useState(false);

  // Fetch client data
  const { data: client, isLoading, isError, error, refetch } = useClientFull(clientId);

  // Tab-specific queries (lazy loaded)
  const { data: documentsData, isLoading: docsLoading } = useClientDocuments(
    clientId,
    activeTab === 'documents' ? undefined : undefined
  );
  const { data: obligationsData, isLoading: oblLoading } = useClientObligations(
    clientId,
    activeTab === 'obligations' ? { year: yearFilter, status: statusFilter || undefined } : undefined
  );
  const { data: emailsData, isLoading: emailsLoading } = useClientEmails(clientId);
  const { data: callsData, isLoading: callsLoading } = useClientCalls(clientId);
  const { data: ticketsData, isLoading: ticketsLoading } = useClientTickets(clientId);

  // Obligation Profile hooks
  const { data: obligationTypesGrouped, isLoading: typesLoading } = useObligationTypesGrouped();
  const { data: clientObligationProfile, isLoading: profileLoading } = useClientObligationProfile(clientId);
  const updateProfileMutation = useUpdateClientObligationProfile(clientId);

  // Mutations
  const updateMutation = useUpdateClientFull(clientId);
  const uploadMutation = useUploadDocument(clientId);
  const deleteMutation = useDeleteDocument(clientId);
  const createTicketMutation = useCreateTicket(clientId);

  // Handlers
  const handleSave = useCallback(() => {
    updateMutation.mutate(editData, {
      onSuccess: () => {
        setIsEditing(false);
        setEditData({});
        refetch();
      },
    });
  }, [editData, updateMutation, refetch]);

  const handleCancelEdit = useCallback(() => {
    setIsEditing(false);
    setEditData({});
  }, []);

  const handleFieldChange = useCallback((field: keyof ClientFull, value: unknown) => {
    setEditData((prev) => ({ ...prev, [field]: value }));
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-500">Φόρτωση στοιχείων πελάτη...</span>
      </div>
    );
  }

  if (isError || !client) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-lg font-semibold text-red-800 mb-2">Σφάλμα φόρτωσης</h2>
        <p className="text-red-600 mb-4">
          {error instanceof Error ? error.message : 'Δεν βρέθηκε ο πελάτης'}
        </p>
        <Button variant="secondary" onClick={() => navigate('/clients')}>
          <ChevronLeft className="w-4 h-4 mr-2" />
          Επιστροφή στους πελάτες
        </Button>
      </div>
    );
  }

  const currentData = { ...client, ...editData };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Back button and client info */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/clients')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-blue-600">
                  {client.eponimia.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{client.eponimia}</h1>
                <div className="flex items-center gap-3 mt-1">
                  <span className="font-mono text-sm bg-gray-100 px-2 py-0.5 rounded">
                    ΑΦΜ: {client.afm}
                  </span>
                  <span
                    className={`px-2 py-0.5 text-xs font-medium rounded ${
                      client.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {client.is_active ? 'Ενεργός' : 'Ανενεργός'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            {isEditing ? (
              <>
                <Button
                  variant="secondary"
                  onClick={handleCancelEdit}
                  disabled={updateMutation.isPending}
                >
                  Ακύρωση
                </Button>
                <Button onClick={handleSave} disabled={updateMutation.isPending}>
                  {updateMutation.isPending ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4 mr-2" />
                  )}
                  Αποθήκευση
                </Button>
              </>
            ) : (
              <Button onClick={() => setIsEditing(true)}>
                <Save className="w-4 h-4 mr-2" />
                Επεξεργασία
              </Button>
            )}
          </div>
        </div>

        {/* Stats cards */}
        {client.counts && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{client.counts.obligations}</p>
              <p className="text-sm text-gray-500">Υποχρεώσεις</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{client.counts.pending_obligations}</p>
              <p className="text-sm text-gray-500">Εκκρεμείς</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{client.counts.documents}</p>
              <p className="text-sm text-gray-500">Έγγραφα</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{client.counts.open_tickets}</p>
              <p className="text-sm text-gray-500">Ανοιχτά Tickets</p>
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {/* Tab navigation */}
        <div className="flex overflow-x-auto border-b border-gray-200">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="p-6">
          {/* INFO TAB */}
          {activeTab === 'info' && (
            <InfoTab
              client={currentData as ClientFull}
              isEditing={isEditing}
              onFieldChange={handleFieldChange}
            />
          )}

          {/* OBLIGATIONS TAB */}
          {activeTab === 'obligations' && (
            <ObligationsTab
              clientId={clientId}
              data={obligationsData}
              isLoading={oblLoading}
              yearFilter={yearFilter}
              setYearFilter={setYearFilter}
              statusFilter={statusFilter}
              setStatusFilter={setStatusFilter}
            />
          )}

          {/* OBLIGATION PROFILE TAB */}
          {activeTab === 'profile' && (
            <ObligationProfileTab
              groupedTypes={obligationTypesGrouped || []}
              clientProfile={clientObligationProfile}
              isLoading={typesLoading || profileLoading}
              onSave={(typeIds, profileIds) => {
                updateProfileMutation.mutate({
                  obligation_type_ids: typeIds,
                  obligation_profile_ids: profileIds,
                });
              }}
              isSaving={updateProfileMutation.isPending}
            />
          )}

          {/* DOCUMENTS TAB */}
          {activeTab === 'documents' && (
            <DocumentsTab
              data={documentsData}
              isLoading={docsLoading}
              onUpload={() => setUploadModalOpen(true)}
              onDelete={(docId) => {
                if (confirm('Διαγραφή εγγράφου;')) {
                  deleteMutation.mutate(docId);
                }
              }}
            />
          )}

          {/* EMAILS TAB */}
          {activeTab === 'emails' && (
            <EmailsTab data={emailsData} isLoading={emailsLoading} />
          )}

          {/* CALLS TAB */}
          {activeTab === 'calls' && (
            <CallsTab data={callsData} isLoading={callsLoading} />
          )}

          {/* TICKETS TAB */}
          {activeTab === 'tickets' && (
            <TicketsTab
              data={ticketsData}
              isLoading={ticketsLoading}
              onCreate={() => setTicketModalOpen(true)}
            />
          )}

          {/* NOTES TAB */}
          {activeTab === 'notes' && (
            <NotesTab
              client={currentData as ClientFull}
              isEditing={isEditing}
              onFieldChange={handleFieldChange}
            />
          )}
        </div>
      </div>

      {/* Upload Modal */}
      {uploadModalOpen && (
        <UploadModal
          onClose={() => setUploadModalOpen(false)}
          onUpload={(file, category, description) => {
            uploadMutation.mutate(
              { file, category, description },
              {
                onSuccess: () => setUploadModalOpen(false),
              }
            );
          }}
          isLoading={uploadMutation.isPending}
        />
      )}

      {/* Create Ticket Modal */}
      {ticketModalOpen && (
        <CreateTicketModal
          onClose={() => setTicketModalOpen(false)}
          onCreate={(title, description, priority) => {
            createTicketMutation.mutate(
              { title, description, priority },
              {
                onSuccess: () => setTicketModalOpen(false),
              }
            );
          }}
          isLoading={createTicketMutation.isPending}
        />
      )}
    </div>
  );
}

// ============================================
// INFO TAB COMPONENT
// ============================================
function InfoTab({
  client,
  isEditing,
  onFieldChange,
}: {
  client: ClientFull;
  isEditing: boolean;
  onFieldChange: (field: keyof ClientFull, value: unknown) => void;
}) {
  // Helper to get string value from client field
  const getStringValue = (field: keyof ClientFull): string => {
    const value = client[field];
    if (value === null || value === undefined) return '';
    if (typeof value === 'object') return '';
    return String(value);
  };

  const renderField = (
    field: keyof ClientFull,
    type: 'text' | 'email' | 'checkbox' | 'select' | 'date' = 'text',
    options?: { value: string; label: string }[]
  ): React.ReactNode => {
    const value = client[field];
    const stringValue = getStringValue(field);

    if (!isEditing) {
      if (type === 'checkbox') {
        return value ? 'Ναι' : 'Όχι';
      }
      if (type === 'select' && options) {
        const option = options.find((o) => o.value === stringValue);
        return option?.label || stringValue || '-';
      }
      return stringValue || '-';
    }

    if (type === 'checkbox') {
      return (
        <input
          type="checkbox"
          checked={!!value}
          onChange={(e) => onFieldChange(field, e.target.checked)}
          className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
        />
      );
    }

    if (type === 'select' && options) {
      return (
        <select
          value={stringValue}
          onChange={(e) => onFieldChange(field, e.target.value)}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">-- Επιλέξτε --</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      );
    }

    return (
      <input
        type={type}
        value={stringValue}
        onChange={(e) => onFieldChange(field, e.target.value)}
        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500"
      />
    );
  };

  return (
    <div className="space-y-8">
      {/* Basic Info Section */}
      <section>
        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
          <User className="w-5 h-5 text-blue-600" />
          Βασικά Στοιχεία
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FieldRow label="Επωνυμία">{renderField('eponimia')}</FieldRow>
          <FieldRow label="ΑΦΜ">{renderField('afm')}</FieldRow>
          <FieldRow label="ΔΟΥ">{renderField('doy')}</FieldRow>
          <FieldRow label="Όνομα">{renderField('onoma')}</FieldRow>
          <FieldRow label="Πατρώνυμο">{renderField('onoma_patros')}</FieldRow>
          <FieldRow label="Ενεργός">{renderField('is_active', 'checkbox')}</FieldRow>
        </div>
      </section>

      {/* Tax Info Section */}
      <section>
        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
          <Building className="w-5 h-5 text-green-600" />
          Φορολογικά Στοιχεία
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FieldRow label="Είδος Υπόχρεου">
            {renderField('eidos_ipoxreou', 'select', TAXPAYER_TYPES as unknown as { value: string; label: string }[])}
          </FieldRow>
          <FieldRow label="Κατηγορία Βιβλίων">
            {renderField('katigoria_vivlion', 'select', BOOK_CATEGORIES as unknown as { value: string; label: string }[])}
          </FieldRow>
          <FieldRow label="Νομική Μορφή">
            {renderField('nomiki_morfi', 'select', LEGAL_FORMS as unknown as { value: string; label: string }[])}
          </FieldRow>
          <FieldRow label="Αγρότης">{renderField('agrotis', 'checkbox')}</FieldRow>
          <FieldRow label="Ημερομηνία Έναρξης">
            {renderField('imerominia_enarksis', 'date')}
          </FieldRow>
          <FieldRow label="Αριθμός ΓΕΜΗ">{renderField('arithmos_gemi')}</FieldRow>
        </div>
      </section>

      {/* Contact Info Section */}
      <section>
        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
          <Phone className="w-5 h-5 text-purple-600" />
          Στοιχεία Επικοινωνίας
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FieldRow label="Email">{renderField('email', 'email')}</FieldRow>
          <FieldRow label="Κινητό">{renderField('kinito_tilefono')}</FieldRow>
          <FieldRow label="Τηλ. Οικίας 1">{renderField('tilefono_oikias_1')}</FieldRow>
          <FieldRow label="Τηλ. Οικίας 2">{renderField('tilefono_oikias_2')}</FieldRow>
          <FieldRow label="Τηλ. Επιχείρησης 1">{renderField('tilefono_epixeirisis_1')}</FieldRow>
          <FieldRow label="Τηλ. Επιχείρησης 2">{renderField('tilefono_epixeirisis_2')}</FieldRow>
        </div>
      </section>

      {/* Home Address Section */}
      <section>
        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
          <MapPin className="w-5 h-5 text-orange-600" />
          Διεύθυνση Κατοικίας
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FieldRow label="Διεύθυνση">{renderField('diefthinsi_katoikias')}</FieldRow>
          <FieldRow label="Αριθμός">{renderField('arithmos_katoikias')}</FieldRow>
          <FieldRow label="Πόλη">{renderField('poli_katoikias')}</FieldRow>
          <FieldRow label="Δήμος">{renderField('dimos_katoikias')}</FieldRow>
          <FieldRow label="Νομός">{renderField('nomos_katoikias')}</FieldRow>
          <FieldRow label="Τ.Κ.">{renderField('tk_katoikias')}</FieldRow>
        </div>
      </section>

      {/* Business Address Section */}
      <section>
        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
          <Building className="w-5 h-5 text-blue-600" />
          Διεύθυνση Επιχείρησης
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FieldRow label="Διεύθυνση">{renderField('diefthinsi_epixeirisis')}</FieldRow>
          <FieldRow label="Αριθμός">{renderField('arithmos_epixeirisis')}</FieldRow>
          <FieldRow label="Πόλη">{renderField('poli_epixeirisis')}</FieldRow>
          <FieldRow label="Δήμος">{renderField('dimos_epixeirisis')}</FieldRow>
          <FieldRow label="Νομός">{renderField('nomos_epixeirisis')}</FieldRow>
          <FieldRow label="Τ.Κ.">{renderField('tk_epixeirisis')}</FieldRow>
        </div>
      </section>

      {/* Bank Info Section */}
      <section>
        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
          <CreditCard className="w-5 h-5 text-green-600" />
          Τραπεζικά Στοιχεία
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FieldRow label="Τράπεζα">{renderField('trapeza')}</FieldRow>
          <FieldRow label="IBAN">{renderField('iban')}</FieldRow>
        </div>
      </section>

      {/* Credentials Section */}
      <section>
        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
          <Key className="w-5 h-5 text-red-600" />
          Διαπιστευτήρια (TAXISnet, ΙΚΑ, ΓΕΜΗ)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FieldRow label="TAXISnet Χρήστης">{renderField('onoma_xristi_taxisnet')}</FieldRow>
          <FieldRow label="TAXISnet Κωδικός">
            {isEditing ? renderField('kodikos_taxisnet') : '••••••••'}
          </FieldRow>
          <FieldRow label="ΙΚΑ Χρήστης">{renderField('onoma_xristi_ika_ergodoti')}</FieldRow>
          <FieldRow label="ΙΚΑ Κωδικός">
            {isEditing ? renderField('kodikos_ika_ergodoti') : '••••••••'}
          </FieldRow>
          <FieldRow label="ΓΕΜΗ Χρήστης">{renderField('onoma_xristi_gemi')}</FieldRow>
          <FieldRow label="ΓΕΜΗ Κωδικός">
            {isEditing ? renderField('kodikos_gemi') : '••••••••'}
          </FieldRow>
        </div>
      </section>

      {/* Meta Info */}
      <section className="bg-gray-50 rounded-lg p-4">
        <div className="flex flex-wrap gap-6 text-sm text-gray-500">
          <span>
            <Calendar className="w-4 h-4 inline mr-1" />
            Δημιουργία: {new Date(client.created_at).toLocaleDateString('el-GR')}
          </span>
          <span>
            <Clock className="w-4 h-4 inline mr-1" />
            Τελευταία ενημέρωση: {new Date(client.updated_at).toLocaleDateString('el-GR')}
          </span>
        </div>
      </section>
    </div>
  );
}

// Field row component
function FieldRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <div className="text-sm text-gray-900">{children}</div>
    </div>
  );
}

// ============================================
// OBLIGATIONS TAB COMPONENT
// ============================================
interface ObligationItem {
  id: number;
  obligation_type_name?: string;
  obligation_type_code?: string;
  year: number;
  month: number;
  deadline: string;
  status: string;
  completed_date?: string | null;
  notes?: string;
}

function ObligationsTab({
  clientId,
  data,
  isLoading,
  yearFilter,
  setYearFilter,
  statusFilter,
  setStatusFilter,
}: {
  clientId: number;
  data: { obligations: ObligationItem[] } | undefined;
  isLoading: boolean;
  yearFilter: number;
  setYearFilter: (year: number) => void;
  statusFilter: string;
  setStatusFilter: (status: string) => void;
}) {
  // clientId used in Link below
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Έτος:</label>
          <select
            value={yearFilter}
            onChange={(e) => setYearFilter(Number(e.target.value))}
            className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm"
          >
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Κατάσταση:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm"
          >
            <option value="">Όλες</option>
            <option value="pending">Εκκρεμείς</option>
            <option value="completed">Ολοκληρωμένες</option>
            <option value="overdue">Καθυστερημένες</option>
          </select>
        </div>
        <Link
          to={`/obligations?client=${clientId}`}
          className="ml-auto text-sm text-blue-600 hover:underline"
        >
          Προβολή όλων
          <ExternalLink className="w-3 h-3 inline ml-1" />
        </Link>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
        </div>
      )}

      {/* Table */}
      {!isLoading && data && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Τύπος
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Περίοδος
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Προθεσμία
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Κατάσταση
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Ολοκλήρωση
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.obligations.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    Δεν βρέθηκαν υποχρεώσεις
                  </td>
                </tr>
              ) : (
                data.obligations.map((obl) => (
                  <tr key={obl.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">
                      <Link
                        to={`/obligations?id=${obl.id}`}
                        className="text-blue-600 hover:underline font-medium"
                      >
                        {obl.obligation_type_name || obl.obligation_type_code}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {String(obl.month).padStart(2, '0')}/{obl.year}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {new Date(obl.deadline).toLocaleDateString('el-GR')}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          STATUS_COLORS[obl.status] || 'bg-gray-100'
                        }`}
                      >
                        {STATUS_LABELS[obl.status] || obl.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {obl.completed_date
                        ? new Date(obl.completed_date).toLocaleDateString('el-GR')
                        : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ============================================
// DOCUMENTS TAB COMPONENT
// ============================================
function DocumentsTab({
  data,
  isLoading,
  onUpload,
  onDelete,
}: {
  data: { documents: ClientDocument[] } | undefined;
  isLoading: boolean;
  onUpload: () => void;
  onDelete: (docId: number) => void;
}) {
  return (
    <div className="space-y-4">
      {/* Header with upload button */}
      <div className="flex justify-between items-center">
        <h3 className="text-sm font-medium text-gray-700">
          {data ? `${data.documents.length} έγγραφα` : 'Έγγραφα'}
        </h3>
        <Button onClick={onUpload}>
          <Upload className="w-4 h-4 mr-2" />
          Μεταφόρτωση
        </Button>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
        </div>
      )}

      {/* Documents grid */}
      {!isLoading && data && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.documents.length === 0 ? (
            <div className="col-span-full text-center py-8 text-gray-500">
              Δεν υπάρχουν έγγραφα
            </div>
          ) : (
            data.documents.map((doc) => (
              <div
                key={doc.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-gray-900 truncate">{doc.filename}</p>
                      <p className="text-xs text-gray-500">
                        {doc.category_display || doc.document_category}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                  <span className="text-xs text-gray-500">
                    {new Date(doc.uploaded_at).toLocaleDateString('el-GR')}
                  </span>
                  <div className="flex gap-2">
                    {doc.file_url && (
                      <a
                        href={doc.file_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                        title="Προβολή"
                      >
                        <Eye className="w-4 h-4" />
                      </a>
                    )}
                    {doc.file_url && (
                      <a
                        href={doc.file_url}
                        download
                        className="p-1.5 text-green-600 hover:bg-green-50 rounded"
                        title="Λήψη"
                      >
                        <Download className="w-4 h-4" />
                      </a>
                    )}
                    <button
                      onClick={() => onDelete(doc.id)}
                      className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                      title="Διαγραφή"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

// ============================================
// EMAILS TAB COMPONENT
// ============================================
function EmailsTab({
  data,
  isLoading,
}: {
  data: { emails: Array<{ id: number; recipient_email: string; subject: string; status: string; status_display?: string; sent_at: string | null; template_name?: string | null }> } | undefined;
  isLoading: boolean;
}) {
  return (
    <div className="space-y-4">
      {/* Loading */}
      {isLoading && (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
        </div>
      )}

      {/* Table */}
      {!isLoading && data && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Ημερομηνία
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Θέμα
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Παραλήπτης
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Κατάσταση
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.emails.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                    Δεν υπάρχουν καταγεγραμμένα email
                  </td>
                </tr>
              ) : (
                data.emails.map((email) => (
                  <tr key={email.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {email.sent_at
                        ? new Date(email.sent_at).toLocaleString('el-GR')
                        : '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{email.subject}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{email.recipient_email}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          email.status === 'sent'
                            ? 'bg-green-100 text-green-800'
                            : email.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {email.status_display || email.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ============================================
// CALLS TAB COMPONENT
// ============================================
function CallsTab({
  data,
  isLoading,
}: {
  data: { calls: Array<{ id: number; phone_number: string; direction: string; direction_display?: string; status: string; status_display?: string; started_at: string | null; duration_formatted?: string; notes?: string }> } | undefined;
  isLoading: boolean;
}) {
  const getCallIcon = (direction: string, status: string) => {
    if (status === 'missed') return <PhoneMissed className="w-4 h-4 text-red-500" />;
    if (direction === 'incoming') return <PhoneIncoming className="w-4 h-4 text-green-500" />;
    return <PhoneOutgoing className="w-4 h-4 text-blue-500" />;
  };

  return (
    <div className="space-y-4">
      {/* Loading */}
      {isLoading && (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
        </div>
      )}

      {/* Table */}
      {!isLoading && data && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Τύπος
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Αριθμός
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Ημερομηνία
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Διάρκεια
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Σημειώσεις
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.calls.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    Δεν υπάρχουν καταγεγραμμένες κλήσεις
                  </td>
                </tr>
              ) : (
                data.calls.map((call) => (
                  <tr key={call.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {getCallIcon(call.direction, call.status)}
                        <span className="text-sm">
                          {call.direction_display || call.direction}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm font-mono">{call.phone_number}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {call.started_at
                        ? new Date(call.started_at).toLocaleString('el-GR')
                        : '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {call.duration_formatted || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 truncate max-w-xs">
                      {call.notes || '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ============================================
// TICKETS TAB COMPONENT
// ============================================
function TicketsTab({
  data,
  isLoading,
  onCreate,
}: {
  data: { tickets: VoIPTicket[] } | undefined;
  isLoading: boolean;
  onCreate: () => void;
}) {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-sm font-medium text-gray-700">
          {data ? `${data.tickets.length} tickets` : 'Tickets'}
        </h3>
        <Button onClick={onCreate}>
          <Plus className="w-4 h-4 mr-2" />
          Νέο Ticket
        </Button>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
        </div>
      )}

      {/* Table */}
      {!isLoading && data && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Τίτλος
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Κατάσταση
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Προτεραιότητα
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Ανατέθηκε
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Δημιουργία
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.tickets.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    Δεν υπάρχουν tickets
                  </td>
                </tr>
              ) : (
                data.tickets.map((ticket) => (
                  <tr key={ticket.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <p className="text-sm font-medium text-gray-900">{ticket.title}</p>
                      {ticket.description && (
                        <p className="text-xs text-gray-500 truncate max-w-xs">
                          {ticket.description}
                        </p>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          ticket.is_open
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {ticket.status_display || ticket.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          PRIORITY_COLORS[ticket.priority] || 'bg-gray-100'
                        }`}
                      >
                        {ticket.priority_display || ticket.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {ticket.assigned_to_name || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {new Date(ticket.created_at).toLocaleDateString('el-GR')}
                      <span className="text-xs text-gray-400 ml-1">
                        ({ticket.days_since_created} μέρες)
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ============================================
// NOTES TAB COMPONENT
// ============================================
function NotesTab({
  isEditing,
}: {
  client: ClientFull;
  isEditing: boolean;
  onFieldChange: (field: keyof ClientFull, value: unknown) => void;
}) {
  // Note: simeiosis_pelati field doesn't exist in the current model
  // This is a placeholder for future implementation
  const [notes, setNotes] = useState('');

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-gray-700">Σημειώσεις Πελάτη</h3>
      {isEditing ? (
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={10}
          className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
          placeholder="Προσθέστε σημειώσεις για τον πελάτη..."
        />
      ) : (
        <div className="bg-gray-50 rounded-lg p-4 min-h-[200px]">
          {notes ? (
            <p className="whitespace-pre-wrap text-gray-700">{notes}</p>
          ) : (
            <p className="text-gray-400 italic">Δεν υπάρχουν σημειώσεις. Η λειτουργία αυτή θα προστεθεί σύντομα.</p>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================
// UPLOAD MODAL COMPONENT
// ============================================
function UploadModal({
  onClose,
  onUpload,
  isLoading,
}: {
  onClose: () => void;
  onUpload: (file: File, category?: string, description?: string) => void;
  isLoading: boolean;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [category, setCategory] = useState('general');
  const [description, setDescription] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleSubmit = () => {
    if (file) {
      onUpload(file, category, description);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold">Μεταφόρτωση Εγγράφου</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-4 space-y-4">
          {/* Drop zone */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={inputRef}
              type="file"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && setFile(e.target.files[0])}
              accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
            />
            {file ? (
              <div className="flex items-center justify-center gap-2">
                <FileText className="w-8 h-8 text-blue-600" />
                <span className="font-medium">{file.name}</span>
                <button
                  onClick={() => setFile(null)}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <>
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600 mb-1">Σύρετε αρχείο εδώ ή</p>
                <button
                  onClick={() => inputRef.current?.click()}
                  className="text-blue-600 hover:underline"
                >
                  επιλέξτε αρχείο
                </button>
                <p className="text-xs text-gray-400 mt-2">
                  PDF, DOC, XLS, JPG, PNG (max 10MB)
                </p>
              </>
            )}
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Κατηγορία
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg"
            >
              {DOCUMENT_CATEGORIES.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Περιγραφή (προαιρετικά)
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg"
              placeholder="Π.χ. Τιμολόγιο Δεκεμβρίου 2025"
            />
          </div>
        </div>
        <div className="flex justify-end gap-3 p-4 border-t bg-gray-50">
          <Button variant="secondary" onClick={onClose} disabled={isLoading}>
            Ακύρωση
          </Button>
          <Button onClick={handleSubmit} disabled={!file || isLoading}>
            {isLoading ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Upload className="w-4 h-4 mr-2" />
            )}
            Μεταφόρτωση
          </Button>
        </div>
      </div>
    </div>
  );
}

// ============================================
// CREATE TICKET MODAL COMPONENT
// ============================================
function CreateTicketModal({
  onClose,
  onCreate,
  isLoading,
}: {
  onClose: () => void;
  onCreate: (title: string, description?: string, priority?: 'low' | 'medium' | 'high' | 'urgent') => void;
  isLoading: boolean;
}) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');

  const handleSubmit = () => {
    if (title.trim()) {
      onCreate(title, description, priority);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold">Νέο Ticket</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-4 space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Τίτλος *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg"
              placeholder="Π.χ. Επικοινωνία για ΦΠΑ"
              autoFocus
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Περιγραφή
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg resize-none"
              placeholder="Λεπτομέρειες..."
            />
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Προτεραιότητα
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as typeof priority)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg"
            >
              <option value="low">Χαμηλή</option>
              <option value="medium">Μεσαία</option>
              <option value="high">Υψηλή</option>
              <option value="urgent">Επείγον</option>
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-3 p-4 border-t bg-gray-50">
          <Button variant="secondary" onClick={onClose} disabled={isLoading}>
            Ακύρωση
          </Button>
          <Button onClick={handleSubmit} disabled={!title.trim() || isLoading}>
            {isLoading ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Plus className="w-4 h-4 mr-2" />
            )}
            Δημιουργία
          </Button>
        </div>
      </div>
    </div>
  );
}

// ============================================
// OBLIGATION PROFILE TAB COMPONENT
// ============================================
function ObligationProfileTab({
  groupedTypes,
  clientProfile,
  isLoading,
  onSave,
  isSaving,
}: {
  groupedTypes: ObligationGroup[];
  clientProfile: { obligation_type_ids: number[]; obligation_profile_ids: number[] } | undefined;
  isLoading: boolean;
  onSave: (typeIds: number[], profileIds: number[]) => void;
  isSaving: boolean;
}) {
  // Local state for selected obligations
  const [selectedTypeIds, setSelectedTypeIds] = useState<Set<number>>(new Set());
  const [hasChanges, setHasChanges] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Initialize from client profile when it loads
  useEffect(() => {
    if (clientProfile) {
      setSelectedTypeIds(new Set(clientProfile.obligation_type_ids));
    }
  }, [clientProfile]);

  // Toggle a single obligation type
  const toggleType = (typeId: number) => {
    const newSelected = new Set(selectedTypeIds);
    if (newSelected.has(typeId)) {
      newSelected.delete(typeId);
    } else {
      newSelected.add(typeId);
    }
    setSelectedTypeIds(newSelected);
    setHasChanges(true);
    setSaveSuccess(false);
  };

  // Select all in a group
  const selectAllInGroup = (group: ObligationGroup) => {
    const newSelected = new Set(selectedTypeIds);
    group.types.forEach((t) => newSelected.add(t.id));
    setSelectedTypeIds(newSelected);
    setHasChanges(true);
    setSaveSuccess(false);
  };

  // Deselect all in a group
  const deselectAllInGroup = (group: ObligationGroup) => {
    const newSelected = new Set(selectedTypeIds);
    group.types.forEach((t) => newSelected.delete(t.id));
    setSelectedTypeIds(newSelected);
    setHasChanges(true);
    setSaveSuccess(false);
  };

  // Check if all in group are selected
  const isAllSelectedInGroup = (group: ObligationGroup) => {
    return group.types.every((t) => selectedTypeIds.has(t.id));
  };

  // Handle save
  const handleSave = () => {
    onSave(Array.from(selectedTypeIds), clientProfile?.obligation_profile_ids || []);
    setHasChanges(false);
    setSaveSuccess(true);
    // Reset success message after 3 seconds
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
        <p className="text-gray-500 mt-2">Φόρτωση προφίλ υποχρεώσεων...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Προφίλ Υποχρεώσεων</h3>
          <p className="text-sm text-gray-500 mt-1">
            Επιλέξτε τις υποχρεώσεις που ισχύουν για αυτόν τον πελάτη
          </p>
        </div>
        <div className="flex items-center gap-3">
          {saveSuccess && (
            <span className="flex items-center text-green-600 text-sm">
              <CheckCircle className="w-4 h-4 mr-1" />
              Αποθηκεύτηκε
            </span>
          )}
          <Button
            onClick={handleSave}
            disabled={!hasChanges || isSaving}
          >
            {isSaving ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Αποθήκευση
          </Button>
        </div>
      </div>

      {/* Groups */}
      {groupedTypes.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Δεν υπάρχουν διαθέσιμοι τύποι υποχρεώσεων.
        </div>
      ) : (
        <div className="space-y-6">
          {groupedTypes.map((group) => (
            <div key={group.group_id || 'ungrouped'} className="border border-gray-200 rounded-lg overflow-hidden">
              {/* Group Header */}
              <div className="flex items-center justify-between bg-gray-50 px-4 py-3 border-b border-gray-200">
                <h4 className="font-medium text-gray-900">{group.group_name}</h4>
                <button
                  onClick={() =>
                    isAllSelectedInGroup(group)
                      ? deselectAllInGroup(group)
                      : selectAllInGroup(group)
                  }
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  {isAllSelectedInGroup(group) ? 'Αποεπιλογή όλων' : 'Επιλογή όλων'}
                </button>
              </div>

              {/* Types List */}
              <div className="divide-y divide-gray-100">
                {group.types.map((type) => (
                  <label
                    key={type.id}
                    className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={selectedTypeIds.has(type.id)}
                        onChange={() => toggleType(type.id)}
                        className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                      />
                      <div>
                        <span className="text-sm font-medium text-gray-900">{type.name}</span>
                        <span className="text-xs text-gray-500 ml-2">({type.code})</span>
                      </div>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        type.frequency === 'monthly'
                          ? 'bg-blue-100 text-blue-800'
                          : type.frequency === 'quarterly'
                          ? 'bg-purple-100 text-purple-800'
                          : type.frequency === 'annual'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {FREQUENCY_LABELS[type.frequency] || type.frequency}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <p className="text-sm text-gray-600">
          <span className="font-medium text-gray-900">{selectedTypeIds.size}</span> υποχρεώσεις επιλεγμένες
        </p>
      </div>
    </div>
  );
}
