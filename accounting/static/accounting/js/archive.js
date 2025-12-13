/**
 * Archive & Duplicate Handling JavaScript
 * LogistikoCRM - ArchiveService Integration
 *
 * Handles file uploads με duplicate detection και user choice modal.
 */

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Format file size in human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size (e.g., "1.5 MB")
 */
function formatSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Format datetime string
 * @param {string} dateString - ISO datetime string
 * @returns {string} Formatted date (e.g., "13/12/2025 15:30")
 */
function formatDate(dateString) {
    if (!dateString) return '-';

    try {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        return `${day}/${month}/${year} ${hours}:${minutes}`;
    } catch (e) {
        return dateString;
    }
}

// =============================================================================
// DUPLICATE HANDLER CLASS
// =============================================================================

class DuplicateHandler {
    /**
     * Handles file upload με automatic duplicate detection.
     *
     * @param {string} url - Upload endpoint URL
     * @param {FormData} formData - Form data με file
     * @param {Function} onSuccess - Callback on successful upload
     * @param {Function} onError - Callback on error (optional)
     */
    static async handleUpload(url, formData, onSuccess, onError = null) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            // Check if duplicate decision required
            if (data.requires_decision) {
                const action = await DuplicateHandler.showModal(data.existing_file, data.new_file, data.suggested_path);

                if (action) {
                    // User made a choice, retry upload με on_duplicate parameter
                    formData.append('on_duplicate', action);
                    return DuplicateHandler.handleUpload(url, formData, onSuccess, onError);
                } else {
                    // User cancelled
                    if (onError) {
                        onError({error: 'Ο χρήστης ακύρωσε την αποθήκευση'});
                    }
                    return;
                }
            }

            // Check if successful
            if (data.success) {
                if (onSuccess) {
                    onSuccess(data);
                }
            } else {
                // Error occurred
                const errorMsg = data.error || 'Άγνωστο σφάλμα';
                console.error('Upload error:', errorMsg);

                if (onError) {
                    onError(data);
                } else {
                    alert('Σφάλμα: ' + errorMsg);
                }
            }

        } catch (error) {
            console.error('Network error:', error);

            if (onError) {
                onError({error: error.message});
            } else {
                alert('Σφάλμα δικτύου: ' + error.message);
            }
        }
    }

    /**
     * Εμφανίζει το modal για duplicate file choice.
     *
     * @param {Object} existingFile - Info about existing file {name, size, modified}
     * @param {Object} newFile - Info about new file {name, size}
     * @param {string} suggestedPath - Suggested versioned path if keep_both
     * @returns {Promise<string|null>} User choice: 'replace' | 'keep_both' | null (cancelled)
     */
    static showModal(existingFile, newFile, suggestedPath = null) {
        return new Promise((resolve) => {
            const modalElement = document.getElementById('duplicateFileModal');

            if (!modalElement) {
                console.error('Duplicate modal not found in page!');
                // Fallback: ask via confirm
                const replace = confirm('Το αρχείο υπάρχει ήδη. Θέλετε να το αντικαταστήσετε;');
                resolve(replace ? 'replace' : null);
                return;
            }

            // Populate modal με file info
            const modal = new bootstrap.Modal(modalElement);

            // Existing file
            document.getElementById('duplicateFileName').textContent = existingFile.name || '-';
            document.getElementById('existingFileName').textContent = existingFile.name || '-';
            document.getElementById('existingFileName').title = existingFile.name || '';
            document.getElementById('existingFileSize').textContent = formatSize(existingFile.size || 0);
            document.getElementById('existingFileDate').textContent = formatDate(existingFile.modified);

            // New file
            document.getElementById('newFileName').textContent = newFile.name || '-';
            document.getElementById('newFileName').title = newFile.name || '';
            document.getElementById('newFileSize').textContent = formatSize(newFile.size || 0);

            // Suggested path (if keep_both)
            if (suggestedPath) {
                document.getElementById('suggestedPath').textContent = suggestedPath;
                document.getElementById('suggestedPathContainer').style.display = 'block';
            } else {
                document.getElementById('suggestedPathContainer').style.display = 'none';
            }

            // Button handlers
            const btnReplace = document.getElementById('btnReplace');
            const btnKeepBoth = document.getElementById('btnKeepBoth');

            // Remove previous listeners (avoid duplicates)
            const newBtnReplace = btnReplace.cloneNode(true);
            const newBtnKeepBoth = btnKeepBoth.cloneNode(true);
            btnReplace.replaceWith(newBtnReplace);
            btnKeepBoth.replaceWith(newBtnKeepBoth);

            // Add new listeners
            newBtnReplace.onclick = () => {
                modal.hide();
                resolve('replace');
            };

            newBtnKeepBoth.onclick = () => {
                modal.hide();
                resolve('keep_both');
            };

            // Cancel handler
            modalElement.addEventListener('hidden.bs.modal', function onModalHidden() {
                // Called when modal is closed without choice
                modalElement.removeEventListener('hidden.bs.modal', onModalHidden);
                resolve(null);
            }, {once: true});

            // Show modal
            modal.show();
        });
    }
}

// =============================================================================
// SIMPLE UPLOAD WRAPPER (για compatibility με υπάρχοντα forms)
// =============================================================================

/**
 * Simple wrapper για standard file upload forms.
 *
 * Usage στο HTML:
 * <form id="uploadForm" action="/upload/" method="POST" enctype="multipart/form-data">
 *   <input type="file" name="file" required>
 *   <button type="submit">Upload</button>
 * </form>
 *
 * <script>
 *   setupDuplicateHandling('uploadForm', (data) => {
 *     console.log('Upload success:', data);
 *     window.location.reload();
 *   });
 * </script>
 */
function setupDuplicateHandling(formId, onSuccess, onError = null) {
    const form = document.getElementById(formId);

    if (!form) {
        console.error(`Form "${formId}" not found`);
        return;
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const url = form.action;

        DuplicateHandler.handleUpload(url, formData, onSuccess, onError);
    });
}

// =============================================================================
// EXPORT (if using modules)
// =============================================================================

// For module usage:
// export { DuplicateHandler, setupDuplicateHandling, formatSize, formatDate };

// For global usage (current approach):
window.DuplicateHandler = DuplicateHandler;
window.setupDuplicateHandling = setupDuplicateHandling;
window.formatFileSize = formatSize;
window.formatFileDate = formatDate;
