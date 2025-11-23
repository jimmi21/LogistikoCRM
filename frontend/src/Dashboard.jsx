/**
 * ACCOUNTING DASHBOARD - PROFESSIONAL JAVASCRIPT
 * 
 * Author: ddiplas
 * Version: 2.0
 * Description: Modern, modular, and maintainable JavaScript for accounting dashboard
 * 
 * Dependencies: None (vanilla JavaScript)
 * Browser Support: ES2020+
 */

'use strict';

/* ============================================
   1. CONFIGURATION
   ============================================ */

const CONFIG = {
    api: {
        quickComplete: '/accounting/quick-complete/',
        bulkComplete: '/accounting/advanced-bulk-complete/',
        emailTemplates: '/accounting/api/email-templates/',
        sendBulkEmail: '/api/send-bulk-email/',
    },
    selectors: {
        filterForm: '#filter-form',
        filterStatus: '#filter-status',
        filterClient: '#filter-client',
        filterType: '#filter-type',
        filterDateFrom: '#filter-date-from',
        filterDateTo: '#filter-date-to',
        filterSort: '#filter-sort',
        filterSelect: '.filter-select',
        filtersBadge: '#active-filters-count',
        filtersDisplay: '#active-filters-display',
        filtersList: '#active-filters-list',
        selectAllHeader: '#select-all-header',
        oblCheckbox: '.obl-checkbox',
        bulkBar: '#bulk-actions-bar',
        selectedCount: '#selected-count',
        obligationsTable: '#obligations-table',
    },
    animation: {
        duration: 300,
        ease: 'ease-out',
    },
    modal: {
        zIndex: 9999,
    },
    notifications: {
        duration: 3000,
        position: 'top-right',
    },
};

/* ============================================
   2. UTILITY FUNCTIONS
   ============================================ */

/**
 * Safe DOM element retrieval
 */
const DOM = {
    query: (selector) => {
        const el = document.querySelector(selector);
        if (!el) {
            console.warn(`Element not found: ${selector}`);
        }
        return el;
    },

    queryAll: (selector) => {
        return document.querySelectorAll(selector);
    },

    create: (tag, className = '', innerHTML = '') => {
        const el = document.createElement(tag);
        if (className) el.className = className;
        if (innerHTML) el.innerHTML = innerHTML;
        return el;
    },

    show: (el) => {
        if (el) el.style.display = '';
    },

    hide: (el) => {
        if (el) el.style.display = 'none';
    },

    toggle: (el, show) => {
        if (el) el.style.display = show ? '' : 'none';
    },

    addClass: (el, className) => {
        if (el) el.classList.add(className);
    },

    removeClass: (el, className) => {
        if (el) el.classList.remove(className);
    },

    toggleClass: (el, className, force) => {
        if (el) el.classList.toggle(className, force);
    },

    hasClass: (el, className) => {
        return el ? el.classList.contains(className) : false;
    },
};

/**
 * Cookie utilities
 */
const Cookies = {
    get: (name) => {
        if (!document.cookie) return null;

        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === `${name}=`) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    },
};

/**
 * CSRF token helper
 */
const CSRF = {
    getToken: () => {
        return Cookies.get('csrftoken');
    },
};

/**
 * Logger with levels
 */
const Logger = {
    log: (message, data = null) => {
        console.log(`✅ ${message}`, data);
    },

    warn: (message, data = null) => {
        console.warn(`⚠️ ${message}`, data);
    },

    error: (message, data = null) => {
        console.error(`❌ ${message}`, data);
    },

    info: (message, data = null) => {
        console.info(`ℹ️ ${message}`, data);
    },
};

/* ============================================
   3. NOTIFICATION SYSTEM
   ============================================ */

class Notification {
    constructor(message, type = 'info') {
        this.message = message;
        this.type = type;
        this.element = null;
    }

    show() {
        const colors = {
            success: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            error: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
            warning: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            info: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
        };

        this.element = DOM.create('div', '', this.message);

        Object.assign(this.element.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: colors[this.type] || colors.info,
            color: 'white',
            padding: '15px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
            zIndex: CONFIG.modal.zIndex + 1,
            fontWeight: '600',
            animation: 'slideIn 0.3s ease',
            maxWidth: '400px',
        });

        document.body.appendChild(this.element);

        setTimeout(() => this.hide(), CONFIG.notifications.duration);
    }

    hide() {
        if (this.element) {
            this.element.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (this.element && this.element.parentNode) {
                    this.element.parentNode.removeChild(this.element);
                }
            }, 300);
        }
    }
}

