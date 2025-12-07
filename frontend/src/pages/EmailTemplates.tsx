/**
 * EmailTemplates.tsx
 * Page for managing email templates - CRUD operations
 */

import { useState } from 'react';
import {
  Mail,
  Plus,
  Edit2,
  Trash2,
  FileText,
  AlertCircle,
  RefreshCw,
  Eye,
  Check,
  X,
  Copy,
} from 'lucide-react';
import { Modal, ConfirmDialog, Button } from '../components';
import {
  useEmailTemplates,
  useCreateEmailTemplate,
  useUpdateEmailTemplate,
  useDeleteEmailTemplate,
  usePreviewEmail,
  type EmailTemplateFormData,
} from '../hooks/useEmail';
import { useObligationTypes } from '../hooks/useObligations';
import type { EmailTemplate } from '../types';

// Available variables for templates
const TEMPLATE_VARIABLES = [
  { key: 'client_name', label: 'Επωνυμία πελάτη' },
  { key: 'client_afm', label: 'ΑΦΜ πελάτη' },
  { key: 'client_email', label: 'Email πελάτη' },
  { key: 'obligation_type', label: 'Τύπος υποχρέωσης' },
  { key: 'period_month', label: 'Μήνας περιόδου' },
  { key: 'period_year', label: 'Έτος περιόδου' },
  { key: 'period_display', label: 'Περίοδος (ΜΜ/ΕΕΕΕ)' },
  { key: 'deadline', label: 'Προθεσμία' },
  { key: 'completed_date', label: 'Ημ/νία ολοκλήρωσης' },
  { key: 'accountant_name', label: 'Όνομα λογιστή' },
  { key: 'company_name', label: 'Όνομα εταιρείας' },
];

