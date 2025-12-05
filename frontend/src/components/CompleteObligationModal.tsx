/**
 * CompleteObligationModal.tsx
 * Modal for completing an obligation with optional document attachment and email notification
 */

import { useState, useRef, useCallback } from 'react';
import { CheckCircle, Upload, File, X, AlertCircle, Mail } from 'lucide-react';
import { Modal } from './Modal';
import { Button } from './Button';
import { useEmailTemplates } from '../hooks/useEmail';
import type { Obligation, EmailTemplate, ClientDocument } from '../types';

interface CompleteObligationModalProps {
  isOpen: boolean;
  onClose: () => void;
  obligation: Obligation | null;
  clientName: string;
  clientEmail?: string;
  existingDocuments?: ClientDocument[];
  onComplete: (data: {
    file?: File | null;
    documentId?: number | null;
    sendEmail: boolean;
    emailTemplateId?: number | null;
    notes: string;
    timeSpent?: number | null;
  }) => Promise<void>;
  isLoading?: boolean;
}

const ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png'];
const MAX_FILE_SIZE = 10 * 1024 * 1024;

export function CompleteObligationModal({
  isOpen,
  onClose,
  obligation,
  clientName,
  clientEmail,
  existingDocuments = [],
  onComplete,
  isLoading = false,
}: CompleteObligationModalProps) {
  const [attachDocument, setAttachDocument] = useState(false);
  const [documentSource, setDocumentSource] = useState<'upload' | 'existing'>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [sendEmail, setSendEmail] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [notes, setNotes] = useState('');
  const [timeSpent, setTimeSpent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: templates } = useEmailTemplates();

  const validateFile = useCallback((file: File): string | null => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `Μη επιτρεπτός τύπος αρχείου. Επιτρέπονται: ${ALLOWED_EXTENSIONS.join(', ')}`;
    }
    if (file.size > MAX_FILE_SIZE) {
      return 'Το αρχείο είναι μεγαλύτερο από 10MB.';
    }
    return null;
  }, []);

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0];
      if (selectedFile) {
        const validationError = validateFile(selectedFile);
        if (validationError) {
          setError(validationError);
          return;
        }
        setFile(selectedFile);
        setSelectedDocId(null);
        setError(null);
      }
    },
    [validateFile]
  );

  const handleSubmit = async () => {
    try {
      await onComplete({
        file: attachDocument && documentSource === 'upload' ? file : null,
        documentId: attachDocument && documentSource === 'existing' ? selectedDocId : null,
        sendEmail: sendEmail && !!clientEmail,
        emailTemplateId: sendEmail && selectedTemplate ? selectedTemplate : null,
        notes,
        timeSpent: timeSpent ? parseFloat(timeSpent) : null,
      });
      handleClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Σφάλμα κατά την ολοκλήρωση');
    }
  };

  const handleClose = () => {
    setAttachDocument(false);
    setDocumentSource('upload');
    setFile(null);
    setSelectedDocId(null);
    setSendEmail(true);
    setSelectedTemplate(null);
    setNotes('');
    setTimeSpent('');
    setError(null);
    onClose();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  if (!obligation) return null;

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Ολοκλήρωση Υποχρέωσης" size="lg">
      <div className="space-y-4">
        {/* Obligation info */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-8 h-8 text-green-500" />
            <div>
              <p className="font-medium text-gray-900">
                {obligation.type_name || obligation.type_code}
              </p>
              <p className="text-sm text-gray-500">
                {clientName} - {String(obligation.month).padStart(2, '0')}/{obligation.year}
              </p>
            </div>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <span className="text-sm text-red-700">{error}</span>
          </div>
        )}

        {/* Attach document option */}
        <div className="border border-gray-200 rounded-lg p-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={attachDocument}
              onChange={(e) => setAttachDocument(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <span className="font-medium text-gray-900">Επισύναψη εγγράφου</span>
          </label>

          {attachDocument && (
            <div className="mt-4 space-y-3 pl-6">
              {/* Document source selection */}
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    checked={documentSource === 'upload'}
                    onChange={() => setDocumentSource('upload')}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-sm">Μεταφόρτωση νέου</span>
                </label>
                {existingDocuments.length > 0 && (
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={documentSource === 'existing'}
                      onChange={() => setDocumentSource('existing')}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="text-sm">Επιλογή υπάρχοντος</span>
                  </label>
                )}
              </div>

              {/* Upload file */}
              {documentSource === 'upload' && (
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileSelect}
                    accept={ALLOWED_EXTENSIONS.join(',')}
                    className="hidden"
                  />
                  {file ? (
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <File className="w-6 h-6 text-blue-500" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{file.name}</p>
                        <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                      <button
                        onClick={() => setFile(null)}
                        className="p-1 hover:bg-gray-200 rounded"
                      >
                        <X className="w-4 h-4 text-gray-400" />
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="flex items-center gap-2 px-4 py-2 border border-dashed border-gray-300 rounded-lg hover:border-gray-400 transition-colors"
                    >
                      <Upload className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">Επιλογή αρχείου...</span>
                    </button>
                  )}
                </div>
              )}

              {/* Select existing document */}
              {documentSource === 'existing' && existingDocuments.length > 0 && (
                <select
                  value={selectedDocId || ''}
                  onChange={(e) => setSelectedDocId(e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="">-- Επιλέξτε έγγραφο --</option>
                  {existingDocuments.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.filename}
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}
        </div>

        {/* Send email option */}
        <div className="border border-gray-200 rounded-lg p-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={sendEmail}
              onChange={(e) => setSendEmail(e.target.checked)}
              disabled={!clientEmail}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <Mail className="w-4 h-4 text-gray-400" />
            <span className="font-medium text-gray-900">Αποστολή email ενημέρωσης</span>
            {!clientEmail && (
              <span className="text-xs text-gray-400">(ο πελάτης δεν έχει email)</span>
            )}
          </label>

          {sendEmail && clientEmail && (
            <div className="mt-4 pl-6">
              <label className="block text-sm text-gray-600 mb-1">Πρότυπο</label>
              <select
                value={selectedTemplate || ''}
                onChange={(e) =>
                  setSelectedTemplate(e.target.value ? Number(e.target.value) : null)
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="">Αυτόματη επιλογή</option>
                {templates?.map((template: EmailTemplate) => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Σημειώσεις
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Προαιρετικές σημειώσεις..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm resize-y"
          />
        </div>

        {/* Time spent */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Χρόνος εργασίας (ώρες)
          </label>
          <input
            type="number"
            value={timeSpent}
            onChange={(e) => setTimeSpent(e.target.value)}
            placeholder="π.χ. 1.5"
            step="0.25"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          <Button variant="secondary" onClick={handleClose} disabled={isLoading}>
            Ακύρωση
          </Button>
          <Button
            onClick={handleSubmit}
            isLoading={isLoading}
            disabled={isLoading}
            className="flex-1"
          >
            <CheckCircle className="w-4 h-4 mr-2" />
            Ολοκλήρωση
          </Button>
        </div>
      </div>
    </Modal>
  );
}

export default CompleteObligationModal;