const showNotification = (message, type = 'info') => {
    const notification = new Notification(message, type);
    notification.show();
};

window.showNotification = showNotification;

/* ============================================
   4. MODAL SYSTEM
   ============================================ */

class Modal {
    constructor(content) {
        this.content = content;
        this.element = null;
    }

    show() {
        this.element = DOM.create('div', 'modal-overlay');
        this.element.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: ${CONFIG.modal.zIndex};
            overflow-y: auto;
            padding: 20px;
        `;

        this.element.innerHTML = this.content;
        document.body.appendChild(this.element);

        this.element.addEventListener('click', (e) => {
            if (e.target === this.element) {
                this.close();
            }
        });

        return this;
    }

    close() {
        if (this.element) {
            this.element.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (this.element && this.element.parentNode) {
                    this.element.parentNode.removeChild(this.element);
                }
            }, 300);
        }
    }
}

const createModal = (content) => {
    const modal = new Modal(content);
    return modal.show();
};

window.createModal = createModal;

const closeModal = () => {
    const modal = DOM.query('.modal-overlay');
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            if (modal && modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }
};

window.closeModal = closeModal;

/* ============================================
   5. FILTER MANAGEMENT
   ============================================ */

class FilterManager {
    constructor() {
        this.activeFilters = {};
        this.init();
    }

    init() {
        this.loadFiltersFromURL();
        this.attachEventListeners();
        this.updateSelectVisibility();
        Logger.log('Filter Manager initialized');
    }

    loadFiltersFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        let activeCount = 0;
        const activeList = [];

        const filterMap = {
            status: CONFIG.selectors.filterStatus,
            client: CONFIG.selectors.filterClient,
            type: CONFIG.selectors.filterType,
            date_from: CONFIG.selectors.filterDateFrom,
            date_to: CONFIG.selectors.filterDateTo,
        };

        Object.entries(filterMap).forEach(([key, selector]) => {
            const value = urlParams.get(key);
            if (value) {
                const el = DOM.query(selector);
                if (el) {
                    el.value = value;
                    DOM.addClass(el, 'active-filter');
                    activeCount++;

                    if (el.tagName === 'SELECT') {
                        const option = el.querySelector(`option[value="${value}"]`);
                        if (option) {
                            activeList.push(option.textContent.trim());
                        }
                    } else {
                        activeList.push(`${key === 'date_from' ? 'Από' : 'Έως'}: ${value}`);
                    }
                }
            }
        });

        this.updateFilterDisplay(activeCount, activeList);
        this.activeFilters = Object.fromEntries(
            Object.entries(filterMap).map(([key, selector]) => [
                key,
                DOM.query(selector)?.value || '',
            ])
        );
    }

    updateFilterDisplay(count, list) {
        const badge = DOM.query(CONFIG.selectors.filtersBadge);
        const display = DOM.query(CONFIG.selectors.filtersDisplay);
        const listEl = DOM.query(CONFIG.selectors.filtersList);

        if (count > 0 && badge) {
            badge.textContent = count;
            DOM.show(badge);
        }

        if (count > 0 && display && listEl) {
            listEl.innerHTML = list
                .map(f => `<span style="background: #667eea; color: white; padding: 2px 8px; border-radius: 4px; margin-right: 5px; font-size: 12px;">${f}</span>`)
                .join('');
            DOM.show(display);
        }
    }

    attachEventListeners() {
        DOM.queryAll(CONFIG.selectors.filterSelect).forEach(el => {
            el.addEventListener('change', () => {
                if (el.value) {
                    DOM.addClass(el, 'active-filter');
                    DOM.addClass(el, 'has-value');
                } else {
                    DOM.removeClass(el, 'active-filter');
                    DOM.removeClass(el, 'has-value');
                }
                this.updateSelectVisibility();
            });
        });
    }

    updateSelectVisibility() {
        DOM.queryAll('select').forEach(select => {
            const value = select.value;

            if (value && value !== '') {
                DOM.addClass(select, 'has-value');
            } else {
                DOM.removeClass(select, 'has-value');
            }

            // Force browser repaint
            select.style.display = 'none';
            // eslint-disable-next-line no-unused-expressions
            select.offsetHeight;
            select.style.display = '';
        });
    }

    clear() {
        window.location.href = '/accounting/dashboard/';
    }
}

const filterManager = new FilterManager();

window.clearFilters = () => filterManager.clear();

/* ============================================
   6. BULK OPERATIONS
   ============================================ */

class BulkOperations {
    constructor() {
        this.selectedIds = [];
        this.init();
    }

    init() {
        this.attachCheckboxListeners();
        Logger.log('Bulk Operations initialized');
    }

    attachCheckboxListeners() {
        DOM.queryAll(CONFIG.selectors.oblCheckbox).forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateBulkBar();
            });
        });

        const headerCheckbox = DOM.query(CONFIG.selectors.selectAllHeader);
        if (headerCheckbox) {
            headerCheckbox.addEventListener('change', (e) => {
                this.toggleAllCheckboxes(e.target.checked);
            });
        }
    }

    updateBulkBar() {
        const checkboxes = DOM.queryAll(`${CONFIG.selectors.oblCheckbox}:checked`);
        const bulkBar = DOM.query(CONFIG.selectors.bulkBar);
        const count = checkboxes.length;

        DOM.show(bulkBar);
        DOM.toggle(bulkBar, count > 0);

        if (count > 0) {
            const countEl = DOM.query(CONFIG.selectors.selectedCount);
            if (countEl) countEl.textContent = count;
        }
    }

    toggleAllCheckboxes(checked) {
        DOM.queryAll(CONFIG.selectors.oblCheckbox).forEach(cb => {
            cb.checked = checked;
        });

        const headerCheckbox = DOM.query(CONFIG.selectors.selectAllHeader);
        if (headerCheckbox) {
            headerCheckbox.checked = checked;
        }

        this.updateBulkBar();
    }

    getSelectedIds() {
        return Array.from(DOM.queryAll(`${CONFIG.selectors.oblCheckbox}:checked`))
            .map(cb => parseInt(cb.value));
    }

    selectAll() {
        this.toggleAllCheckboxes(true);
    }

    deselectAll() {
        this.toggleAllCheckboxes(false);
    }
}

const bulkOps = new BulkOperations();

window.selectAll = () => bulkOps.selectAll();
window.deselectAll = () => bulkOps.deselectAll();
window.toggleAllCheckboxes = (source) => bulkOps.toggleAllCheckboxes(source.checked);
window.updateBulkBar = () => bulkOps.updateBulkBar();
window.getSelectedIds = () => bulkOps.getSelectedIds();

/* ============================================
   7. TABLE NAVIGATION
   ============================================ */

const navigateToObligation = (id) => {
    window.location.href = `/el/456-admin/accounting/monthlyobligation/${id}/change/`;
};

window.navigateToObligation = navigateToObligation;

const toggleTableCompactView = () => {
    const table = DOM.query(CONFIG.selectors.obligationsTable);
    if (table) {
        DOM.toggleClass(table, 'compact');
    }
};

window.toggleTableCompactView = toggleTableCompactView;

const toggleTableFullscreen = () => {
    const container = DOM.query('.table-container');
    if (container) {
        DOM.toggleClass(container, 'fullscreen');
    }
};

window.toggleTableFullscreen = toggleTableFullscreen;

const closeBulkBar = () => {
    const bulkBar = DOM.query(CONFIG.selectors.bulkBar);
    DOM.hide(bulkBar);
};

window.closeBulkBar = closeBulkBar;

/* ============================================
   8. QUICK COMPLETE
   ============================================ */

class QuickComplete {
    constructor(obligationId) {
        this.obligationId = obligationId;
    }

    show() {
        const content = `
            <div class="modal-content" style="background: white; padding: 30px; border-radius: 12px; max-width: 500px; width: 90%; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">
                <h3 style="margin: 0 0 20px 0; color: #333; display: flex; align-items: center; gap: 10px;">
                    <span style="color: #10b981;">✓</span> Ολοκλήρωση Υποχρέωσης
                </h3>
                <form id="complete-form">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">
                            ⏱️ Ώρες Εργασίας:
                        </label>
                        <input type="number" id="time-spent" name="time_spent" step="0.5" min="0" value="0"
                               placeholder="π.χ. 2.5"
                               style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px;">
                    </div>
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">
                            📝 Σημειώσεις:
                        </label>
                        <textarea id="notes" name="notes" rows="3"
                                  style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px; resize: vertical;"
                                  placeholder="π.χ. Υποβλήθηκε ηλεκτρονικά στο myDATA..."></textarea>
                    </div>
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">
                            📎 Επισύναψη Αρχείου:
                        </label>
                        <input type="file" id="attachment" name="attachment"
                               accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.zip"
                               style="width: 100%; padding: 10px; border: 2px dashed #e0e0e0; border-radius: 8px; font-size: 14px; cursor: pointer; background: #f9fafb;">
                        <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">
                            Υποστηριζόμενα: PDF, Word, Excel, Εικόνες, ZIP (max 10MB)
                        </div>
                    </div>
                </form>
                <div style="display: flex; gap: 10px; justify-content: flex-end;">
                    <button onclick="closeModal()"
                            style="background: #f5f5f5; color: #666; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                        Ακύρωση
                    </button>
                    <button onclick="submitComplete(${this.obligationId})"
                            style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                        ✓ Ολοκλήρωση
                    </button>
                </div>
            </div>
        `;

        createModal(content);

        setTimeout(() => {
            const input = DOM.query('#time-spent');
            if (input) input.focus();
        }, 100);
    }

    async submit() {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '⏳ Αποθήκευση...';
        btn.disabled = true;

        try {
            const formData = new FormData();
            formData.append('time_spent', DOM.query('#time-spent')?.value || '0');
            formData.append('notes', DOM.query('#notes')?.value || '');

            const fileInput = DOM.query('#attachment');
            if (fileInput && fileInput.files.length > 0) {
                formData.append('attachment', fileInput.files[0]);
            }

            const response = await fetch(`${CONFIG.api.quickComplete}${this.obligationId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': CSRF.getToken() },
                body: formData,
            });

