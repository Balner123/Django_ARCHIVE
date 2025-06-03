document.addEventListener('DOMContentLoaded', function() {
    const addDruhLink = document.getElementById('add_new_druh_link');
    if (addDruhLink) {
        let addDruhUrl = addDruhLink.dataset.addDruhUrl;
        if (addDruhUrl) {
            addDruhLink.href = addDruhUrl;
            addDruhLink.target = "_blank";
            
            addDruhLink.classList.remove('btn-outline-primary'); 
            addDruhLink.classList.add('btn', 'btn-link', 'text-decoration-none', 'mt-1');
           
            addDruhLink.innerHTML = '+ Přidat druh'; 
        }
    }

    const typDataceSelect = document.getElementById('id_typ_datace');
    const datumPresneField = document.getElementById('div_id_datum_vzniku_presne');
    const rokVznikuField = document.getElementById('div_id_rok_vzniku');
    const stoletiVznikuField = document.getElementById('div_id_stoleti_vzniku');

    function toggleDataceFields() {
        if (!typDataceSelect) {
            return; 
        }

        const selectedTypValue = typDataceSelect.value;
        
        if (datumPresneField) datumPresneField.classList.add('d-none');
        if (rokVznikuField) rokVznikuField.classList.add('d-none');
        if (stoletiVznikuField) stoletiVznikuField.classList.add('d-none');

        if (selectedTypValue === 'datum' && datumPresneField) {
            datumPresneField.classList.remove('d-none');
        } else if (selectedTypValue === 'rok' && rokVznikuField) {
            rokVznikuField.classList.remove('d-none');
        } else if (selectedTypValue === 'stoleti' && stoletiVznikuField) {
            stoletiVznikuField.classList.remove('d-none');
        }
    }

    if (typDataceSelect) { 
        typDataceSelect.addEventListener('change', toggleDataceFields);
        toggleDataceFields(); 
    } else {
        if (!datumPresneField) console.warn('Crispy form field wrapper div_id_datum_vzniku_presne not found.');
        if (!rokVznikuField) console.warn('Crispy form field wrapper div_id_rok_vzniku not found.');
        if (!stoletiVznikuField) console.warn('Crispy form field wrapper div_id_stoleti_vzniku not found.');
    }

    const osobyVyberDiv = document.getElementById('div_id_osoby_vyber');
    if (osobyVyberDiv) {
        const addOsobaButton = document.createElement('a');
        const addOsobaUrl = osobyVyberDiv.dataset.addOsobaUrl;

        if (addOsobaUrl) {
            addOsobaButton.href = addOsobaUrl;
            addOsobaButton.target = "_blank";
            addOsobaButton.classList.add('btn', 'btn-link', 'text-decoration-none', 'dynamic-add-button');
            addOsobaButton.innerHTML = '+ Přidat novou osobu'; 
            
            const osobyVyberSelect = document.getElementById('id_osoby_vyber');
            if (osobyVyberSelect && osobyVyberSelect.parentNode) {
                osobyVyberSelect.parentNode.insertBefore(addOsobaButton, osobyVyberSelect.nextSibling);
            } else {
                osobyVyberDiv.parentNode.insertBefore(addOsobaButton, osobyVyberDiv.nextSibling);
            }

        }
    }
}); 