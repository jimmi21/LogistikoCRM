import { AlertTriangle } from 'lucide-react';
import { Modal } from './Modal';
import { Button } from './Button';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isLoading?: boolean;
  isPending?: boolean;  // Alias for isLoading
  variant?: 'danger' | 'warning';
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Επιβεβαίωση',
  cancelText = 'Ακύρωση',
  isLoading = false,
  isPending,
  variant = 'danger',
}: ConfirmDialogProps) {
  // Support both isLoading and isPending (isPending takes precedence if provided)
  const loading = isPending ?? isLoading;
  const iconColor = variant === 'danger' ? 'text-red-600' : 'text-yellow-600';
  const iconBg = variant === 'danger' ? 'bg-red-100' : 'bg-yellow-100';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <div className="flex flex-col items-center text-center">
        <div className={`p-3 ${iconBg} rounded-full mb-4`}>
          <AlertTriangle className={`w-6 h-6 ${iconColor}`} />
        </div>
        <p className="text-gray-600 mb-6">{message}</p>
        <div className="flex gap-3 w-full">
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={loading}
            className="flex-1"
          >
            {cancelText}
          </Button>
          <Button
            variant="danger"
            onClick={onConfirm}
            isLoading={loading}
            className="flex-1"
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

export default ConfirmDialog;