            const data = await response.json();

            if (data.success) {
                closeModal();
                showNotification(`✅ ${data.message}`, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification(`❌ ${data.message}`, 'error');
                btn.textContent = originalText;
                btn.disabled = false;
            }
        } catch (error) {
            Logger.error('Quick complete error', error);
            showNotification(`❌ Σφάλμα: ${error.message}`, 'error');
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }
}

window.quickComplete = (obligationId) => {
    const qc = new QuickComplete(obligationId);
    qc.show();
};

window.submitComplete = function (obligationId) {
    const qc = new QuickComplete(obligationId);
    qc.submit();
};

/* ============================================
   9. ADVANCED BULK COMPLETE
   ============================================ */

class AdvancedBulkComplete {
    constructor() {
        this.obligationsByClient = {};
    }

    show() {
        const selectedCheckboxes = DOM.queryAll(`${CONFIG.selectors.oblCheckbox}:checked`);

        if (selectedCheckboxes.length === 0) {
            showNotification('⚠️ Επιλέξτε τουλάχιστον μία υποχρέωση!', 'warning');
            return;
        }

        this.groupByClient(selectedCheckboxes);
        this.renderModal();
    }

    groupByClient(checkboxes) {
        this.obligationsByClient = {};

        checkboxes.forEach(cb => {
            const afm = cb.dataset.clientAfm;
            const clientName = cb.dataset.clientName;
            const obligationType = cb.dataset.obligationType;
            const deadline = cb.dataset.deadline;
            const id = cb.value;

            if (!this.obligationsByClient[afm]) {
                this.obligationsByClient[afm] = {
                    name: clientName,
                    afm: afm,
                    obligations: [],
                };
            }

            this.obligationsByClient[afm].obligations.push({
                id: id,
                type: obligationType,
                deadline: deadline,
            });
        });
    }

