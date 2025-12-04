import { useState, useEffect } from 'react';
import { Info } from 'lucide-react';
import { Button } from '../Button';
import type { EmailTemplate, EmailTemplateFormData, EmailVariable, ObligationTypeData } from '../../types';
import { useObligationTypes } from '../../hooks/useObligations';

interface TemplateFormProps {
  template?: EmailTemplate | null;
  variables?: EmailVariable[];
  onSubmit: (data: EmailTemplateFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function TemplateForm({
  template,
  variables = [],
  onSubmit,
  onCancel,
  isLoading = false,
}: TemplateFormProps) {
  const { data: obligationTypes } = useObligationTypes();

  const [formData, setFormData] = useState<EmailTemplateFormData>({
    name: '',
    description: '',
    subject: '',
    body_html: '',
    obligation_type: null,
    is_active: true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showVariables, setShowVariables] = useState(false);

  useEffect(() => {
    if (template) {
      setFormData({
        name: template.name,
        description: template.description || '',
        subject: template.subject,
        body_html: template.body_html || '',
        obligation_type: template.obligation_type || null,
        is_active: template.is_active,
      });
    }
  }, [template]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox'
        ? (e.target as HTMLInputElement).checked
        : name === 'obligation_type'
          ? (value === '' ? null : parseInt(value, 10))
          : value,
    }));

    // Clear error when field is edited
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const insertVariable = (variable: string) => {
    const textarea = document.getElementById('body_html') as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = formData.body_html;
      const newText = text.substring(0, start) + variable + text.substring(end);
      setFormData((prev) => ({ ...prev, body_html: newText }));

      // Reset cursor position
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + variable.length;
        textarea.focus();
      }, 0);
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Το όνομα είναι υποχρεωτικό';
    }
    if (!formData.subject.trim()) {
      newErrors.subject = 'Το θέμα είναι υποχρεωτικό';
    }
    if (!formData.body_html.trim()) {
      newErrors.body_html = 'Το κείμενο είναι υποχρεωτικό';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Name */}
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Όνομα Προτύπου *
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.name ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="π.χ. Ολοκλήρωση ΦΠΑ"
        />
        {errors.name && <p className="mt-1 text-sm text-red-500">{errors.name}</p>}
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Περιγραφή
        </label>
        <input
          type="text"
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Σύντομη περιγραφή του προτύπου"
        />
      </div>

      {/* Obligation Type */}
      <div>
        <label htmlFor="obligation_type" className="block text-sm font-medium text-gray-700 mb-1">
          Τύπος Υποχρέωσης (προαιρετικό)
        </label>
        <select
          id="obligation_type"
          name="obligation_type"
          value={formData.obligation_type || ''}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">-- Όλοι οι τύποι --</option>
          {obligationTypes?.map((type: ObligationTypeData) => (
            <option key={type.id} value={type.id}>
              {type.name} ({type.code})
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-gray-500">
          Αν επιλέξετε τύπο, το πρότυπο θα χρησιμοποιείται αυτόματα για αυτόν τον τύπο.
        </p>
      </div>

      {/* Subject */}
      <div>
        <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
          Θέμα Email *
        </label>
        <input
          type="text"
          id="subject"
          name="subject"
          value={formData.subject}
          onChange={handleChange}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.subject ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="π.χ. Ολοκλήρωση {obligation_type} - {period_display}"
        />
        {errors.subject && <p className="mt-1 text-sm text-red-500">{errors.subject}</p>}
      </div>

      {/* Body */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <label htmlFor="body_html" className="block text-sm font-medium text-gray-700">
            Κείμενο Email *
          </label>
          <button
            type="button"
            onClick={() => setShowVariables(!showVariables)}
            className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            <Info size={14} />
            {showVariables ? 'Απόκρυψη μεταβλητών' : 'Διαθέσιμες μεταβλητές'}
          </button>
        </div>

        {/* Variables List */}
        {showVariables && variables.length > 0 && (
          <div className="mb-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-xs text-blue-700 mb-2">
              Κάντε κλικ σε μια μεταβλητή για να την προσθέσετε στο κείμενο:
            </p>
            <div className="flex flex-wrap gap-1">
              {variables.map((variable) => (
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
          id="body_html"
          name="body_html"
          value={formData.body_html}
          onChange={handleChange}
          rows={10}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm ${
            errors.body_html ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Αγαπητέ/ή {client_name},

Σας ενημερώνουμε ότι ολοκληρώθηκε η υποχρέωση {obligation_type} για την περίοδο {period_display}.

Με εκτίμηση,
{accountant_name}"
        />
        {errors.body_html && <p className="mt-1 text-sm text-red-500">{errors.body_html}</p>}
      </div>

      {/* Is Active */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_active"
          name="is_active"
          checked={formData.is_active}
          onChange={handleChange}
          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
        <label htmlFor="is_active" className="text-sm text-gray-700">
          Ενεργό πρότυπο
        </label>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Ακύρωση
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Αποθήκευση...' : template ? 'Ενημέρωση' : 'Δημιουργία'}
        </Button>
      </div>
    </form>
  );
}

export default TemplateForm;
