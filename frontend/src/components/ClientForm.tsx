import { useState, useEffect, type FormEvent } from 'react';
import { Button } from './Button';
import { validateAfm } from '../utils/afm';
import type { Client, ClientFormData } from '../types';

interface ClientFormProps {
  client?: Client | null;
  onSubmit: (data: ClientFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function ClientForm({ client, onSubmit, onCancel, isLoading = false }: ClientFormProps) {
  const [formData, setFormData] = useState<ClientFormData>({
    afm: '',
    eponimia: '',
    email: '',
    kinito_tilefono: '',
    is_active: true,
  });
  const [errors, setErrors] = useState<Partial<Record<keyof ClientFormData, string>>>({});

  // Populate form when editing
  useEffect(() => {
    if (client) {
      setFormData({
        afm: client.afm || '',
        eponimia: client.eponimia || '',
        email: client.email || '',
        kinito_tilefono: client.kinito_tilefono || '',
        is_active: client.is_active ?? true,
      });
    }
  }, [client]);

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof ClientFormData, string>> = {};

    if (!formData.eponimia.trim()) {
      newErrors.eponimia = 'Η επωνυμία είναι υποχρεωτική';
    }

    if (!formData.afm.trim()) {
      newErrors.afm = 'Το ΑΦΜ είναι υποχρεωτικό';
    } else if (!validateAfm(formData.afm)) {
      newErrors.afm = 'Μη έγκυρο ΑΦΜ (πρέπει να είναι 9 ψηφία)';
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Μη έγκυρη διεύθυνση email';
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

  const handleChange = (field: keyof ClientFormData, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Επωνυμία */}
      <div>
        <label htmlFor="eponimia" className="block text-sm font-medium text-gray-700 mb-1">
          Επωνυμία *
        </label>
        <input
          type="text"
          id="eponimia"
          value={formData.eponimia}
          onChange={(e) => handleChange('eponimia', e.target.value)}
          className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.eponimia ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Εισάγετε επωνυμία"
        />
        {errors.eponimia && <p className="mt-1 text-sm text-red-500">{errors.eponimia}</p>}
      </div>

      {/* ΑΦΜ */}
      <div>
        <label htmlFor="afm" className="block text-sm font-medium text-gray-700 mb-1">
          ΑΦΜ *
        </label>
        <input
          type="text"
          id="afm"
          value={formData.afm}
          onChange={(e) => handleChange('afm', e.target.value.replace(/\D/g, '').slice(0, 9))}
          className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono ${
            errors.afm ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="123456789"
          maxLength={9}
        />
        {errors.afm && <p className="mt-1 text-sm text-red-500">{errors.afm}</p>}
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <input
          type="email"
          id="email"
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.email ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="example@email.com"
        />
        {errors.email && <p className="mt-1 text-sm text-red-500">{errors.email}</p>}
      </div>

      {/* Τηλέφωνο */}
      <div>
        <label htmlFor="kinito_tilefono" className="block text-sm font-medium text-gray-700 mb-1">
          Κινητό Τηλέφωνο
        </label>
        <input
          type="tel"
          id="kinito_tilefono"
          value={formData.kinito_tilefono}
          onChange={(e) => handleChange('kinito_tilefono', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="69xxxxxxxx"
        />
      </div>

      {/* Ενεργός */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="is_active"
          checked={formData.is_active}
          onChange={(e) => handleChange('is_active', e.target.checked)}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
          Ενεργός πελάτης
        </label>
      </div>

      {/* Buttons */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={isLoading}>
          Ακύρωση
        </Button>
        <Button type="submit" variant="primary" isLoading={isLoading}>
          {client ? 'Αποθήκευση' : 'Δημιουργία'}
        </Button>
      </div>
    </form>
  );
}

export default ClientForm;
