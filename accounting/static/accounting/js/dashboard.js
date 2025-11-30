/**
 * Dashboard JavaScript - Ολοκλήρωση & File Upload
 * Διορθώνει τα missing functions και προσθέτει αρχειοθέτηση
 */

// ============================================================================
// QUICK COMPLETE - Γρήγορη Ολοκλήρωση Υποχρέωσης
// ============================================================================

function quickComplete(obligationId) {
    if (!confirm('Είστε σίγουροι ότι θέλετε να ολοκληρώσετε αυτήν την υποχρέωση;')) {
        return;
    }

    // Show loading state
    const btn = event.currentTarget;
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="icon">⏳</span><span class="label">Επεξεργασία...</span>';

    // AJAX request
    fetch(`/accounting/obligation/${obligationId}/complete/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            status: 'completed'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Success notification
            showNotification('✅ Η υποχρέωση ολοκληρώθηκε επιτυχώς!', 'success');

            // Reload page after short delay
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            throw new Error(data.error || 'Σφάλμα κατά την ολοκλήρωση');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('❌ Σφάλμα: ' + error.message, 'error');

        // Restore button
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    });
}


// ============================================================================
// COMPLETE WITH FILE - Ολοκλήρωση με Ανέβασμα Αρχείου
// ============================================================================

function completeWithFile(obligationId) {
    // Show file upload modal
    showFileUploadModal(obligationId);
}

function showFileUploadModal(obligationId) {
    const modal = document.getElementById('file-upload-modal');
    if (!modal) {
        createFileUploadModal();
    }

    const modalElement = document.getElementById('file-upload-modal');
    modalElement.dataset.obligationId = obligationId;
    modalElement.style.display = 'flex';

    // Reset form
    document.getElementById('upload-form').reset();
}

function createFileUploadModal() {
    const modalHTML = `
    <div id="file-upload-modal" class="modal" style="display: none;">
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h2>📎 Ανέβασμα Αρχείου & Ολοκλήρωση</h2>
                <button type="button" class="modal-close" onclick="closeFileUploadModal()">&times;</button>
            </div>

            <form id="upload-form" onsubmit="handleFileUpload(event)">
                <div class="modal-body">
                    <!-- File Upload -->
                    <div class="form-group">
                        <label for="file-input" class="form-label">
                            <span class="icon">📄</span>
                            Επιλογή Αρχείου *
                        </label>
                        <input type="file"
                               id="file-input"
                               name="file"
                               required
                               accept=".pdf,.xlsx,.xls,.docx,.doc,.jpg,.jpeg,.png"
                               class="file-input">
                        <small class="help-text">Επιτρεπόμενοι τύποι: PDF, Excel, Word, εικόνες</small>
                    </div>

                    <!-- Category -->
                    <div class="form-group">
                        <label for="file-category" class="form-label">
                            <span class="icon">📁</span>
                            Κατηγορία Εγγράφου
                        </label>
                        <select id="file-category" name="category" class="form-select">
                            <option value="general">📁 Γενικά</option>
                            <option value="tax">📋 Φορολογικά</option>
                            <option value="vat">💶 ΦΠΑ</option>
                            <option value="myf">📊 ΜΥΦ</option>
                            <option value="invoices">🧾 Τιμολόγια</option>
                            <option value="contracts">📜 Συμβάσεις</option>
                            <option value="payroll">👥 Μισθοδοσία</option>
                        </select>
                    </div>

                    <!-- Description -->
                    <div class="form-group">
                        <label for="file-description" class="form-label">
                            <span class="icon">📝</span>
                            Περιγραφή (προαιρετικό)
                        </label>
                        <textarea id="file-description"
                                  name="description"
                                  rows="3"
                                  class="form-textarea"
                                  placeholder="Προσθέστε σημειώσεις για το αρχείο..."></textarea>
                    </div>

                    <!-- Time Spent -->
                    <div class="form-group">
                        <label for="time-spent" class="form-label">
                            <span class="icon">⏱️</span>
                            Χρόνος Εργασίας (ώρες)
                        </label>
                        <input type="number"
                               id="time-spent"
                               name="time_spent"
                               step="0.25"
                               min="0"
                               class="form-input"
                               placeholder="π.χ. 1.5">
                    </div>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeFileUploadModal()">
                        Ακύρωση
                    </button>
                    <button type="submit" class="btn btn-success">
                        <span class="icon">✓</span>
                        <span>Ανέβασμα & Ολοκλήρωση</span>
                    </button>
                </div>
            </form>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeFileUploadModal() {
    const modal = document.getElementById('file-upload-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function handleFileUpload(event) {
    event.preventDefault();

    const modal = document.getElementById('file-upload-modal');
    const obligationId = modal.dataset.obligationId;
    const form = event.target;
    const formData = new FormData(form);

    // Disable submit button
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalHTML = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="icon">⏳</span><span>Ανέβασμα...</span>';

    // Upload file and complete
    fetch(`/accounting/obligation/${obligationId}/complete-with-file/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('✅ Το αρχείο ανέβηκε και η υποχρέωση ολοκληρώθηκε!', 'success');
            closeFileUploadModal();

            // Reload page
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            throw new Error(data.error || 'Σφάλμα κατά το ανέβασμα');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('❌ Σφάλμα: ' + error.message, 'error');

        // Restore button
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalHTML;
    });
}


// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

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

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// ============================================================================
// Initialize on page load
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard JavaScript loaded ✅');

    // Create modal if it doesn't exist
    if (!document.getElementById('file-upload-modal')) {
        createFileUploadModal();
    }
});


// ============================================================================
// NAVIGATION
// ============================================================================

function navigateToObligation(obligationId) {
    window.location.href = `/accounting/obligation/${obligationId}/`;
}
