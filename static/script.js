document.addEventListener('DOMContentLoaded', () => {
    const algorithmRadios = document.querySelectorAll('input[name="algorithm"]');
    const quantumField = document.getElementById('quantumField');

    // Toggle quantum field based on algorithm selection
    algorithmRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            document.body.className = radio.value;
            quantumField.style.display = radio.value === 'rr' ? 'block' : 'none';
            
            // Toggle required attribute
            const quantumInput = quantumField.querySelector('input');
            if (quantumInput) {
                quantumInput.toggleAttribute('required', radio.value === 'rr');
            }
        });
    });

    // Form validation
    document.querySelector('form').addEventListener('submit', (e) => {
        if (e.submitter && e.submitter.name === 'add_process') {
            const arrivalInput = document.querySelector('input[name="arrival"]');
            const burstInput = document.querySelector('input[name="burst"]');
            
            if (!burstInput.value || parseInt(burstInput.value) < 1) {
                e.preventDefault();
                burstInput.classList.add('error');
                alert('Burst time must be at least 1');
                return;
            }
            
            if (arrivalInput.value && parseInt(arrivalInput.value) < 0) {
                e.preventDefault();
                arrivalInput.classList.add('error');
                alert('Arrival time cannot be negative');
                return;
            }
        }
        
        if (e.submitter && e.submitter.name === 'run_algorithm') {
            const algorithm = document.querySelector('input[name="algorithm"]:checked').value;
            if (algorithm === 'rr') {
                const quantumInput = document.querySelector('input[name="quantum"]');
                if (!quantumInput.value || parseInt(quantumInput.value) < 1) {
                    e.preventDefault();
                    quantumInput.classList.add('error');
                    alert('Quantum must be at least 1');
                    return;
                }
            }
        }
    });

    // Clear error state on input
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', () => {
            input.classList.remove('error');
        });
    });
});
