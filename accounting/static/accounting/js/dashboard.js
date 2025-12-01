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
// COMPLETION MODAL - Ολοκλήρωση (με προαιρετικό αρχείο & email)
// ============================================================================

function showCompletionModal(obligationId) {
    const modal = document.getElementById('completion-modal');
    if (!modal) {
        createCompletionModal();
    }

    const modalElement = document.getElementById('completion-modal');
    modalElement.dataset.obligationId = obligationId;
    modalElement.style.display = 'flex';

    // Reset form
    document.getElementById('completion-form').reset();
}

// Legacy function - for backwards compatibility
function completeWithFile(obligationId) {
    showCompletionModal(obligationId);
}

function createCompletionModal() {
    const modalHTML = `
    <div id="completion-modal" class="modal" style="display: none;">
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h2>✓ Ολοκλήρωση Υποχρέωσης</h2>
                <button type="button" class="modal-close" onclick="closeCompletionModal()">&times;</button>
            </div>

            <form id="completion-form" onsubmit="handleCompletion(event)">
                <div class="modal-body">
                    <!-- File Upload (OPTIONAL) -->
                    <div class="form-group">
                        <label for="file-input" class="form-label">
                            <span class="icon">📎</span>
                            Επισύναψη Αρχείου (προαιρετικό)
                        </label>
                        <input type="file"
                               id="file-input"
                               name="file"
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

                    <!-- Email Notification -->
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox"
                                   id="send-email"
                                   name="send_email"
                                   value="1"
                                   class="form-checkbox">
                            <span class="icon">📧</span>
                            <span>Αποστολή email ειδοποίησης στον πελάτη</span>
                        </label>
                        <small class="help-text">Ο πελάτης θα ενημερωθεί για την ολοκλήρωση της υποχρέωσης</small>
                    </div>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeCompletionModal()">
                        Ακύρωση
                    </button>
                    <button type="submit" class="btn btn-success">
                        <span class="icon">✓</span>
                        <span>Ολοκλήρωση</span>
                    </button>
                </div>
            </form>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeCompletionModal() {
    const modal = document.getElementById('completion-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Legacy function
function closeFileUploadModal() {
    closeCompletionModal();
}

function handleCompletion(event) {
    event.preventDefault();

    const modal = document.getElementById('completion-modal');
    const obligationId = modal.dataset.obligationId;
    const form = event.target;
    const fileInput = form.querySelector('#file-input');
    const hasFile = fileInput && fileInput.files && fileInput.files.length > 0;

    // Disable submit button
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalHTML = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="icon">⏳</span><span>Ολοκλήρωση...</span>';

    if (hasFile) {
        // Complete WITH file upload
        const formData = new FormData(form);

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
                closeCompletionModal();
                setTimeout(() => window.location.reload(), 1000);
            } else {
                throw new Error(data.error || 'Σφάλμα κατά το ανέβασμα');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('❌ Σφάλμα: ' + error.message, 'error');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalHTML;
        });
    } else {
        // Complete WITHOUT file (simple completion)
        const sendEmail = form.querySelector('#send-email').checked;
        const timeSpent = form.querySelector('#time-spent').value;

        fetch(`/accounting/obligation/${obligationId}/complete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                status: 'completed',
                send_email: sendEmail,
                time_spent: timeSpent || null
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ Η υποχρέωση ολοκληρώθηκε επιτυχώς!', 'success');
                closeCompletionModal();
                setTimeout(() => window.location.reload(), 1000);
            } else {
                throw new Error(data.error || 'Σφάλμα κατά την ολοκλήρωση');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('❌ Σφάλμα: ' + error.message, 'error');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalHTML;
        });
    }
}

// Legacy function - for backwards compatibility
function handleFileUpload(event) {
    handleCompletion(event);
}


// ============================================================================
// BULK COMPLETION - Μαζική Ολοκλήρωση
// ============================================================================

