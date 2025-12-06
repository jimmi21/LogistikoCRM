import { useState, useEffect, type FormEvent } from 'react';
import { Search, Loader2, Check } from 'lucide-react';
import { Button } from './Button';
import { validateAfm } from '../utils/afm';
import { gsisApi, type AFMData } from '../api/client';
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
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupMessage, setLookupMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [fetchedData, setFetchedData] = useState<AFMData | null>(null);

  // Handle AFM lookup from GSIS
  const handleLookupAfm = async () => {
    if (!formData.afm || formData.afm.length !== 9) {
      setLookupMessage({ type: 'error', text: 'Εισάγετε έγκυρο ΑΦΜ (9 ψηφία)' });
      return;
    }

    setLookupLoading(true);
    setLookupMessage(null);
    setFetchedData(null);

    try {
      const result = await gsisApi.lookupAfm(formData.afm);

      if (result.success && result.data) {
        setFetchedData(result.data);
        // Αυτόματη συμπλήρωση επωνυμίας
        setFormData(prev => ({
          ...prev,
          eponimia: result.data?.onomasia || prev.eponimia,
        }));
        setLookupMessage({ type: 'success', text: 'Τα στοιχεία βρέθηκαν!' });
      } else {
        setLookupMessage({ type: 'error', text: result.error || 'Δεν βρέθηκαν στοιχεία' });
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Σφάλμα αναζήτησης';
      setLookupMessage({ type: 'error', text: errorMessage });
    } finally {
      setLookupLoading(false);
    }
  };

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
        <div className="flex gap-2">
          <input
            type="text"
            id="afm"
            value={formData.afm}
            onChange={(e) => {
              handleChange('afm', e.target.value.replace(/\D/g, '').slice(0, 9));
              setLookupMessage(null);
              setFetchedData(null);
            }}
            className={`flex-1 px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono ${
              errors.afm ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="123456789"
            maxLength={9}
          />
          <Button
            type="button"
            variant="secondary"
            onClick={handleLookupAfm}
            disabled={lookupLoading || formData.afm.length !== 9}
            title="Λήψη στοιχείων από ΑΑΔΕ"
          >
            {lookupLoading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Search size={18} />
            )}
          </Button>
        </div>
        {errors.afm && <p className="mt-1 text-sm text-red-500">{errors.afm}</p>}
        {lookupMessage && (
          <p className={`mt-1 text-sm flex items-center gap-1 ${
            lookupMessage.type === 'success' ? 'text-green-600' : 'text-red-500'
          }`}>
            {lookupMessage.type === 'success' && <Check size={14} />}
            {lookupMessage.text}
          </p>
        )}
      </div>

      {/* Fetched Data Preview */}
      {fetchedData && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
          <p className="font-medium text-blue-900 mb-2">Στοιχεία από ΑΑΔΕ:</p>
          <div className="grid grid-cols-2 gap-2 text-blue-800">
            <div>
              <span className="text-blue-600">Επωνυμία:</span> {fetchedData.onomasia}
            </div>
            <div>
              <span className="text-blue-600">ΔΟΥ:</span> {fetchedData.doy_descr}
            </div>
            {fetchedData.postal_address && (
              <div className="col-span-2">
                <span className="text-blue-600">Διεύθυνση:</span>{' '}
                {fetchedData.postal_address} {fetchedData.postal_address_no}, {fetchedData.postal_zip_code} {fetchedData.postal_area}
              </div>
            )}
            {fetchedData.legal_form_descr && (
              <div>
                <span className="text-blue-600">Μορφή:</span> {fetchedData.legal_form_descr}
              </div>
            )}
            {fetchedData.registration_date && (
              <div>
                <span className="text-blue-600">Έναρξη:</span> {fetchedData.registration_date}
              </div>
            )}
          </div>
        </div>
      )}

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
