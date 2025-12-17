/**
 * FileManager.tsx
 * Full-featured file manager page with browse, search, upload, share functionality
 */

import { useState, useCallback, useMemo } from 'react';
import {
  FolderOpen, Upload, Search, Grid, List, Filter, Star, Share2, Trash2,
  Download, Eye, ChevronRight, Home, Tag, Clock, HardDrive,
  FolderPlus, MoreVertical, CheckSquare, Square, X, Link2,
  FileText, Image, FileSpreadsheet, File, RefreshCw, Settings
} from 'lucide-react';
import { Layout } from '../components/layout';
import { Button } from '../components/Button';
import { Modal } from '../components/Modal';
import { ConfirmDialog } from '../components/ConfirmDialog';
import {
  useFileManagerDocuments,
  useFileManagerStats,
  useRecentDocuments,
  useBrowseFolders,
  useTags,
  useFavorites,
  useCollections,
  useUploadDocuments,
  useDeleteDocument,
  useBulkDeleteDocuments,
  useAddFavorite,
  useRemoveFavorite,
  useCreateSharedLink,
  downloadDocument,
  getFileIcon,
  getFileColor,
} from '../hooks/useFileManager';
import type {
  FileManagerDocument,
  DocumentFilters,
  ViewMode,
  DocumentCategory,
} from '../types/fileManager';
import { DOCUMENT_CATEGORIES, GREEK_MONTHS } from '../types/fileManager';
import { useClients } from '../hooks/useClients';

// File type icon component
function FileIcon({ fileType, size = 24 }: { fileType: string; size?: number }) {
  const type = fileType?.toLowerCase() || '';
  const color = getFileColor(type);

  if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(type)) {
    return <Image size={size} style={{ color }} />;
  }
  if (['xls', 'xlsx'].includes(type)) {
    return <FileSpreadsheet size={size} style={{ color }} />;
  }
  if (['pdf', 'doc', 'docx'].includes(type)) {
    return <FileText size={size} style={{ color }} />;
  }
  return <File size={size} style={{ color }} />;
}

