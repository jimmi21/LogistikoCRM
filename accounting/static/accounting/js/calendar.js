/**
 * Calendar View JavaScript
 * FullCalendar integration for D.P. Economy obligations
 * Greek language, responsive design
 */

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var modal = document.getElementById('event-modal');
    var currentEvent = null;

    // Initialize FullCalendar
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'el',

        // Header toolbar with navigation and view buttons
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listMonth'
        },

        // Greek button text
        buttonText: {
            today: 'Σήμερα',
            month: 'Μήνας',
            week: 'Εβδομάδα',
            day: 'Ημέρα',
            list: 'Λίστα'
        },

        // Week starts on Monday (Greek standard)
        firstDay: 1,

        // Show week numbers
        weekNumbers: true,
        weekText: 'Εβδ.',

        // Highlight current day
        nowIndicator: true,

        // Limit events shown per day, with "more" link
        dayMaxEvents: 3,
        moreLinkText: function(num) {
            return '+' + num + ' ακόμα';
        },

        // Navigation text
        navLinks: true,

        // Event source - API endpoint
        events: function(info, successCallback, failureCallback) {
            var params = new URLSearchParams({
                start: info.startStr,
                end: info.endStr,
                client: document.getElementById('filter-client').value || '',
                type: document.getElementById('filter-type').value || '',
                status: document.getElementById('filter-status').value || ''
            });

            fetch('/accounting/api/calendar-events/?' + params.toString())
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(function(data) {
                    successCallback(data.events);
                })
                .catch(function(error) {
                    console.error('Error fetching events:', error);
                    failureCallback(error);
                });
        },

        // Add CSS class based on status
        eventClassNames: function(arg) {
            return ['event-' + (arg.event.extendedProps.status || 'pending')];
        },

        // Event click - show detail modal
        eventClick: function(info) {
            info.jsEvent.preventDefault();
            currentEvent = info.event;
            showEventModal(info.event);
        },

        // Date click - optional: could navigate to dashboard with date filter
        dateClick: function(info) {
            // Optional: Navigate to dashboard filtered by date
            // window.location.href = '/accounting/dashboard/?date_from=' + info.dateStr + '&date_to=' + info.dateStr;
        },

        // Event hover effects
        eventMouseEnter: function(info) {
            info.el.style.opacity = '0.8';
            info.el.style.cursor = 'pointer';
        },

        eventMouseLeave: function(info) {
            info.el.style.opacity = '1';
        },

        // Loading indicator
        loading: function(isLoading) {
            if (isLoading) {
                calendarEl.classList.add('loading');
            } else {
                calendarEl.classList.remove('loading');
            }
        },

        // Responsive height
        height: 'auto',

        // Fix header on scroll (for large calendars)
        stickyHeaderDates: true
    });

    calendar.render();

    // ============================================
    // FILTER HANDLERS
    // ============================================

    var filterClient = document.getElementById('filter-client');
    var filterType = document.getElementById('filter-type');
    var filterStatus = document.getElementById('filter-status');
    var clearFiltersBtn = document.getElementById('clear-filters');

    // Refetch events when filters change
    filterClient.addEventListener('change', function() {
        calendar.refetchEvents();
        updateClearButtonVisibility();
    });

    filterType.addEventListener('change', function() {
        calendar.refetchEvents();
        updateClearButtonVisibility();
    });

    filterStatus.addEventListener('change', function() {
        calendar.refetchEvents();
        updateClearButtonVisibility();
    });

    // Clear filters button
    clearFiltersBtn.addEventListener('click', function() {
        filterClient.value = '';
        filterType.value = '';
        filterStatus.value = '';
        calendar.refetchEvents();
        updateClearButtonVisibility();
    });

    // Show/hide clear button based on filter state
    function updateClearButtonVisibility() {
        var hasFilters = filterClient.value || filterType.value || filterStatus.value;
        clearFiltersBtn.style.display = hasFilters ? 'inline-flex' : 'none';
    }

    // Initial visibility
    updateClearButtonVisibility();

    // ============================================
    // MODAL FUNCTIONS
    // ============================================

    function showEventModal(event) {
        var props = event.extendedProps;

        // Set modal content
        document.getElementById('modal-title').textContent = event.title;
        document.getElementById('modal-client').textContent = props.client_name || '-';
        document.getElementById('modal-afm').textContent = props.client_afm || '-';
        document.getElementById('modal-type').textContent = props.obligation_type || '-';
        document.getElementById('modal-period').textContent = props.period || '-';
        document.getElementById('modal-deadline').textContent = formatDate(event.start);
        document.getElementById('modal-status').innerHTML = getStatusBadge(props.status);

        // Notes (show only if available)
        var notesRow = document.getElementById('modal-notes-row');
        var notesEl = document.getElementById('modal-notes');
        if (props.notes && props.notes.trim()) {
            notesEl.textContent = props.notes;
            notesRow.style.display = 'flex';
        } else {
            notesRow.style.display = 'none';
        }

        // Set edit button URL
        document.getElementById('modal-edit-btn').href = props.edit_url || '#';

        // Set client profile URL
        var clientBtn = document.getElementById('modal-client-btn');
        if (props.client_id) {
            clientBtn.href = '/accounting/client/' + props.client_id + '/';
            clientBtn.style.display = 'inline-flex';
        } else {
            clientBtn.style.display = 'none';
        }

        // Show/hide complete button based on status
        var completeBtn = document.getElementById('modal-complete-btn');
        if (props.status === 'pending' || props.status === 'overdue') {
            completeBtn.style.display = 'inline-flex';
            completeBtn.onclick = function() {
                completeObligation(event.id);
            };
        } else {
            completeBtn.style.display = 'none';
        }

        // Show modal
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function hideModal() {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        currentEvent = null;
    }

    // Format date in Greek locale
    function formatDate(date) {
        if (!date) return '-';
        return date.toLocaleDateString('el-GR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    // Get status badge HTML
    function getStatusBadge(status) {
        var badges = {
            'pending': '<span class="status-badge pending">🟡 Εκκρεμής</span>',
            'completed': '<span class="status-badge completed">✅ Ολοκληρωμένη</span>',
            'overdue': '<span class="status-badge overdue">🔴 Εκπρόθεσμη</span>'
        };
        return badges[status] || '<span class="status-badge">' + status + '</span>';
    }

    // Complete obligation - redirect to dashboard with complete action
    function completeObligation(obligationId) {
        // Redirect to dashboard with quick complete
        window.location.href = '/accounting/dashboard/?complete=' + obligationId;
    }

    // ============================================
    // MODAL EVENT LISTENERS
    // ============================================

    // Close button
    var closeBtn = document.querySelector('.modal-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', hideModal);
    }

    // Click outside modal to close
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            hideModal();
        }
    });

    // ESC key to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'flex') {
            hideModal();
        }
    });

    // ============================================
    // KEYBOARD SHORTCUTS
    // ============================================

    document.addEventListener('keydown', function(e) {
        // Don't trigger if user is typing in a form field
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        // Arrow keys for navigation
        if (e.key === 'ArrowLeft') {
            calendar.prev();
        } else if (e.key === 'ArrowRight') {
            calendar.next();
        } else if (e.key === 't' || e.key === 'T') {
            calendar.today();
        } else if (e.key === 'm' || e.key === 'M') {
            calendar.changeView('dayGridMonth');
        } else if (e.key === 'w' || e.key === 'W') {
            calendar.changeView('timeGridWeek');
        } else if (e.key === 'l' || e.key === 'L') {
            calendar.changeView('listMonth');
        }
    });

    // ============================================
    // RESPONSIVE HANDLING
    // ============================================

    function handleResize() {
        if (window.innerWidth < 768) {
            calendar.changeView('listMonth');
        }
    }

    // Check on load (but don't override user preference)
    // handleResize();

    // Optional: Auto-switch on resize
    // window.addEventListener('resize', debounce(handleResize, 250));
});

// Debounce utility function
function debounce(func, wait) {
    var timeout;
    return function executedFunction() {
        var context = this;
        var args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            func.apply(context, args);
        }, wait);
    };
}
