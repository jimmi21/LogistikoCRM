import { useState, useEffect } from 'react';
import { Button } from '../Button';
import type { EmailAutomationRule, EmailAutomationRuleFormData, EmailTemplate, ObligationTypeData } from '../../types';
import { useObligationTypes } from '../../hooks/useObligations';
import { useEmailTemplates } from '../../hooks/useEmails';

interface AutomationFormProps {
  automation?: EmailAutomationRule | null;
  onSubmit: (data: EmailAutomationRuleFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const TRIGGER_OPTIONS = [
  { value: 'on_complete', label: 'Όταν ολοκληρώνεται υποχρέωση' },
  { value: 'before_deadline', label: 'Πριν την προθεσμία' },
  { value: 'on_overdue', label: 'Όταν καθυστερεί' },
  { value: 'manual', label: 'Χειροκίνητα' },
];

const TIMING_OPTIONS = [
  { value: 'immediate', label: 'Άμεσα' },
  { value: 'delay_1h', label: 'Μετά από 1 ώρα' },
  { value: 'delay_24h', label: 'Επόμενη ημέρα' },
  { value: 'scheduled', label: 'Συγκεκριμένη ώρα' },
];

export function AutomationForm({
  automation,
  onSubmit,
  onCancel,
  isLoading = false,
}: AutomationFormProps) {
  const { data: obligationTypes } = useObligationTypes();
  const { data: templates } = useEmailTemplates({ is_active: true });

  const [formData, setFormData] = useState<EmailAutomationRuleFormData>({
    name: '',
    description: '',
    trigger: 'on_complete',
    filter_obligation_types: [],
    template: 0,
    timing: 'immediate',
    days_before_deadline: null,
    scheduled_time: null,
    is_active: true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (automation) {
      setFormData({
        name: automation.name,
        description: automation.description || '',
        trigger: automation.trigger,
        filter_obligation_types: automation.filter_obligation_types || [],
        template: automation.template,
        timing: automation.timing,
        days_before_deadline: automation.days_before_deadline,
        scheduled_time: automation.scheduled_time,
        is_active: automation.is_active,
      });
    }
  }, [automation]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]:
        type === 'checkbox'
          ? (e.target as HTMLInputElement).checked
          : name === 'template' || name === 'days_before_deadline'
            ? value === '' ? null : parseInt(value, 10)
            : value,
    }));

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const handleTypeChange = (typeId: number) => {
    setFormData((prev) => {
      const currentTypes = prev.filter_obligation_types || [];
      const newTypes = currentTypes.includes(typeId)
        ? currentTypes.filter((id) => id !== typeId)
        : [...currentTypes, typeId];
      return { ...prev, filter_obligation_types: newTypes };
    });
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Το όνομα είναι υποχρεωτικό';
    }
    if (!formData.template) {
      newErrors.template = 'Επιλέξτε πρότυπο email';
    }
    if (formData.trigger === 'before_deadline' && !formData.days_before_deadline) {
      newErrors.days_before_deadline = 'Εισάγετε αριθμό ημερών';
    }
    if (formData.timing === 'scheduled' && !formData.scheduled_time) {
      newErrors.scheduled_time = 'Εισάγετε ώρα αποστολής';
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
          Όνομα Κανόνα *
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
          placeholder="π.χ. Ειδοποίηση ολοκλήρωσης"
        />
        {errors.name && <p className="mt-1 text-sm text-red-500">{errors.name}</p>}
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Περιγραφή
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Σύντομη περιγραφή του κανόνα"
        />
      </div>

      {/* Trigger */}
      <div>
        <label htmlFor="trigger" className="block text-sm font-medium text-gray-700 mb-1">
          Trigger *
        </label>
        <select
          id="trigger"
          name="trigger"
          value={formData.trigger}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {TRIGGER_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Days before deadline (conditional) */}
      {formData.trigger === 'before_deadline' && (
        <div>
          <label htmlFor="days_before_deadline" className="block text-sm font-medium text-gray-700 mb-1">
            Ημέρες πριν την προθεσμία *
          </label>
          <input
            type="number"
            id="days_before_deadline"
            name="days_before_deadline"
            value={formData.days_before_deadline || ''}
            onChange={handleChange}
            min={1}
            max={30}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              errors.days_before_deadline ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="π.χ. 3"
          />
          {errors.days_before_deadline && (
            <p className="mt-1 text-sm text-red-500">{errors.days_before_deadline}</p>
          )}
        </div>
      )}

      {/* Template */}
      <div>
        <label htmlFor="template" className="block text-sm font-medium text-gray-700 mb-1">
          Πρότυπο Email *
        </label>
        <select
          id="template"
          name="template"
          value={formData.template || ''}
          onChange={handleChange}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.template ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value="">-- Επιλέξτε πρότυπο --</option>
          {templates?.map((template: EmailTemplate) => (
            <option key={template.id} value={template.id}>
              {template.name}
            </option>
          ))}
        </select>
        {errors.template && <p className="mt-1 text-sm text-red-500">{errors.template}</p>}
      </div>

      {/* Timing */}
      <div>
        <label htmlFor="timing" className="block text-sm font-medium text-gray-700 mb-1">
          Χρονοδιάγραμμα
        </label>
        <select
          id="timing"
          name="timing"
          value={formData.timing}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {TIMING_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Scheduled time (conditional) */}
      {formData.timing === 'scheduled' && (
        <div>
          <label htmlFor="scheduled_time" className="block text-sm font-medium text-gray-700 mb-1">
            Ώρα αποστολής *
          </label>
          <input
            type="time"
            id="scheduled_time"
            name="scheduled_time"
            value={formData.scheduled_time || ''}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              errors.scheduled_time ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.scheduled_time && (
            <p className="mt-1 text-sm text-red-500">{errors.scheduled_time}</p>
          )}
        </div>
      )}

      {/* Filter Obligation Types */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Φίλτρο Τύπων Υποχρεώσεων
        </label>
        <p className="text-xs text-gray-500 mb-2">
          Αν δεν επιλέξετε κανέναν τύπο, ο κανόνας θα ισχύει για όλους.
        </p>
        <div className="max-h-40 overflow-y-auto border border-gray-300 rounded-lg p-2 space-y-1">
          {obligationTypes?.map((type: ObligationTypeData) => (
            <label key={type.id} className="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer">
              <input
                type="checkbox"
                checked={formData.filter_obligation_types?.includes(type.id) || false}
                onChange={() => handleTypeChange(type.id)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                {type.name} ({type.code})
              </span>
            </label>
          ))}
        </div>
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
          Ενεργός κανόνας
        </label>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Ακύρωση
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Αποθήκευση...' : automation ? 'Ενημέρωση' : 'Δημιουργία'}
        </Button>
      </div>
    </form>
  );
}

export default AutomationForm;