// Stats card component
function StatCard({ icon: Icon, label, value, color }: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  color: string;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg`} style={{ backgroundColor: `${color}15` }}>
          <Icon size={20} style={{ color }} />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-500">{label}</p>
        </div>
      </div>
    </div>
  );
}

// Document card for grid view
function DocumentCard({
  document,
  isSelected,
  onSelect,
  onPreview,
  onDownload,
  onShare,
  onFavorite,
  onDelete,
}: {
  document: FileManagerDocument;
  isSelected: boolean;
  onSelect: () => void;
  onPreview: () => void;
  onDownload: () => void;
  onShare: () => void;
  onFavorite: () => void;
  onDelete: () => void;
}) {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div
      className={`bg-white rounded-lg border ${isSelected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'}
        p-4 hover:shadow-md transition-all cursor-pointer group relative`}
    >
      {/* Selection checkbox */}
      <button
        onClick={(e) => { e.stopPropagation(); onSelect(); }}
        className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity"
      >
        {isSelected ? (
          <CheckSquare size={20} className="text-blue-500" />
        ) : (
          <Square size={20} className="text-gray-400" />
        )}
      </button>

      {/* Menu button */}
      <div className="absolute top-2 right-2">
        <button
          onClick={(e) => { e.stopPropagation(); setShowMenu(!showMenu); }}
          className="p-1 rounded hover:bg-gray-100 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <MoreVertical size={16} className="text-gray-500" />
        </button>

        {showMenu && (
          <div className="absolute right-0 top-8 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10 min-w-[150px]">
            {document.can_preview && (
              <button
                onClick={() => { onPreview(); setShowMenu(false); }}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
              >
                <Eye size={14} /> Προβολή
              </button>
            )}
            <button
              onClick={() => { onDownload(); setShowMenu(false); }}
              className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
            >
              <Download size={14} /> Λήψη
            </button>
            <button
              onClick={() => { onShare(); setShowMenu(false); }}
              className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
            >
              <Share2 size={14} /> Κοινοποίηση
            </button>
            <button
              onClick={() => { onFavorite(); setShowMenu(false); }}
              className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
            >
              <Star size={14} fill={document.is_favorite ? '#F59E0B' : 'none'} />
              {document.is_favorite ? 'Αφαίρεση' : 'Αγαπημένο'}
            </button>
            <hr className="my-1" />
            <button
              onClick={() => { onDelete(); setShowMenu(false); }}
              className="w-full px-3 py-2 text-left text-sm hover:bg-red-50 text-red-600 flex items-center gap-2"
            >
              <Trash2 size={14} /> Διαγραφή
            </button>
          </div>
        )}
      </div>

      {/* File icon */}
      <div className="flex justify-center mb-3 pt-4" onClick={onPreview}>
        <FileIcon fileType={document.file_type} size={48} />
      </div>

      {/* File info */}
      <div className="text-center" onClick={onPreview}>
        <p className="font-medium text-gray-900 truncate" title={document.filename}>
          {document.filename}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {document.file_size_display} • {document.file_type.toUpperCase()}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          {document.client_name}
        </p>
      </div>

      {/* Tags */}
      {document.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2 justify-center">
          {document.tags.slice(0, 2).map((tag) => (
            <span
              key={tag.id}
              className="px-2 py-0.5 text-xs rounded-full"
              style={{ backgroundColor: `${tag.color}20`, color: tag.color }}
            >
              {tag.name}
            </span>
          ))}
          {document.tags.length > 2 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-500">
              +{document.tags.length - 2}
            </span>
          )}
        </div>
      )}

      {/* Status icons */}
      <div className="flex justify-center gap-2 mt-2">
        {document.is_favorite && <Star size={14} className="text-yellow-500" fill="#F59E0B" />}
        {document.shared_links_count > 0 && <Link2 size={14} className="text-blue-500" />}
        {document.version > 1 && (
          <span className="text-xs bg-gray-100 px-1.5 py-0.5 rounded text-gray-600">v{document.version}</span>
        )}
      </div>
    </div>
  );
}

// Document row for list view
function DocumentRow({
  document,
  isSelected,
  onSelect,
  onPreview,
  onDownload,
  onShare,
  onFavorite,
  onDelete,
}: {
  document: FileManagerDocument;
  isSelected: boolean;
  onSelect: () => void;
  onPreview: () => void;
  onDownload: () => void;
  onShare: () => void;
  onFavorite: () => void;
  onDelete: () => void;
}) {
  return (
    <tr className={`hover:bg-gray-50 ${isSelected ? 'bg-blue-50' : ''}`}>
      <td className="px-4 py-3">
        <button onClick={onSelect}>
          {isSelected ? (
            <CheckSquare size={18} className="text-blue-500" />
          ) : (
            <Square size={18} className="text-gray-400" />
          )}
        </button>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-3 cursor-pointer" onClick={onPreview}>
          <FileIcon fileType={document.file_type} size={24} />
          <div>
            <p className="font-medium text-gray-900">{document.filename}</p>
            <p className="text-xs text-gray-500">{document.client_name}</p>
          </div>
        </div>
      </td>
      <td className="px-4 py-3">
        <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
          {document.category_display}
        </span>
      </td>
      <td className="px-4 py-3 text-sm text-gray-500">{document.file_size_display}</td>
      <td className="px-4 py-3 text-sm text-gray-500">
        {new Date(document.uploaded_at).toLocaleDateString('el-GR')}
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-1">
          {document.tags.slice(0, 2).map((tag) => (
            <span
              key={tag.id}
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: tag.color }}
              title={tag.name}
            />
          ))}
        </div>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-1">
          <button onClick={onFavorite} className="p-1 rounded hover:bg-gray-100" title="Αγαπημένο">
            <Star size={16} className={document.is_favorite ? 'text-yellow-500' : 'text-gray-400'} fill={document.is_favorite ? '#F59E0B' : 'none'} />
          </button>
          {document.can_preview && (
            <button onClick={onPreview} className="p-1 rounded hover:bg-gray-100" title="Προβολή">
              <Eye size={16} className="text-gray-400" />
            </button>
          )}
          <button onClick={onDownload} className="p-1 rounded hover:bg-gray-100" title="Λήψη">
            <Download size={16} className="text-gray-400" />
          </button>
          <button onClick={onShare} className="p-1 rounded hover:bg-gray-100" title="Κοινοποίηση">
            <Share2 size={16} className="text-gray-400" />
          </button>
          <button onClick={onDelete} className="p-1 rounded hover:bg-red-100" title="Διαγραφή">
            <Trash2 size={16} className="text-gray-400 hover:text-red-500" />
          </button>
        </div>
      </td>
    </tr>
  );
}

// Upload Modal
function UploadModal({
  isOpen,
  onClose,
  onUpload,
  isLoading,
}: {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (files: File[], clientId: number, category: DocumentCategory) => void;
  isLoading: boolean;
}) {
  const [files, setFiles] = useState<File[]>([]);
  const [clientId, setClientId] = useState<number | null>(null);
  const [category, setCategory] = useState<DocumentCategory>('general');
  const [isDragging, setIsDragging] = useState(false);

  const { data: clientsData } = useClients({ page_size: 1000 });
  const clients = clientsData?.results || [];

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...droppedFiles]);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...selectedFiles]);
    }
  }, []);

  const removeFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleSubmit = () => {
    if (files.length > 0 && clientId) {
      onUpload(files, clientId, category);
    }
  };

  const reset = () => {
    setFiles([]);
    setClientId(null);
    setCategory('general');
  };

  return (
    <Modal isOpen={isOpen} onClose={() => { reset(); onClose(); }} title="Μεταφόρτωση Αρχείων" size="lg">
      <div className="space-y-4">
        {/* Client selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Πελάτης *</label>
          <select
            value={clientId || ''}
            onChange={(e) => setClientId(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Επιλέξτε πελάτη...</option>
            {clients.map((client) => (
              <option key={client.id} value={client.id}>
                {client.eponimia} ({client.afm})
              </option>
            ))}
          </select>
        </div>

        {/* Category selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Κατηγορία</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as DocumentCategory)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            {DOCUMENT_CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>

        {/* Drop zone */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            type="file"
            multiple
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.gif,.webp,.zip"
          />
          <Upload className="w-10 h-10 mx-auto text-gray-400 mb-3" />
          <p className="text-gray-600 font-medium">Σύρετε αρχεία εδώ ή κάντε κλικ</p>
          <p className="text-sm text-gray-400 mt-1">PDF, DOC, XLS, JPG, PNG, ZIP (max 10MB)</p>
        </div>

        {/* File list */}
        {files.length > 0 && (
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <FileIcon fileType={file.name.split('.').pop() || ''} size={20} />
                  <span className="text-sm truncate max-w-[200px]">{file.name}</span>
                  <span className="text-xs text-gray-400">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
                <button onClick={() => removeFile(index)} className="p-1 hover:bg-gray-200 rounded">
                  <X size={16} className="text-gray-500" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button variant="secondary" onClick={() => { reset(); onClose(); }}>Ακύρωση</Button>
          <Button
            onClick={handleSubmit}
            disabled={files.length === 0 || !clientId || isLoading}
          >
            {isLoading ? 'Μεταφόρτωση...' : `Μεταφόρτωση ${files.length} αρχείων`}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

// Share Modal
function ShareModal({
  isOpen,
  onClose,
  document,
  onShare,
  isLoading,
}: {
  isOpen: boolean;
  onClose: () => void;
  document: FileManagerDocument | null;
  onShare: (data: { documentId: number; expiresInDays?: number; password?: string }) => void;
  isLoading: boolean;
}) {
  const [expiresInDays, setExpiresInDays] = useState<number | undefined>(7);
  const [password, setPassword] = useState('');
  const [usePassword, setUsePassword] = useState(false);

  if (!document) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Κοινοποίηση Αρχείου" size="md">
      <div className="space-y-4">
        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
          <FileIcon fileType={document.file_type} size={32} />
          <div>
            <p className="font-medium">{document.filename}</p>
            <p className="text-sm text-gray-500">{document.file_size_display}</p>
          </div>
        </div>

        {/* Expiration */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Λήξη συνδέσμου</label>
          <select
            value={expiresInDays || ''}
            onChange={(e) => setExpiresInDays(e.target.value ? Number(e.target.value) : undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">Χωρίς λήξη</option>
            <option value="1">1 ημέρα</option>
            <option value="7">7 ημέρες</option>
            <option value="30">30 ημέρες</option>
            <option value="90">90 ημέρες</option>
          </select>
        </div>

        {/* Password protection */}
        <div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={usePassword}
              onChange={(e) => setUsePassword(e.target.checked)}
              className="w-4 h-4 rounded"
            />
            <span className="text-sm text-gray-700">Προστασία με κωδικό</span>
          </label>
          {usePassword && (
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Εισάγετε κωδικό..."
              className="mt-2 w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button variant="secondary" onClick={onClose}>Ακύρωση</Button>
          <Button
            onClick={() => onShare({
              documentId: document.id,
              expiresInDays,
              password: usePassword ? password : undefined,
            })}
            disabled={isLoading}
          >
            <Link2 size={16} className="mr-2" />
            {isLoading ? 'Δημιουργία...' : 'Δημιουργία Συνδέσμου'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

// Preview Modal
function PreviewModal({
  isOpen,
  onClose,
  document,
}: {
  isOpen: boolean;
  onClose: () => void;
  document: FileManagerDocument | null;
}) {
  if (!document) return null;

  const isPdf = document.file_type.toLowerCase() === 'pdf';
  const isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(document.file_type.toLowerCase());

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={document.filename} size="xl">
      <div className="min-h-[60vh]">
        {isPdf && document.file_url && (
          <iframe
            src={document.file_url}
            className="w-full h-[70vh] border-0"
            title={document.filename}
          />
        )}
        {isImage && document.file_url && (
          <div className="flex justify-center items-center h-[70vh]">
            <img
              src={document.file_url}
              alt={document.filename}
              className="max-w-full max-h-full object-contain"
            />
          </div>
        )}
        {!isPdf && !isImage && (
          <div className="flex flex-col items-center justify-center h-[40vh] text-gray-500">
            <FileIcon fileType={document.file_type} size={64} />
            <p className="mt-4">Δεν είναι δυνατή η προεπισκόπηση αυτού του τύπου αρχείου.</p>
            <Button
              className="mt-4"
              onClick={() => downloadDocument(document.id, document.filename)}
            >
              <Download size={16} className="mr-2" /> Λήψη αρχείου
            </Button>
          </div>
        )}
      </div>
    </Modal>
  );
}

// Main FileManager component
export default function FileManager() {
  // View state
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());

  // Filter state
  const [filters, setFilters] = useState<DocumentFilters>({
    page: 1,
    page_size: 24,
    ordering: '-uploaded_at',
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Modal state
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [previewModalOpen, setPreviewModalOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [activeDocument, setActiveDocument] = useState<FileManagerDocument | null>(null);

  // Data hooks
  const { data: documentsData, isLoading, refetch } = useFileManagerDocuments(filters);
  const { data: stats } = useFileManagerStats();
  const { data: tags } = useTags();
  const { data: favorites } = useFavorites();
  const { data: collectionsData } = useCollections();

  // Mutation hooks
  const uploadMutation = useUploadDocuments();
  const deleteMutation = useDeleteDocument();
  const bulkDeleteMutation = useBulkDeleteDocuments();
  const addFavoriteMutation = useAddFavorite();
  const removeFavoriteMutation = useRemoveFavorite();
  const createShareLinkMutation = useCreateSharedLink();

  const documents = documentsData?.results || [];
  const totalCount = documentsData?.count || 0;
  const collections = collectionsData?.results || [];

  // Handlers
  const handleSearch = useCallback(() => {
    setFilters((prev) => ({ ...prev, search: searchQuery, page: 1 }));
  }, [searchQuery]);

  const handleCategoryFilter = useCallback((category: DocumentCategory | '') => {
    setFilters((prev) => ({
      ...prev,
      category: category || undefined,
      page: 1,
    }));
  }, []);

  const handleUpload = useCallback(async (files: File[], clientId: number, category: DocumentCategory) => {
    try {
      await uploadMutation.mutateAsync({
        files,
        client_id: clientId,
        document_category: category,
      });
      setUploadModalOpen(false);
    } catch (error) {
      console.error('Upload error:', error);
    }
  }, [uploadMutation]);

  const handleShare = useCallback(async (data: { documentId: number; expiresInDays?: number; password?: string }) => {
    try {
      const result = await createShareLinkMutation.mutateAsync({
        document_id: data.documentId,
        expires_in_days: data.expiresInDays,
        password: data.password,
      });
      // Copy to clipboard
      const fullUrl = window.location.origin + result.public_url;
      await navigator.clipboard.writeText(fullUrl);
      alert(`Ο σύνδεσμος αντιγράφηκε: ${fullUrl}`);
      setShareModalOpen(false);
    } catch (error) {
      console.error('Share error:', error);
    }
  }, [createShareLinkMutation]);

  const handleDelete = useCallback(async () => {
    if (!activeDocument) return;
    try {
      await deleteMutation.mutateAsync(activeDocument.id);
      setDeleteConfirmOpen(false);
      setActiveDocument(null);
    } catch (error) {
      console.error('Delete error:', error);
    }
  }, [activeDocument, deleteMutation]);

  const handleBulkDelete = useCallback(async () => {
    if (selectedIds.size === 0) return;
    try {
      await bulkDeleteMutation.mutateAsync(Array.from(selectedIds));
      setSelectedIds(new Set());
    } catch (error) {
      console.error('Bulk delete error:', error);
    }
  }, [selectedIds, bulkDeleteMutation]);

  const handleToggleFavorite = useCallback(async (doc: FileManagerDocument) => {
    try {
      if (doc.is_favorite) {
        await removeFavoriteMutation.mutateAsync(doc.id);
      } else {
        await addFavoriteMutation.mutateAsync({ documentId: doc.id });
      }
    } catch (error) {
      console.error('Favorite error:', error);
    }
  }, [addFavoriteMutation, removeFavoriteMutation]);

  const toggleSelection = useCallback((id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const selectAll = useCallback(() => {
    if (selectedIds.size === documents.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(documents.map((d) => d.id)));
    }
  }, [documents, selectedIds.size]);

  return (
    <Layout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <FolderOpen className="text-blue-500" />
              Διαχείριση Αρχείων
            </h1>
            <p className="text-gray-500 mt-1">
              Οργανώστε, αναζητήστε και κοινοποιήστε τα αρχεία σας
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" onClick={() => refetch()}>
              <RefreshCw size={16} className="mr-2" /> Ανανέωση
            </Button>
            <Button onClick={() => setUploadModalOpen(true)}>
              <Upload size={16} className="mr-2" /> Μεταφόρτωση
            </Button>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <StatCard
              icon={File}
              label="Συνολικά Αρχεία"
              value={stats.total_documents}
              color="#3B82F6"
            />
            <StatCard
              icon={HardDrive}
              label="Αποθηκευτικός Χώρος"
              value={stats.total_size_display}
              color="#10B981"
            />
            <StatCard
              icon={Clock}
              label="Πρόσφατα (7 ημέρες)"
              value={stats.recent_uploads_count}
              color="#F59E0B"
            />
            <StatCard
              icon={Link2}
              label="Ενεργοί Σύνδεσμοι"
              value={stats.active_shared_links}
              color="#8B5CF6"
            />
          </div>
        )}

        {/* Search and filters bar */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            {/* Search */}
            <div className="flex-1 min-w-[200px] relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Αναζήτηση αρχείων..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Category filter */}
            <select
              value={filters.category || ''}
              onChange={(e) => handleCategoryFilter(e.target.value as DocumentCategory | '')}
              className="px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Όλες οι κατηγορίες</option>
              {DOCUMENT_CATEGORIES.map((cat) => (
                <option key={cat.value} value={cat.value}>{cat.label}</option>
              ))}
            </select>

            {/* View mode toggle */}
            <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-blue-50 text-blue-600' : 'text-gray-500'}`}
              >
                <Grid size={18} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 ${viewMode === 'list' ? 'bg-blue-50 text-blue-600' : 'text-gray-500'}`}
              >
                <List size={18} />
              </button>
            </div>

            {/* More filters */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-3 py-2 border rounded-lg ${showFilters ? 'border-blue-500 text-blue-600' : 'border-gray-300 text-gray-500'}`}
            >
              <Filter size={18} /> Φίλτρα
            </button>
          </div>

          {/* Extended filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm text-gray-500 mb-1">Έτος</label>
                <select
                  value={filters.year || ''}
                  onChange={(e) => setFilters((prev) => ({ ...prev, year: e.target.value ? Number(e.target.value) : undefined }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Όλα</option>
                  {[2025, 2024, 2023, 2022].map((year) => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Μήνας</label>
                <select
                  value={filters.month || ''}
                  onChange={(e) => setFilters((prev) => ({ ...prev, month: e.target.value ? Number(e.target.value) : undefined }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Όλοι</option>
                  {GREEK_MONTHS.map((month, index) => (
                    <option key={index} value={index + 1}>{month}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Τύπος αρχείου</label>
                <select
                  value={filters.file_type || ''}
                  onChange={(e) => setFilters((prev) => ({ ...prev, file_type: e.target.value || undefined }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Όλοι</option>
                  <option value="pdf">PDF</option>
                  <option value="xlsx">Excel</option>
                  <option value="docx">Word</option>
                  <option value="jpg">Εικόνες</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Ετικέτα</label>
                <select
                  value={filters.tag || ''}
                  onChange={(e) => setFilters((prev) => ({ ...prev, tag: e.target.value || undefined }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Όλες</option>
                  {tags?.map((tag) => (
                    <option key={tag.id} value={tag.name}>{tag.name}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Bulk actions bar */}
        {selectedIds.size > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4 flex items-center justify-between">
            <span className="text-blue-700">
              Επιλεγμένα: {selectedIds.size} αρχεία
            </span>
            <div className="flex items-center gap-2">
              <Button variant="secondary" size="sm" onClick={() => setSelectedIds(new Set())}>
                Ακύρωση
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleBulkDelete}
                className="text-red-600 hover:bg-red-50"
              >
                <Trash2 size={14} className="mr-1" /> Διαγραφή
              </Button>
            </div>
          </div>
        )}

        {/* Documents display */}
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <FolderOpen size={48} className="mx-auto mb-4 text-gray-300" />
            <p>Δεν βρέθηκαν αρχεία</p>
            <Button className="mt-4" onClick={() => setUploadModalOpen(true)}>
              <Upload size={16} className="mr-2" /> Μεταφορτώστε το πρώτο αρχείο
            </Button>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {documents.map((doc) => (
              <DocumentCard
                key={doc.id}
                document={doc}
                isSelected={selectedIds.has(doc.id)}
                onSelect={() => toggleSelection(doc.id)}
                onPreview={() => { setActiveDocument(doc); setPreviewModalOpen(true); }}
                onDownload={() => downloadDocument(doc.id, doc.filename)}
                onShare={() => { setActiveDocument(doc); setShareModalOpen(true); }}
                onFavorite={() => handleToggleFavorite(doc)}
                onDelete={() => { setActiveDocument(doc); setDeleteConfirmOpen(true); }}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left">
                    <button onClick={selectAll}>
                      {selectedIds.size === documents.length ? (
                        <CheckSquare size={18} className="text-blue-500" />
                      ) : (
                        <Square size={18} className="text-gray-400" />
                      )}
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Αρχείο</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Κατηγορία</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Μέγεθος</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Ημερομηνία</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Ετικέτες</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Ενέργειες</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {documents.map((doc) => (
                  <DocumentRow
                    key={doc.id}
                    document={doc}
                    isSelected={selectedIds.has(doc.id)}
                    onSelect={() => toggleSelection(doc.id)}
                    onPreview={() => { setActiveDocument(doc); setPreviewModalOpen(true); }}
                    onDownload={() => downloadDocument(doc.id, doc.filename)}
                    onShare={() => { setActiveDocument(doc); setShareModalOpen(true); }}
                    onFavorite={() => handleToggleFavorite(doc)}
                    onDelete={() => { setActiveDocument(doc); setDeleteConfirmOpen(true); }}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalCount > (filters.page_size || 24) && (
          <div className="flex justify-center items-center gap-4 mt-6">
            <Button
              variant="secondary"
              disabled={filters.page === 1}
              onClick={() => setFilters((prev) => ({ ...prev, page: (prev.page || 1) - 1 }))}
            >
              Προηγούμενη
            </Button>
            <span className="text-gray-500">
              Σελίδα {filters.page} από {Math.ceil(totalCount / (filters.page_size || 24))}
            </span>
            <Button
              variant="secondary"
              disabled={(filters.page || 1) * (filters.page_size || 24) >= totalCount}
              onClick={() => setFilters((prev) => ({ ...prev, page: (prev.page || 1) + 1 }))}
            >
              Επόμενη
            </Button>
          </div>
        )}
      </div>

      {/* Modals */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUpload={handleUpload}
        isLoading={uploadMutation.isPending}
      />

      <ShareModal
        isOpen={shareModalOpen}
        onClose={() => { setShareModalOpen(false); setActiveDocument(null); }}
        document={activeDocument}
        onShare={handleShare}
        isLoading={createShareLinkMutation.isPending}
      />

      <PreviewModal
        isOpen={previewModalOpen}
        onClose={() => { setPreviewModalOpen(false); setActiveDocument(null); }}
        document={activeDocument}
      />

      <ConfirmDialog
        isOpen={deleteConfirmOpen}
        onClose={() => { setDeleteConfirmOpen(false); setActiveDocument(null); }}
        onConfirm={handleDelete}
        title="Διαγραφή Αρχείου"
        message={`Είστε σίγουροι ότι θέλετε να διαγράψετε το αρχείο "${activeDocument?.filename}";`}
        confirmText="Διαγραφή"
        cancelText="Ακύρωση"
        variant="danger"
      />
    </Layout>
  );
}