    renderModal() {
        let clientGroupsHtml = '';
        let groupColorIndex = 1;

        Object.values(this.obligationsByClient).forEach((client, clientIndex) => {
            clientGroupsHtml += this.renderClientGroup(client, clientIndex, groupColorIndex);
            groupColorIndex = groupColorIndex >= 5 ? 1 : groupColorIndex + 1;
        });

        const content = `
            <div class="modal-content" style="background: white; padding: 30px; border-radius: 12px; max-width: 900px; width: 90%; max-height: 80vh; overflow-y: auto; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
                <h3 style="margin: 0 0 20px 0; color: #333; font-size: 22px;">
                    🎯 Έξυπνη Ολοκλήρωση Υποχρεώσεων
                </h3>

                <div style="background: #f0f9ff; border: 1px solid #3b82f6; padding: 12px; border-radius: 6px; margin-bottom: 20px;">
                    <div style="font-size: 13px; color: #1e40af; line-height: 1.6;">
                        <strong>💡 Οδηγίες:</strong><br>
                        • Ομαδοποιήστε υποχρεώσεις που θα κλείσουν με το ίδιο αρχείο<br>
                        • Ανεβάστε διαφορετικά αρχεία για κάθε ομάδα<br>
                        • Οι μη ομαδοποιημένες υποχρεώσεις θα λάβουν ξεχωριστό αρχείο
                    </div>
                </div>

                <div id="clients-container">
                    ${clientGroupsHtml}
                </div>

                <div style="margin-top: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">
                        📝 Γενικές Σημειώσεις (προαιρετικό):
                    </label>
                    <textarea id="bulk-notes" rows="3"
                              style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px; resize: vertical;"
                              placeholder="π.χ. Όλα υποβλήθηκαν στο myDATA..."></textarea>
                </div>

                <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
                    <button onclick="closeModal()"
                            style="background: #f5f5f5; color: #666; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                        Ακύρωση
                    </button>
                    <button onclick="submitAdvancedBulkComplete()"
                            style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 10px 25px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                        ✓ Ολοκλήρωση Όλων
                    </button>
                </div>
            </div>
        `;

        createModal(content);
    }

