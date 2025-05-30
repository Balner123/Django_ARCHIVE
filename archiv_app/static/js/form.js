document.addEventListener('DOMContentLoaded', function() {
    const formInputs = document.querySelectorAll('.form-control, .form-select');
    formInputs.forEach(input => {
        input.classList.add('mb-3');
    });

    const formLabelsAndLegends = document.querySelectorAll('label, legend'); 
    formLabelsAndLegends.forEach(el => {
        if (el.tagName === 'LEGEND' || !el.closest('.form-check')) {
            el.style.fontWeight = '600';
            el.style.textTransform = 'uppercase';
            el.style.fontSize = '0.85rem';
        } else {
            el.style.fontWeight = 'normal';
            el.style.textTransform = 'none';
            el.style.fontSize = '1rem';
        }
    });
    
    const addDruhLink = document.getElementById('add_new_druh_link');
    if (addDruhLink) {
        let addDruhUrl = addDruhLink.dataset.addDruhUrl; // Změněno pro bezpečné předání URL
        if (addDruhUrl) {
            addDruhLink.href = addDruhUrl;
            addDruhLink.target = "_blank";
            
            addDruhLink.classList.remove('btn-outline-primary');
            addDruhLink.classList.add('btn', 'btn-link', 'text-decoration-none', 'mt-1');
            addDruhLink.style.fontSize = '0.875rem';
            addDruhLink.style.color = '#0d6efd';
            addDruhLink.style.opacity = '0.8';
            addDruhLink.style.transition = 'all 0.2s ease';
            addDruhLink.innerHTML = '+ Přidat druh';

            addDruhLink.addEventListener('mouseenter', () => {
                addDruhLink.style.opacity = '1';
                addDruhLink.style.transform = 'translateX(3px)';
            });
            addDruhLink.addEventListener('mouseleave', () => {
                addDruhLink.style.opacity = '0.8';
                addDruhLink.style.transform = 'translateX(0)';
            });
        }
    }

    // Úprava pro <select> element namísto radio buttonů
    const typDataceSelect = document.getElementById('id_typ_datace'); // Změněno na ID selectu
    const datumPresneField = document.getElementById('div_id_datum_vzniku_presne');
    const rokVznikuField = document.getElementById('div_id_rok_vzniku');
    const stoletiVznikuField = document.getElementById('div_id_stoleti_vzniku');

    function toggleDataceFields() {
        // Pokud hlavní select pro typ datace neexistuje, nic nedělat
        if (!typDataceSelect) {
            // Volitelně logovat, pokud jsou ostatní pole přítomna, ale hlavní select chybí
            // if (datumPresneField || rokVznikuField || stoletiVznikuField) {
            //     console.warn('Element id_typ_datace (select) not found, but other date fields exist.');
            // }
            return; 
        }

        const selectedTypValue = typDataceSelect.value; // Získání hodnoty ze selectu
        
        // Skrýt všechna pole na začátku
        if (datumPresneField) datumPresneField.style.display = 'none';
        if (rokVznikuField) rokVznikuField.style.display = 'none';
        if (stoletiVznikuField) stoletiVznikuField.style.display = 'none';

        // Zobrazit relevantní pole
        if (selectedTypValue === 'datum' && datumPresneField) {
            datumPresneField.style.display = 'block';
        } else if (selectedTypValue === 'rok' && rokVznikuField) {
            rokVznikuField.style.display = 'block';
        } else if (selectedTypValue === 'stoleti' && stoletiVznikuField) {
            stoletiVznikuField.style.display = 'block';
        }
    }

    // Navázání event listeneru a počáteční volání, pokud select existuje
    if (typDataceSelect) { 
        typDataceSelect.addEventListener('change', toggleDataceFields);
        toggleDataceFields(); // Zavoláme funkci při načtení stránky pro správné zobrazení
    } else {
        // Logování pro debug, pokud nejsou nalezeny hlavní elementy pro dataci
        // Toto by mělo být odstraněno/upraveno v produkci
        if (!datumPresneField) console.warn('Crispy form field wrapper div_id_datum_vzniku_presne not found.');
        if (!rokVznikuField) console.warn('Crispy form field wrapper div_id_rok_vzniku not found.');
        if (!stoletiVznikuField) console.warn('Crispy form field wrapper div_id_stoleti_vzniku not found.');
    }

    const osobyVyberDiv = document.getElementById('div_id_osoby_vyber');
    if (osobyVyberDiv) {
        const addOsobaButton = document.createElement('a');
        const addOsobaUrl = osobyVyberDiv.dataset.addOsobaUrl; // Změněno pro bezpečné předání URL

        if (addOsobaUrl) {
            addOsobaButton.href = addOsobaUrl;
            addOsobaButton.target = "_blank";
            addOsobaButton.classList.add('btn', 'btn-link', 'text-decoration-none');
            addOsobaButton.style.fontSize = '0.875rem';
            addOsobaButton.style.color = '#0d6efd';
            addOsobaButton.style.opacity = '0.8';
            addOsobaButton.style.transition = 'all 0.2s ease';
            addOsobaButton.innerHTML = '+ Přidat novou osobu';
            
            const osobyVyberSelect = document.getElementById('id_osoby_vyber');
            if (osobyVyberSelect && osobyVyberSelect.parentNode) {
                osobyVyberSelect.parentNode.insertBefore(addOsobaButton, osobyVyberSelect.nextSibling);
                addOsobaButton.style.marginTop = "0.5rem";
                addOsobaButton.style.display = "block";

                addOsobaButton.addEventListener('mouseenter', () => {
                    addOsobaButton.style.opacity = '1';
                    addOsobaButton.style.transform = 'translateX(3px)';
                });
                addOsobaButton.addEventListener('mouseleave', () => {
                    addOsobaButton.style.opacity = '0.8';
                    addOsobaButton.style.transform = 'translateX(0)';
                });
            } else {
                // Fallback, pokud select není nalezen přímo, vložíme za div_id_osoby_vyber
                osobyVyberDiv.parentNode.insertBefore(addOsobaButton, osobyVyberDiv.nextSibling);
            }
        }
    }
}); 