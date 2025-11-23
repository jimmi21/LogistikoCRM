document.addEventListener('DOMContentLoaded', function() {
    // Βρες τα fields
    const clientField = document.querySelector('#id_client');
    const typeField = document.querySelector('#id_obligation_type');
    const yearField = document.querySelector('#id_year');
    const monthField = document.querySelector('#id_month');
    
    if (!clientField || !typeField || !yearField || !monthField) {
        return;  // Δεν είμαστε στη σωστή σελίδα
    }
    
    // Function για έλεγχο
    function checkDuplicate() {
        if (!clientField.value || !typeField.value || 
            !yearField.value || !monthField.value) {
            hideWarning();
            return;
        }
        
        // AJAX call
        fetch(`/accounting/check-obligation/?client=${clientField.value}&type=${typeField.value}&year=${yearField.value}&month=${monthField.value}`)
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    showWarning();
                } else {
                    hideWarning();
                }
            });
    }
    
    // Show warning
    function showWarning() {
        let warning = document.getElementById('duplicate-warning');
        if (!warning) {
            warning = document.createElement('div');
            warning.id = 'duplicate-warning';
            warning.style.cssText = `
                background: #fff3cd; 
                border: 1px solid #ffc107; 
                color: #856404; 
                padding: 12px; 
                margin: 10px 0; 
                border-radius: 4px;
                font-weight: bold;
            `;
            warning.innerHTML = '⚠️ ΠΡΟΣΟΧΗ: Υπάρχει ήδη αυτή η υποχρέωση!';
            
            // Βάλε το warning πριν τα buttons
            const submitRow = document.querySelector('.submit-row');
            if (submitRow) {
                submitRow.parentNode.insertBefore(warning, submitRow);
            }
        }
    }
    
    // Hide warning
    function hideWarning() {
        const warning = document.getElementById('duplicate-warning');
        if (warning) {
            warning.remove();
        }
    }
    
    // Add listeners
    clientField.addEventListener('change', checkDuplicate);
    typeField.addEventListener('change', checkDuplicate);
    yearField.addEventListener('change', checkDuplicate);
    monthField.addEventListener('change', checkDuplicate);
});