    renderClientGroup(client, clientIndex, groupColorIndex) {
        return `
            <div class="client-group" data-client-afm="${client.afm}">
                <div class="client-group-header">
                    <div>
                        <strong style="font-size: 16px; color: #1f2937;">${client.name}</strong>
                        <span style="color: #6c757d; margin-left: 10px;">ΑΦΜ: ${client.afm}</span>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button type="button" onclick="selectAllClientObligations('${client.afm}')"
                                style="background: #667eea; color: white; border: none; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer;">
                            Επιλογή Όλων
                        </button>
                        <button type="button" onclick="groupClientObligations('${client.afm}', ${groupColorIndex})"
                                style="background: #10b981; color: white; border: none; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer;">
                            Ομαδοποίηση
                        </button>
                    </div>
                </div>

                <div class="obligations-list" style="margin: 10px 0;">
                    ${client.obligations.map((obl) => `
                        <div class="obligation-item" data-obligation-id="${obl.id}" data-group="0">
                            <input type="checkbox" id="adv-obl-${obl.id}" checked
                                   style="width: 18px; height: 18px; margin-right: 10px;">
                            <label for="adv-obl-${obl.id}" style="flex: 1; cursor: pointer;">
                                <strong>${obl.type}</strong>
                                <span style="color: #6c757d; margin-left: 10px;">${obl.deadline}</span>
                                <span class="group-indicator group-color-0" style="display: none;"></span>
                            </label>
                        </div>
                    `).join('')}
                </div>

                <div class="file-groups" style="margin-top: 15px;">
                    <div class="file-group" data-group="0">
                        <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #555; font-size: 13px;">
                            📎 Αρχεία για μεμονωμένες υποχρεώσεις:
                        </label>
                        <div class="file-upload-zone" onclick="triggerFileInput('client-${clientIndex}-individual')">
                            <input type="file" id="file-client-${clientIndex}-individual"
                                   data-client-afm="${client.afm}" data-group="0"
                                   multiple accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.zip"
                                   style="display: none;" onchange="handleFileSelect(this)">
                            <div>📤 Κλικ για upload αρχείων</div>
                            <div style="font-size: 11px; color: #6c757d; margin-top: 5px;">
                                Κάθε υποχρέωση θα λάβει ξεχωριστό αρχείο
                            </div>
                            <div class="file-list" style="margin-top: 10px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async submit() {
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '⏳ Επεξεργασία...';
        button.disabled = true;

        try {
            const formData = new FormData();
            const completionData = [];

            Logger.log('Collecting bulk complete data...');

            DOM.queryAll('.client-group').forEach(clientGroup => {
                const afm = clientGroup.dataset.clientAfm;
                const groups = {};

                clientGroup.querySelectorAll('.obligation-item').forEach(item => {
                    const checkbox = item.querySelector('input[type="checkbox"]');
                    if (checkbox && checkbox.checked) {
                        const oblId = item.dataset.obligationId;
                        const groupNum = item.dataset.group || '0';

                        if (!groups[groupNum]) {
                            groups[groupNum] = [];
                        }
                        groups[groupNum].push(oblId);
                    }
                });

                Object.keys(groups).forEach(groupNum => {
                    let fileInput;
                    if (groupNum === '0') {
                        fileInput = clientGroup.querySelector('input[type="file"][data-group="0"]');
                    } else {
                        fileInput = clientGroup.querySelector(`input[type="file"][data-group="${groupNum}"]`);
                    }

                    if (fileInput && fileInput.files.length > 0) {
                        Array.from(fileInput.files).forEach((file) => {
                            const key = `file_${afm}_${groupNum}`;
                            formData.append(key, file);
                        });
                    }

                    completionData.push({
                        client_afm: afm,
                        group: groupNum,
                        obligations: groups[groupNum],
                    });
                });
            });

            formData.append('completion_data', JSON.stringify(completionData));
            formData.append('notes', DOM.query('#bulk-notes')?.value || '');
            formData.append('csrfmiddlewaretoken', CSRF.getToken());

            const response = await fetch(CONFIG.api.bulkComplete, {
                method: 'POST',
                headers: { 'X-CSRFToken': CSRF.getToken() },
                body: formData,
            });

            const data = await response.json();

            if (data.success) {
                closeModal();
                showNotification(`✅ ${data.completed_count} υποχρεώσεις ολοκληρώθηκαν!`, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification(`❌ ${data.message}`, 'error');
                button.innerHTML = originalText;
                button.disabled = false;
            }
        } catch (error) {
            Logger.error('Advanced bulk complete error', error);
            showNotification(`❌ Σφάλμα: ${error.message}`, 'error');
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }
}

const advancedBulk = new AdvancedBulkComplete();

window.showAdvancedBulkComplete = () => advancedBulk.show();
window.submitAdvancedBulkComplete = function () {
    advancedBulk.submit();
};

window.selectAllClientObligations = (afm) => {
    const group = DOM.query(`.client-group[data-client-afm="${afm}"]`);
    if (group) {
        group.querySelectorAll('.obligation-item input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
        });
    }
};

window.groupClientObligations = (afm, groupNumber) => {
    const group = DOM.query(`.client-group[data-client-afm="${afm}"]`);
    if (!group) return;

    const checkedItems = group.querySelectorAll('.obligation-item input[type="checkbox"]:checked');

    if (checkedItems.length === 0) {
        showNotification('Επιλέξτε υποχρεώσεις για ομαδοποίηση', 'warning');
        return;
    }

    checkedItems.forEach(cb => {
        const item = cb.closest('.obligation-item');
        const currentGroup = item.dataset.group;
        const newGroup = currentGroup == groupNumber ? '0' : groupNumber;

        item.dataset.group = newGroup;

        const indicator = item.querySelector('.group-indicator');
        if (newGroup == '0') {
            indicator.style.display = 'none';
        } else {
            indicator.style.display = 'inline-block';
            indicator.className = `group-indicator group-color-${newGroup}`;
            indicator.textContent = `Ομάδα ${newGroup}`;
        }
    });

    updateFileUploadZones(afm);
};

window.updateFileUploadZones = (afm) => {
    const clientGroup = DOM.query(`.client-group[data-client-afm="${afm}"]`);
    if (!clientGroup) return;

    const fileGroupsContainer = clientGroup.querySelector('.file-groups');
    const existingGroups = new Set(['0']);

    clientGroup.querySelectorAll('.obligation-item').forEach(item => {
        const group = item.dataset.group || '0';
        if (group !== '0') {
            existingGroups.add(group);
        }
    });

    let html = '';
    Array.from(existingGroups).sort().forEach(groupNum => {
        const groupObligations = clientGroup.querySelectorAll(`.obligation-item[data-group="${groupNum}"]`);
        const isIndividual = groupNum === '0';

        if (groupObligations.length > 0 || groupNum === '0') {
            const inputId = `file-${afm}-group-${groupNum}`;

            html += `
                <div class="file-group" data-group="${groupNum}" style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #555; font-size: 13px;">
                        📎 ${isIndividual ? 'Αρχεία για μεμονωμένες υποχρεώσεις' : `Αρχείο για Ομάδα ${groupNum}`}:
                        <span class="group-color-${groupNum}" style="padding: 2px 8px; border-radius: 12px; font-size: 11px;">
                            ${groupObligations.length} υποχρεώσεις
                        </span>
                    </label>
                    <div class="file-upload-zone" onclick="document.getElementById('${inputId}').click()">
                        <input type="file"
                               id="${inputId}"
                               data-client-afm="${afm}"
                               data-group="${groupNum}"
                               ${isIndividual ? 'multiple' : ''}
                               accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.zip"
                               style="display: none;"
                               onchange="handleFileSelect(this)">
                        <div>📤 Κλικ για upload ${isIndividual ? 'αρχείων' : 'αρχείου'}</div>
                        <div style="font-size: 11px; color: #6c757d; margin-top: 5px;">
                            ${isIndividual ? 'Κάθε υποχρέωση θα λάβει ξεχωριστό αρχείο' : 'Όλες οι υποχρεώσεις της ομάδας θα λάβουν αυτό το αρχείο'}
                        </div>
                        <div class="file-list" style="margin-top: 10px;"></div>
                    </div>
                </div>
            `;
        }
    });

    fileGroupsContainer.innerHTML = html;
};

window.triggerFileInput = (inputId) => {
    const el = DOM.query(`#file-${inputId}`);
    if (el) el.click();
};

window.handleFileSelect = (input) => {
    const zone = input.closest('.file-upload-zone');
    if (!zone) return;

    const fileList = zone.querySelector('.file-list');
    const files = Array.from(input.files);

    if (files.length > 0) {
        zone.classList.add('has-file');
        fileList.innerHTML = files.map(f => `
            <div style="display: flex; align-items: center; gap: 5px; margin-top: 5px;">
                <span style="color: #10b981;">✓</span>
                <span style="font-size: 12px; color: #374151;">${f.name}</span>
                <span style="font-size: 11px; color: #6c757d;">(${(f.size / 1024).toFixed(1)} KB)</span>
            </div>
        `).join('');
    }
};

/* ============================================
   10. BULK ACTIONS
   ============================================ */

window.bulkEmail = () => {
    const ids = bulkOps.getSelectedIds();
    if (ids.length === 0) {
        showNotification('⚠️ Επιλέξτε τουλάχιστον μία υποχρέωση!', 'warning');
        return;
    }
    showEmailModal(ids);
};

window.bulkExport = () => {
    const ids = bulkOps.getSelectedIds();
    if (ids.length === 0) {
        showNotification('⚠️ Επιλέξτε τουλάχιστον μία υποχρέωση!', 'warning');
        return;
    }
    const params = new URLSearchParams({ ids: ids.join(',') });
    window.location.href = `/accounting/export-excel/?${params}`;
};

window.bulkDelete = () => {
    const ids = bulkOps.getSelectedIds();
    if (ids.length === 0) {
        showNotification('⚠️ Επιλέξτε τουλάχιστον μία υποχρέωση!', 'warning');
        return;
    }

    if (confirm(`⚠️ Είστε σίγουροι ότι θέλετε να διαγράψετε ${ids.length} υποχρεώσεις;`)) {
        Logger.log('Deleting obligations:', ids);
        showNotification('🗑️ Η διαγραφή θα υλοποιηθεί σύντομα', 'info');
    }
};

window.bulkAction = (action) => {
    Logger.log(`Bulk action: ${action}`);
    showNotification('Η ενέργεια θα υλοποιηθεί σύντομα', 'info');
};

/* ============================================
   11. EMAIL FUNCTIONS
   ============================================ */

window.showEmailModal = (obligationIds) => {
    const content = `
        <div class="modal-content" style="background: white; padding: 30px; border-radius: 16px; max-width: 700px; width: 90%; max-height: 80vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid #e0e0e0;">
                <h2 style="margin: 0; color: #333; font-size: 24px;">📧 Αποστολή Email</h2>
                <button onclick="closeModal()" style="background: none; border: none; font-size: 28px; color: #999; cursor: pointer; line-height: 1;">×</button>
            </div>

            <div style="background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin-bottom: 20px; border-radius: 6px;">
                <strong style="color: #1e40af;">📊 Επιλεγμένες:</strong> ${obligationIds.length} υποχρεώσεις
            </div>

            <form id="email-form">
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">
                        📝 Πρότυπο Email
                    </label>
                    <select id="email-template"
                            style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px; background: white; color: #333;">
                        <option value="">-- Επιλέξτε Πρότυπο --</option>
                    </select>
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">
                        ⏰ Χρονοδιάγραμμα
                    </label>
                    <select id="email-timing"
                            style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px; background: white; color: #333;">
                        <option value="immediate">⚡ Άμεσα</option>
                        <option value="delay_1h">⏰ Μετά από 1 ώρα</option>
                        <option value="delay_24h">📅 Επόμενη ημέρα</option>
                        <option value="scheduled">🕐 Συγκεκριμένη ώρα</option>
                    </select>
                </div>

                <div id="scheduled-time-div" style="display: none; margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">
                        🕐 Ώρα Αποστολής
                    </label>
                    <input type="datetime-local" id="scheduled-time"
                           style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px;">
                </div>

                <div style="background: #f9fafb; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="font-size: 13px; color: #6b7280; line-height: 1.6;">
                        <strong>💡 Πληροφορίες:</strong><br>
                        • Τα emails θα σταλούν σε ${obligationIds.length} πελάτες<br>
                        • Τα συνημμένα αρχεία θα προστεθούν αυτόματα<br>
                        • Μπορείτε να παρακολουθήσετε την κατάσταση στο admin
                    </div>
                </div>
            </form>

            <div style="display: flex; gap: 10px; justify-content: flex-end; padding-top: 15px; border-top: 2px solid #e0e0e0;">
                <button onclick="closeModal()"
                        style="background: #f5f5f5; color: #666; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                    ✕ Ακύρωση
                </button>
                <button onclick="sendBulkEmail(${JSON.stringify(obligationIds)})"
                        style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 15px;">
                    ✉️ Αποστολή
                </button>
            </div>
        </div>
    `;

    createModal(content);

    loadEmailTemplates();

    const timingSelect = DOM.query('#email-timing');
    if (timingSelect) {
        timingSelect.addEventListener('change', function () {
            const scheduledDiv = DOM.query('#scheduled-time-div');
            if (scheduledDiv) {
                DOM.toggle(scheduledDiv, this.value === 'scheduled');
            }
        });
    }
};

window.loadEmailTemplates = async () => {
    try {
        const response = await fetch(CONFIG.api.emailTemplates);
        const templates = await response.json();

        const select = DOM.query('#email-template');
        if (!select) return;

        select.innerHTML = '<option value="">-- Επιλέξτε Πρότυπο --</option>';

        templates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = template.name;
            select.appendChild(option);
        });