function showBulkCompletionModal(obligationIds) {
    const modal = document.getElementById('bulk-completion-modal');
    if (!modal) {
        createBulkCompletionModal();
    }

    const modalElement = document.getElementById('bulk-completion-modal');
    modalElement.dataset.obligationIds = JSON.stringify(obligationIds);
    modalElement.style.display = 'flex';

    // Update count in modal
    document.getElementById('bulk-modal-count').textContent = obligationIds.length;

    // Reset form
    document.getElementById('bulk-completion-form').reset();
}

function createBulkCompletionModal() {
    const modalHTML = `
    <div id="bulk-completion-modal" class="modal" style="display: none;">
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h2>✓ Μαζική Ολοκλήρωση <span class="badge" id="bulk-modal-count">0</span> Υποχρεώσεων</h2>
                <button type="button" class="modal-close" onclick="closeBulkCompletionModal()">&times;</button>
            </div>

            <form id="bulk-completion-form" onsubmit="handleBulkCompletion(event)">
                <div class="modal-body">
                    <!-- File Upload (OPTIONAL) -->
                    <div class="form-group">
                        <label for="bulk-file-input" class="form-label">
                            <span class="icon">📎</span>
                            Επισύναψη Αρχείου (προαιρετικό - κοινό για όλες)
                        </label>
                        <input type="file"
                               id="bulk-file-input"
                               name="file"
                               accept=".pdf,.xlsx,.xls,.docx,.doc,.jpg,.jpeg,.png,.zip"
                               class="file-input">
                        <small class="help-text">Το αρχείο θα επισυναφθεί σε όλες τις επιλεγμένες υποχρεώσεις</small>
                    </div>

                    <!-- Category -->
                    <div class="form-group">
                        <label for="bulk-file-category" class="form-label">
                            <span class="icon">📁</span>
                            Κατηγορία Εγγράφου
                        </label>
                        <select id="bulk-file-category" name="category" class="form-select">
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
                        <label for="bulk-description" class="form-label">
                            <span class="icon">📝</span>
                            Περιγραφή (προαιρετικό)
                        </label>
                        <textarea id="bulk-description"
                                  name="description"
                                  rows="3"
                                  class="form-textarea"
                                  placeholder="Κοινές σημειώσεις για όλες τις υποχρεώσεις..."></textarea>
                    </div>

                    <!-- Email Notification -->
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox"
                                   id="bulk-send-email"
                                   name="send_email"
                                   value="1"
                                   class="form-checkbox">
                            <span class="icon">📧</span>
                            <span>Αποστολή email στους πελάτες</span>
                        </label>
                        <small class="help-text">Κάθε πελάτης θα ενημερωθεί για τις δικές του υποχρεώσεις</small>
                    </div>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeBulkCompletionModal()">
                        Ακύρωση
                    </button>
                    <button type="submit" class="btn btn-success">
                        <span class="icon">✓</span>
                        <span>Ολοκλήρωση Όλων</span>
                    </button>
                </div>
            </form>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeBulkCompletionModal() {
    const modal = document.getElementById('bulk-completion-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function handleBulkCompletion(event) {
    event.preventDefault();

    const modal = document.getElementById('bulk-completion-modal');
    const obligationIds = JSON.parse(modal.dataset.obligationIds);
    const form = event.target;
    const formData = new FormData(form);

    // Add obligation IDs to form data
    formData.append('obligation_ids', JSON.stringify(obligationIds));

    // Disable submit button
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalHTML = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="icon">⏳</span><span>Ολοκλήρωση...</span>';

    // Send bulk completion request
    fetch('/accounting/bulk-complete/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(\`✅ Ολοκληρώθηκαν \${data.completed_count} υποχρεώσεις επιτυχώς!\`, 'success');
            closeBulkCompletionModal();
            setTimeout(() => window.location.reload(), 1000);
        } else {
            throw new Error(data.error || 'Σφάλμα κατά τη μαζική ολοκλήρωση');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('❌ Σφάλμα: ' + error.message, 'error');
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
