import { useState, useEffect } from 'react';
import { Send, Clock, Eye, Users, Info } from 'lucide-react';
import { Button } from '../Button';
import type { EmailTemplate, EmailVariable, Client, SendEmailData } from '../../types';
import { useEmailTemplates, useEmailVariables, usePreviewEmail } from '../../hooks/useEmails';
import { useClients } from '../../hooks/useClients';

interface EmailComposerProps {
  onSend: (data: SendEmailData & { schedule_at?: string }) => void;
  isLoading?: boolean;
  defaultRecipients?: string[];
  defaultClientIds?: number[];
}

export function EmailComposer({
  onSend,
  isLoading = false,
  defaultRecipients = [],
  defaultClientIds = [],
}: EmailComposerProps) {
  const { data: templates } = useEmailTemplates({ is_active: true });
  const { data: variables } = useEmailVariables();
  const { data: clientsData } = useClients({ page_size: 100 });
  const previewMutation = usePreviewEmail();

  const [recipients, setRecipients] = useState<string>(defaultRecipients.join(', '));
  const [selectedClientIds, setSelectedClientIds] = useState<number[]>(defaultClientIds);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [scheduleDate, setScheduleDate] = useState('');
  const [scheduleTime, setScheduleTime] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [previewResult, setPreviewResult] = useState<{ subject: string; body: string } | null>(null);
  const [showClientSelect, setShowClientSelect] = useState(false);
  const [showVariables, setShowVariables] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const clients = clientsData?.results || [];

  // Load template content when selected
  useEffect(() => {
    if (selectedTemplateId) {
      const template = templates?.find((t: EmailTemplate) => t.id === selectedTemplateId);
      if (template) {
        setSubject(template.subject);
        setBody(template.body_html || '');
      }
    }
  }, [selectedTemplateId, templates]);

  const handleTemplateChange = (templateId: number | null) => {
    setSelectedTemplateId(templateId);
  };

  const toggleClient = (clientId: number) => {
    setSelectedClientIds((prev) =>
      prev.includes(clientId)
        ? prev.filter((id) => id !== clientId)
        : [...prev, clientId]
    );
  };

  const insertVariable = (variable: string) => {
    const textarea = document.getElementById('email-body') as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newText = body.substring(0, start) + variable + body.substring(end);
      setBody(newText);

      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + variable.length;
        textarea.focus();
      }, 0);
    }
  };

  const handlePreview = async () => {
    if (selectedTemplateId && selectedClientIds.length > 0) {
      try {
        const result = await previewMutation.mutateAsync({
          template_id: selectedTemplateId,
          client_id: selectedClientIds[0],
        });
        setPreviewResult(result);
        setShowPreview(true);
      } catch (error) {
        console.error('Preview error:', error);
      }
    } else {
      setPreviewResult({ subject, body });
      setShowPreview(true);
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    const recipientList = recipients.split(',').map((e) => e.trim()).filter(Boolean);
    const hasRecipients = recipientList.length > 0 || selectedClientIds.length > 0;

    if (!hasRecipients) {
      newErrors.recipients = 'Εισάγετε email παραληπτών ή επιλέξτε πελάτες';
    }
    if (!subject.trim()) {
      newErrors.subject = 'Το θέμα είναι υποχρεωτικό';
    }
    if (!body.trim()) {
      newErrors.body = 'Το κείμενο είναι υποχρεωτικό';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSend = () => {
    if (!validate()) return;

    const recipientList = recipients.split(',').map((e) => e.trim()).filter(Boolean);

    // Add emails from selected clients
    const clientEmails = clients
      .filter((c: Client) => selectedClientIds.includes(c.id) && c.email)
      .map((c: Client) => c.email!);

    const allRecipients = [...new Set([...recipientList, ...clientEmails])];

    let schedule_at: string | undefined;
    if (scheduleDate && scheduleTime) {
      schedule_at = `${scheduleDate}T${scheduleTime}:00`;
    }

    onSend({
      to: allRecipients,
      subject,
      body,
      template_id: selectedTemplateId,
      schedule_at,
    });
  };

  return (
    <div className="space-y-4">
      {/* Recipients */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <label htmlFor="recipients" className="block text-sm font-medium text-gray-700">
            Παραλήπτες
          </label>
          <button
            type="button"
            onClick={() => setShowClientSelect(!showClientSelect)}
            className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            <Users size={14} />
            {showClientSelect ? 'Απόκρυψη πελατών' : 'Επιλογή από πελάτες'}
          </button>
        </div>
        <input
          type="text"
          id="recipients"
          value={recipients}
          onChange={(e) => setRecipients(e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.recipients ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="email@example.com, email2@example.com"
        />
        {errors.recipients && <p className="mt-1 text-sm text-red-500">{errors.recipients}</p>}

        {/* Selected clients count */}
        {selectedClientIds.length > 0 && (
          <p className="mt-1 text-sm text-green-600">
            + {selectedClientIds.length} πελάτες επιλεγμένοι
          </p>
        )}

        {/* Client selection */}
        {showClientSelect && (
          <div className="mt-2 max-h-40 overflow-y-auto border border-gray-300 rounded-lg p-2 space-y-1">
            {clients.map((client: Client) => (
              <label
                key={client.id}
                className={`flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer ${
                  !client.email ? 'opacity-50' : ''
                }`}
              >
                <input
                  type="checkbox"
                  checked={selectedClientIds.includes(client.id)}
                  onChange={() => toggleClient(client.id)}
                  disabled={!client.email}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">
                  {client.eponimia}
                  {client.email ? (
                    <span className="text-gray-400 ml-1">({client.email})</span>
                  ) : (
                    <span className="text-red-400 ml-1">(χωρίς email)</span>
                  )}
                </span>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Template selection */}
      <div>
        <label htmlFor="template" className="block text-sm font-medium text-gray-700 mb-1">
          Χρήση Προτύπου
        </label>
        <select
          id="template"
          value={selectedTemplateId || ''}
          onChange={(e) => handleTemplateChange(e.target.value ? parseInt(e.target.value) : null)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">-- Χωρίς πρότυπο --</option>
          {templates?.map((template: EmailTemplate) => (
            <option key={template.id} value={template.id}>
              {template.name}
            </option>
          ))}
        </select>
      </div>

      {/* Subject */}
      <div>
        <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
          Θέμα *
        </label>
        <input
          type="text"
          id="subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.subject ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Θέμα email..."
        />
        {errors.subject && <p className="mt-1 text-sm text-red-500">{errors.subject}</p>}
      </div>

      {/* Body */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <label htmlFor="email-body" className="block text-sm font-medium text-gray-700">
            Κείμενο *
          </label>
          <button
            type="button"
            onClick={() => setShowVariables(!showVariables)}
            className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            <Info size={14} />
            {showVariables ? 'Απόκρυψη μεταβλητών' : 'Μεταβλητές'}
          </button>
        </div>

        {/* Variables List */}
        {showVariables && variables && variables.length > 0 && (
          <div className="mb-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-xs text-blue-700 mb-2">
              Κάντε κλικ για προσθήκη:
            </p>
            <div className="flex flex-wrap gap-1">
              {variables.map((variable: EmailVariable) => (
                <button
                  key={variable.key}
                  type="button"
                  onClick={() => insertVariable(variable.key)}
                  className="px-2 py-1 text-xs bg-white border border-blue-300 rounded hover:bg-blue-100 transition-colors"
                  title={variable.description}
                >
                  {variable.key}
                </button>
              ))}
            </div>
          </div>
        )}

        <textarea
          id="email-body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          rows={10}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm ${
            errors.body ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Κείμενο email..."
        />
        {errors.body && <p className="mt-1 text-sm text-red-500">{errors.body}</p>}
      </div>

      {/* Schedule */}
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <label htmlFor="schedule-date" className="block text-sm font-medium text-gray-700 mb-1">
            Προγραμματισμός (προαιρετικό)
          </label>
          <div className="flex gap-2">
            <input
              type="date"
              id="schedule-date"
              value={scheduleDate}
              onChange={(e) => setScheduleDate(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <input
              type="time"
              value={scheduleTime}
              onChange={(e) => setScheduleTime(e.target.value)}
              className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center pt-4 border-t border-gray-200">
        <Button
          type="button"
          variant="ghost"
          onClick={handlePreview}
          disabled={!body.trim()}
        >
          <Eye size={18} className="mr-2" />
          Προεπισκόπηση
        </Button>

        <div className="flex gap-2">
          {scheduleDate && scheduleTime ? (
            <Button onClick={handleSend} disabled={isLoading}>
              <Clock size={18} className="mr-2" />
              {isLoading ? 'Προγραμματισμός...' : 'Προγραμματισμός'}
            </Button>
          ) : (
            <Button onClick={handleSend} disabled={isLoading}>
              <Send size={18} className="mr-2" />
              {isLoading ? 'Αποστολή...' : 'Αποστολή τώρα'}
            </Button>
          )}
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && previewResult && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div
            className="fixed inset-0 bg-black bg-opacity-50"
            onClick={() => setShowPreview(false)}
          />
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative w-full max-w-2xl bg-white rounded-lg shadow-xl">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold">Προεπισκόπηση Email</h3>
              </div>
              <div className="px-6 py-4">
                <div className="mb-4">
                  <p className="text-sm text-gray-500 mb-1">Θέμα:</p>
                  <p className="font-medium">{previewResult.subject}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Κείμενο:</p>
                  <div
                    className="p-4 bg-gray-50 rounded-lg border border-gray-200 prose max-w-none"
                    dangerouslySetInnerHTML={{ __html: previewResult.body.replace(/\n/g, '<br>') }}
                  />
                </div>
              </div>
              <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
                <Button variant="secondary" onClick={() => setShowPreview(false)}>
                  Κλείσιμο
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default EmailComposer;