        if (templates.length === 0) {
            showNotification('⚠️ Δεν βρέθηκαν πρότυπα email', 'warning');
        }
    } catch (error) {
        Logger.error('Failed to load email templates', error);
        showNotification('⚠️ Σφάλμα φόρτωσης προτύπων', 'error');
    }
};

window.sendBulkEmail = async function (obligationIds) {
    const templateId = DOM.query('#email-template')?.value;
    const timing = DOM.query('#email-timing')?.value;
    const scheduledTime = DOM.query('#scheduled-time')?.value;

    if (!templateId) {
        showNotification('⚠️ Επιλέξτε πρότυπο email!', 'warning');
        return;
    }

    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '⏳ Αποστολή...';
    button.disabled = true;

    try {
        const response = await fetch(CONFIG.api.sendBulkEmail, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF.getToken(),
            },
            body: JSON.stringify({
                obligation_ids: obligationIds,
                template_id: templateId,
                timing: timing,
                scheduled_time: scheduledTime,
            }),
        });

        const result = await response.json();

        if (result.success) {
            closeModal();
            showNotification(`🎉 ${result.emails_created} email(s) προγραμματίστηκαν επιτυχώς!`, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showNotification(`❌ Σφάλμα: ${result.error}`, 'error');
            button.innerHTML = originalText;
            button.disabled = false;
        }
    } catch (error) {
        Logger.error('Failed to send bulk email', error);
        showNotification(`❌ Σφάλμα δικτύου: ${error.message}`, 'error');
        button.innerHTML = originalText;
        button.disabled = false;
    }
};