export default function EmailTemplates() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<EmailTemplate | null>(null);
  const [previewContent, setPreviewContent] = useState<{ subject: string; body: string } | null>(
    null
  );

  // Queries
  const { data: templates, isLoading, isError, error, refetch } = useEmailTemplates();
  const { data: obligationTypes } = useObligationTypes();

  // Mutations
  const createMutation = useCreateEmailTemplate();
  const updateMutation = useUpdateEmailTemplate();
  const deleteMutation = useDeleteEmailTemplate();
  const previewMutation = usePreviewEmail();

  // Handlers
  const handleCreate = async (data: EmailTemplateFormData) => {
    await createMutation.mutateAsync(data);
    setIsCreateModalOpen(false);
  };

  const handleEdit = (template: EmailTemplate) => {
    setSelectedTemplate(template);
    setIsEditModalOpen(true);
  };

  const handleUpdate = async (data: EmailTemplateFormData) => {
    if (!selectedTemplate) return;
    await updateMutation.mutateAsync({ id: selectedTemplate.id, data });
    setIsEditModalOpen(false);
    setSelectedTemplate(null);
  };

  const handleDeleteClick = (template: EmailTemplate) => {
    setSelectedTemplate(template);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedTemplate) return;
    await deleteMutation.mutateAsync(selectedTemplate.id);
    setIsDeleteDialogOpen(false);
    setSelectedTemplate(null);
  };

  const handlePreview = async (template: EmailTemplate) => {
    setSelectedTemplate(template);
    try {
      const result = await previewMutation.mutateAsync({ templateId: template.id });
      setPreviewContent(result);
      setIsPreviewModalOpen(true);
    } catch {
      // Show template without variable substitution
      setPreviewContent({ subject: template.subject, body: template.body_html });
      setIsPreviewModalOpen(true);
    }
  };

  const handleDuplicate = (template: EmailTemplate) => {
    setSelectedTemplate({
      ...template,
      id: 0, // Reset ID for creation
      name: `${template.name} (αντίγραφο)`,
    });
    setIsCreateModalOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Mail className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Πρότυπα Email</h1>
            <p className="text-sm text-gray-500">{templates?.length || 0} πρότυπα</p>
          </div>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Νέο Πρότυπο
        </Button>
      </div>

      {/* Error Banner */}
      {isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <span className="text-red-700">
                Σφάλμα φόρτωσης: {error instanceof Error ? error.message : 'Άγνωστο σφάλμα'}
              </span>
            </div>
            <Button variant="secondary" size="sm" onClick={() => refetch()}>
              <RefreshCw className="w-4 h-4 mr-1" />
              Επανάληψη
            </Button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Φόρτωση προτύπων...</p>
        </div>
      )}

      {/* Templates List */}
      {!isLoading && !isError && (
        <div className="bg-white rounded-lg border border-gray-200">
          {templates?.length === 0 ? (
            <div className="p-12 text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Δεν υπάρχουν πρότυπα
              </h3>
              <p className="text-gray-500 mb-6">
                Δημιουργήστε το πρώτο σας πρότυπο email για να στέλνετε ειδοποιήσεις στους πελάτες.
              </p>
              <Button onClick={() => setIsCreateModalOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Δημιουργία Προτύπου
              </Button>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {templates?.map((template) => (
                <div
                  key={template.id}
                  className="p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-gray-900 truncate">
                          {template.name}
                        </h3>
                        {template.is_active ? (
                          <span className="px-2 py-0.5 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                            Ενεργό
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                            Ανενεργό
                          </span>
                        )}
                        {template.obligation_type_name && (
                          <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                            {template.obligation_type_name}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-1">
                        <strong>Θέμα:</strong> {template.subject}
                      </p>
                      {template.description && (
                        <p className="text-sm text-gray-500">{template.description}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => handlePreview(template)}
                        className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                        title="Προεπισκόπηση"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDuplicate(template)}
                        className="p-2 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded-lg"
                        title="Αντιγραφή"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleEdit(template)}
                        className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                        title="Επεξεργασία"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteClick(template)}
                        className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg"
                        title="Διαγραφή"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Variables Reference */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Διαθέσιμες Μεταβλητές
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Χρησιμοποιήστε αυτές τις μεταβλητές στο θέμα και το κείμενο του email.
          Θα αντικατασταθούν αυτόματα με τα πραγματικά δεδομένα.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {TEMPLATE_VARIABLES.map((variable) => (
            <div
              key={variable.key}
              className="bg-gray-50 rounded-lg p-3 text-sm"
            >
              <code className="text-blue-600 font-mono">{`{${variable.key}}`}</code>
              <p className="text-gray-600 mt-1">{variable.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          setSelectedTemplate(null);
        }}
        title="Νέο Πρότυπο Email"
        size="xl"
      >
        <EmailTemplateForm
          initialData={selectedTemplate || undefined}
          obligationTypes={obligationTypes || []}
          onSubmit={handleCreate}
          onCancel={() => {
            setIsCreateModalOpen(false);
            setSelectedTemplate(null);
          }}
          isLoading={createMutation.isPending}
        />
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedTemplate(null);
        }}
        title="Επεξεργασία Προτύπου"
        size="xl"
      >
        <EmailTemplateForm
          initialData={selectedTemplate || undefined}
          obligationTypes={obligationTypes || []}
          onSubmit={handleUpdate}
          onCancel={() => {
            setIsEditModalOpen(false);
            setSelectedTemplate(null);
          }}
          isLoading={updateMutation.isPending}
        />
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false);
          setSelectedTemplate(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Διαγραφή Προτύπου"
        message={`Είστε σίγουροι ότι θέλετε να διαγράψετε το πρότυπο "${selectedTemplate?.name}";`}
        confirmText="Διαγραφή"
        cancelText="Ακύρωση"
        isLoading={deleteMutation.isPending}
        variant="danger"
      />

      {/* Preview Modal */}
      <Modal
        isOpen={isPreviewModalOpen}
        onClose={() => {
          setIsPreviewModalOpen(false);
          setPreviewContent(null);
        }}
        title={`Προεπισκόπηση: ${selectedTemplate?.name || ''}`}
        size="lg"
      >
        {previewContent && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Θέμα
              </label>
              <div className="p-3 bg-gray-50 rounded-lg text-gray-900">
                {previewContent.subject}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Κείμενο
              </label>
              <div
                className="p-4 bg-gray-50 rounded-lg prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: previewContent.body }}
              />
            </div>
            <div className="flex justify-end pt-4 border-t border-gray-200">
              <Button
                variant="secondary"
                onClick={() => {
                  setIsPreviewModalOpen(false);
                  setPreviewContent(null);
                }}
              >
                Κλείσιμο
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

// ============================================
// EMAIL TEMPLATE FORM COMPONENT
// ============================================

interface EmailTemplateFormProps {
  initialData?: Partial<EmailTemplate>;
  obligationTypes: Array<{ id: number; code: string; name: string }>;
  onSubmit: (data: EmailTemplateFormData) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

function EmailTemplateForm({
  initialData,
  obligationTypes,
  onSubmit,
  onCancel,
  isLoading = false,
}: EmailTemplateFormProps) {
  const [formData, setFormData] = useState<EmailTemplateFormData>({
    name: initialData?.name || '',
    description: initialData?.description || '',
    subject: initialData?.subject || '',
    body_html: initialData?.body_html || '',
    obligation_type: initialData?.obligation_type || null,
    is_active: initialData?.is_active ?? true,
  });
  const [error, setError] = useState<string | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const insertVariable = (variable: string, field: 'subject' | 'body_html') => {
    const placeholder = `{${variable}}`;
    setFormData((prev) => ({
      ...prev,
      [field]: prev[field] + placeholder,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.name.trim()) {
      setError('Το όνομα είναι υποχρεωτικό');
      return;
    }
    if (!formData.subject.trim()) {
      setError('Το θέμα είναι υποχρεωτικό');
      return;
    }
    if (!formData.body_html.trim()) {
      setError('Το κείμενο είναι υποχρεωτικό');
      return;
    }

    try {
      await onSubmit({
        ...formData,
        obligation_type: formData.obligation_type || null,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Σφάλμα κατά την αποθήκευση');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <span className="text-sm text-red-700">{error}</span>
        </div>
      )}

      {/* Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Όνομα Προτύπου *
        </label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="π.χ. Ειδοποίηση ολοκλήρωσης ΦΠΑ"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Περιγραφή
        </label>
        <input
          type="text"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Σύντομη περιγραφή του προτύπου"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Obligation Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Τύπος Υποχρέωσης (αυτόματη επιλογή)
        </label>
        <select
          name="obligation_type"
          value={formData.obligation_type || ''}
          onChange={(e) =>
            setFormData((prev) => ({
              ...prev,
              obligation_type: e.target.value ? Number(e.target.value) : null,
            }))
          }
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">-- Κανένας (χειροκίνητη επιλογή) --</option>
          {obligationTypes.map((type) => (
            <option key={type.id} value={type.id}>
              {type.code} - {type.name}
            </option>
          ))}
        </select>
        <p className="text-xs text-gray-500 mt-1">
          Αν οριστεί, το πρότυπο επιλέγεται αυτόματα για αυτόν τον τύπο υποχρέωσης
        </p>
      </div>

      {/* Subject */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Θέμα Email *
        </label>
        <input
          type="text"
          name="subject"
          value={formData.subject}
          onChange={handleChange}
          placeholder="π.χ. Ολοκλήρωση {obligation_type} - {period_display}"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="flex flex-wrap gap-1 mt-2">
          {['client_name', 'obligation_type', 'period_display'].map((v) => (
            <button
              key={v}
              type="button"
              onClick={() => insertVariable(v, 'subject')}
              className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              {`{${v}}`}
            </button>
          ))}
        </div>
      </div>

      {/* Body */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Κείμενο Email *
        </label>
        <textarea
          name="body_html"
          value={formData.body_html}
          onChange={handleChange}
          rows={10}
          placeholder="Αγαπητέ/ή {client_name},&#10;&#10;Σας ενημερώνουμε ότι η υποχρέωση {obligation_type} για την περίοδο {period_display} ολοκληρώθηκε."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
        />
        <div className="flex flex-wrap gap-1 mt-2">
          {TEMPLATE_VARIABLES.map((v) => (
            <button
              key={v.key}
              type="button"
              onClick={() => insertVariable(v.key, 'body_html')}
              className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              title={v.label}
            >
              {`{${v.key}}`}
            </button>
          ))}
        </div>
      </div>

      {/* Is Active */}
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          name="is_active"
          checked={formData.is_active}
          onChange={handleChange}
          className="w-4 h-4 text-blue-600 rounded"
        />
        <span className="text-sm text-gray-700">Ενεργό πρότυπο</span>
      </label>

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={isLoading}>
          Ακύρωση
        </Button>
        <Button type="submit" isLoading={isLoading} className="flex-1">
          <Check className="w-4 h-4 mr-2" />
          Αποθήκευση
        </Button>
      </div>
    </form>
  );
}
