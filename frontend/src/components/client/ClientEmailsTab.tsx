import { RefreshCw } from 'lucide-react';

// Email interface
export interface EmailItem {
  id: number;
  recipient_email: string;
  subject: string;
  status: string;
  status_display?: string;
  sent_at: string | null;
  template_name?: string | null;
}

// Props interface
export interface ClientEmailsTabProps {
  data: { emails: EmailItem[] } | undefined;
  isLoading: boolean;
}

export default function ClientEmailsTab({
  data,
  isLoading,
}: ClientEmailsTabProps) {
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