/* ============================================
   12. INITIALIZATION
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {
    Logger.log('Dashboard initialized successfully');

    // Initialize filter presets
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

    const presetToday = DOM.query('#filter-preset-today');
    const presetWeek = DOM.query('#filter-preset-week');
    const presetMonth = DOM.query('#filter-preset-month');

    if (presetToday) {
        presetToday.addEventListener('click', () => {
            const fromInput = DOM.query(CONFIG.selectors.filterDateFrom);
            const toInput = DOM.query(CONFIG.selectors.filterDateTo);
            if (fromInput) fromInput.value = todayStr;
            if (toInput) toInput.value = todayStr;
            DOM.query(CONFIG.selectors.filterForm)?.submit();
        });
    }

    if (presetWeek) {
        presetWeek.addEventListener('click', () => {
            const fromInput = DOM.query(CONFIG.selectors.filterDateFrom);
            const toInput = DOM.query(CONFIG.selectors.filterDateTo);
            if (fromInput) fromInput.value = weekAgo;
            if (toInput) toInput.value = todayStr;
            DOM.query(CONFIG.selectors.filterForm)?.submit();
        });
    }

    if (presetMonth) {
        presetMonth.addEventListener('click', () => {
            const fromInput = DOM.query(CONFIG.selectors.filterDateFrom);
            const toInput = DOM.query(CONFIG.selectors.filterDateTo);
            if (fromInput) fromInput.value = monthAgo;
            if (toInput) toInput.value = todayStr;
            DOM.query(CONFIG.selectors.filterForm)?.submit();
        });
    }
});

/* ============================================
   End of JavaScript
   ============================================ */