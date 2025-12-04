import { useState, useEffect, type FormEvent } from 'react';
import { Button } from './Button';
import type { Client, Obligation, ObligationFormData, ObligationStatus } from '../types';

interface ObligationFormProps {
  obligation?: Obligation | null;
  clients: Client[];
  onSubmit: (data: ObligationFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const OBLIGATION_TYPES = [
  { value: 'ΦΠΑ', label: 'ΦΠΑ - Φόρος Προστιθέμενης Αξίας' },
  { value: 'ΑΠΔ', label: 'ΑΠΔ - Αναλυτική Περιοδική Δήλωση' },
  { value: 'ΕΝΦΙΑ', label: 'ΕΝΦΙΑ - Ενιαίος Φόρος Ιδιοκτησίας' },
  { value: 'Ε1', label: 'Ε1 - Δήλωση Φορολογίας Εισοδήματος' },
  { value: 'Ε3', label: 'Ε3 - Κατάσταση Οικονομικών Στοιχείων' },
  { value: 'ΜΥΦ', label: 'ΜΥΦ - Συγκεντρωτικές Καταστάσεις' },
];

const STATUS_OPTIONS: { value: ObligationStatus; label: string }[] = [
  { value: 'pending', label: 'Εκκρεμεί' },
  { value: 'in_progress', label: 'Σε εξέλιξη' },
  { value: 'completed', label: 'Ολοκληρώθηκε' },
  { value: 'overdue', label: 'Εκπρόθεσμη' },
  { value: 'cancelled', label: 'Ακυρώθηκε' },
];

const MONTHS = [
  { value: 1, label: 'Ιανουάριος' },
  { value: 2, label: 'Φεβρουάριος' },
  { value: 3, label: 'Μάρτιος' },
  { value: 4, label: 'Απρίλιος' },
  { value: 5, label: 'Μάιος' },
  { value: 6, label: 'Ιούνιος' },
  { value: 7, label: 'Ιούλιος' },
  { value: 8, label: 'Αύγουστος' },
  { value: 9, label: 'Σεπτέμβριος' },
  { value: 10, label: 'Οκτώβριος' },
  { value: 11, label: 'Νοέμβριος' },
  { value: 12, label: 'Δεκέμβριος' },
];

const currentYear = new Date().getFullYear();
const YEARS = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i);

export function ObligationForm({
  obligation,
  clients,
  onSubmit,
  onCancel,
  isLoading = false,
}: ObligationFormProps) {
  const [formData, setFormData] = useState<ObligationFormData>({
    client: 0,
    obligation_type: 'ΦΠΑ',
    period_month: new Date().getMonth() + 1,
    period_year: currentYear,
    due_date: '',
    status: 'pending',
  });
  const [errors, setErrors] = useState<Partial<Record<keyof ObligationFormData, string>>>({});

  // Populate form when editing
  useEffect(() => {
    if (obligation) {
      setFormData({
        client: obligation.client,
        obligation_type: obligation.obligation_type,
        period_month: obligation.period_month,
        period_year: obligation.period_year,
        due_date: obligation.due_date,
        status: obligation.status,
      });
    }
  }, [obligation]);

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof ObligationFormData, string>> = {};

    if (!formData.client) {
      newErrors.client = 'Επιλέξτε πελάτη';
    }

    if (!formData.obligation_type) {
      newErrors.obligation_type = 'Επιλέξτε τύπο υποχρέωσης';
    }

    if (!formData.due_date) {
      newErrors.due_date = 'Η προθεσμία είναι υποχρεωτική';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  const handleChange = <K extends keyof ObligationFormData>(field: K, value: ObligationFormData[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Πελάτης */}
      <div>
        <label htmlFor="client" className="block text-sm font-medium text-gray-700 mb-1">
          Πελάτης *
        </label>
        <select
          id="client"
          value={formData.client}
          onChange={(e) => handleChange('client', Number(e.target.value))}
          className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.client ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value={0}>-- Επιλέξτε πελάτη --</option>
          {clients.map((client) => (
            <option key={client.id} value={client.id}>
              {client.onoma} ({client.afm})
            </option>
          ))}
        </select>
        {errors.client && <p className="mt-1 text-sm text-red-500">{errors.client}</p>}
      </div>

      {/* Τύπος Υποχρέωσης */}
      <div>
        <label htmlFor="obligation_type" className="block text-sm font-medium text-gray-700 mb-1">
          Τύπος Υποχρέωσης *
        </label>
        <select
          id="obligation_type"
          value={formData.obligation_type}
          onChange={(e) => handleChange('obligation_type', e.target.value)}
          className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.obligation_type ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          {OBLIGATION_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        {errors.obligation_type && (
          <p className="mt-1 text-sm text-red-500">{errors.obligation_type}</p>
        )}
      </div>

      {/* Περίοδος */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="period_month" className="block text-sm font-medium text-gray-700 mb-1">
            Μήνας
          </label>
          <select
            id="period_month"
            value={formData.period_month}
            onChange={(e) => handleChange('period_month', Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {MONTHS.map((month) => (
              <option key={month.value} value={month.value}>
                {month.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="period_year" className="block text-sm font-medium text-gray-700 mb-1">
            Έτος
          </label>
          <select
            id="period_year"
            value={formData.period_year}
            onChange={(e) => handleChange('period_year', Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {YEARS.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Προθεσμία */}
      <div>
        <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 mb-1">
          Προθεσμία *
        </label>
        <input
          type="date"
          id="due_date"
          value={formData.due_date}
          onChange={(e) => handleChange('due_date', e.target.value)}
          className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.due_date ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.due_date && <p className="mt-1 text-sm text-red-500">{errors.due_date}</p>}
      </div>

      {/* Κατάσταση */}
      <div>
        <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
          Κατάσταση
        </label>
        <select
          id="status"
          value={formData.status}
          onChange={(e) => handleChange('status', e.target.value as ObligationStatus)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {STATUS_OPTIONS.map((status) => (
            <option key={status.value} value={status.value}>
              {status.label}
            </option>
          ))}
        </select>
      </div>

      {/* Buttons */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={isLoading}>
          Ακύρωση
        </Button>
        <Button type="submit" variant="primary" isLoading={isLoading}>
          {obligation ? 'Αποθήκευση' : 'Δημιουργία'}
        </Button>
      </div>
    </form>
  );
}

export default ObligationForm;
