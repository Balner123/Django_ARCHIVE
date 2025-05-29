from django import forms
from django.core.exceptions import ValidationError
from .models import Dokument, Fotografie, Soubor, Osoba, Druh, STOLETÍ_CHOICES, ArchivovanyObjekt

class FileUploadMixin(forms.Form):
    """Mixin pro přidání pole pro nahrání souboru a logiku pro jeho uložení."""
    uploaded_file = forms.FileField(
        label="Soubor k nahrání", 
        required=False, 
        help_text="Vyberte soubor pro archivaci."
    )

    def save_uploaded_file(self, instance):
        uploaded_file_data = self.cleaned_data.get('uploaded_file')
        if uploaded_file_data:
            soubor_obj = Soubor.objects.create(file=uploaded_file_data)
            instance.soubor = soubor_obj
        return instance

DATACE_CHOICES = [
    ('datum', 'Přesné datum'),
    ('rok', 'Rok'),
    ('stoleti', 'Století'),
]

class BaseArchivovanyObjektForm(FileUploadMixin, forms.ModelForm):
    """Základní formulář pro ArchivovanyObjekt s FileUploadMixin."""
    # Obecná pole, která chceme nahoře
    popis = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="Popis objektu", required=False)
    
    osoby_vyber = forms.ModelMultipleChoiceField(
        queryset=Osoba.objects.all().order_by('prijmeni', 'jmeno'),
        widget=forms.SelectMultiple(attrs={'size': 8}),
        label="Osoby spojené s objektem",
        help_text="Vyberte jednu nebo více osob (podržením Ctrl/Cmd). První vybraná osoba bude označena jako hlavní.",
        required=False
    )

    typ_datace = forms.ChoiceField(
        choices=DATACE_CHOICES,
        widget=forms.RadioSelect,
        label="Způsob zadání datace vzniku",
        required=True,
        initial='rok' 
    )
    datum_vzniku_presne = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control datace-field'}),
        required=False, label="Přesné datum vzniku"
    )
    rok_vzniku = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control datace-field'}),
        required=False, label="Rok vzniku"
    )
    stoleti_vzniku = forms.ChoiceField(
        choices=[('', '---------')] + STOLETÍ_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select datace-field'}),
        required=False, label="Století vzniku"
    )

    class Meta:
        model = ArchivovanyObjekt 
        # Explicitně definujeme pořadí, 'uploaded_file' je z Mixinu
        fields = ['popis', 'typ_datace', 'datum_vzniku_presne', 'rok_vzniku', 'stoleti_vzniku', 'osoby_vyber', 'uploaded_file'] 
        # 'popis' je zde znovu, aby byl první, i když je definován i výše. Django formy to zvládnou.
        # CrispyForms by měly respektovat pořadí fields.
        widgets = { # widget pro popis je již definován výše
            # Zde mohou být další widgety, pokud jsou potřeba pro pole z modelu
        }
        # help_texts mohou být zde, pokud nejsou u polí definovaných výše
        help_texts = {
            'popis': 'Zadejte popis objektu.', # Příklad, pokud by nebyl u pole
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nastavení počátečních hodnot pro dataci, pokud instance existuje
        if self.instance and self.instance.pk:
            if self.instance.datum_vzniku_presne:
                self.fields['typ_datace'].initial = 'datum'
                self.fields['datum_vzniku_presne'].initial = self.instance.datum_vzniku_presne
            elif self.instance.rok_vzniku:
                self.fields['typ_datace'].initial = 'rok'
                self.fields['rok_vzniku'].initial = self.instance.rok_vzniku
            elif self.instance.stoleti_vzniku:
                self.fields['typ_datace'].initial = 'stoleti'
                self.fields['stoleti_vzniku'].initial = self.instance.stoleti_vzniku
            else: # Pokud nic není nastaveno, výchozí bude 'rok' a pole prázdná
                self.fields['typ_datace'].initial = 'rok'

            # Inicializace osoby_vyber (zůstává stejná)
            initial_osoby = list(self.instance.osoby.all())
            if self.instance.osoba and self.instance.osoba not in initial_osoby:
                initial_osoby.insert(0, self.instance.osoba) 
            unique_initial_osoby = []
            seen_pks = set()
            for osoba_obj in initial_osoby:
                if osoba_obj.pk not in seen_pks:
                    unique_initial_osoby.append(osoba_obj)
                    seen_pks.add(osoba_obj.pk)
            self.fields['osoby_vyber'].initial = unique_initial_osoby
        else:
            # Pro nový formulář, zajistíme, že jsou pole pro dataci správně nastavena dle initial 'typ_datace'
            # Toto bude hlavně řešeno JS, ale můžeme nastavit výchozí required=False pro všechna datace pole
            pass # JS se postará o zobrazení/skrytí a dynamické nastavení required

    def clean(self):
        cleaned_data = super().clean()
        typ_datace = cleaned_data.get('typ_datace')
        datum_presne = cleaned_data.get('datum_vzniku_presne')
        rok = cleaned_data.get('rok_vzniku')
        stoleti = cleaned_data.get('stoleti_vzniku')

        # Resetujeme datace pole, která nejsou relevantní pro vybraný typ_datace
        # a zajistíme, že relevantní pole je vyplněno.
        if typ_datace == 'datum':
            if not datum_presne:
                self.add_error('datum_vzniku_presne', "Toto pole je povinné, pokud je vybráno 'Přesné datum'.")
            cleaned_data['rok_vzniku'] = None
            cleaned_data['stoleti_vzniku'] = None
        elif typ_datace == 'rok':
            if not rok:
                self.add_error('rok_vzniku', "Toto pole je povinné, pokud je vybrán 'Rok'.")
            cleaned_data['datum_vzniku_presne'] = None
            cleaned_data['stoleti_vzniku'] = None
        elif typ_datace == 'stoleti':
            if not stoleti:
                self.add_error('stoleti_vzniku', "Toto pole je povinné, pokud je vybráno 'Století'.")
            cleaned_data['datum_vzniku_presne'] = None
            cleaned_data['rok_vzniku'] = None
        else: # Mělo by být vždy vybráno díky required=True na typ_datace
            self.add_error('typ_datace', "Musíte vybrat způsob zadání datace.")

        # Kontrola, zda je vyplněno alespoň něco (pokud je to požadavek)
        # Tato logika je nyní efektivně pokryta výše, protože typ_datace je povinný
        # a pro každý typ je pak povinné odpovídající pole.
        # if not datum_presne and not rok and not stoleti:
        #     raise ValidationError("Musíte vyplnit alespoň jednu formu datace.", code='no_datace')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance = self.save_uploaded_file(instance)

        # Uložení datace na základě vybraného typu
        typ_datace = self.cleaned_data.get('typ_datace')
        instance.datum_vzniku_presne = None
        instance.rok_vzniku = None
        instance.stoleti_vzniku = None

        if typ_datace == 'datum':
            instance.datum_vzniku_presne = self.cleaned_data.get('datum_vzniku_presne')
        elif typ_datace == 'rok':
            instance.rok_vzniku = self.cleaned_data.get('rok_vzniku')
        elif typ_datace == 'stoleti':
            instance.stoleti_vzniku = self.cleaned_data.get('stoleti_vzniku')

        # Uložení osoby a osob (zůstává stejné)
        selected_osoby = self.cleaned_data.get('osoby_vyber')
        if selected_osoby:
            instance.osoba = selected_osoby[0] 
        else:
            instance.osoba = None

        if commit:
            instance.save()
            if selected_osoby: 
                instance.osoby.set(selected_osoby)
            else:
                instance.osoby.clear()
        return instance

class DokumentForm(BaseArchivovanyObjektForm):
    class Meta(BaseArchivovanyObjektForm.Meta):
        model = Dokument
        fields = BaseArchivovanyObjektForm.Meta.fields + ['druh', 'jazyk']
        # Nyní musíme explicitně definovat celé pořadí pro DokumentForm
        fields = ['popis', 'druh', 'typ_datace', 'datum_vzniku_presne', 'rok_vzniku', 'stoleti_vzniku', 'jazyk', 'osoby_vyber', 'uploaded_file']
        help_texts = {**BaseArchivovanyObjektForm.Meta.help_texts, # help_texts z Base by měly být přepsány/doplněny specifickými
                        'popis': 'Zadejte popis dokumentu.', # Specifický help_text pro dokument
                        'druh': 'Vyberte druh dokumentu. Pokud požadovaný druh chybí, můžete <a href="#" id="add_new_druh_link" class="text-decoration-none">'
                                '<i class="fas fa-plus-circle me-1"></i>přidat nový druh</a>.',
                        'jazyk': 'Vyberte jazyk dokumentu.'
                       }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['druh'].queryset = Druh.objects.all().order_by('nazev')
        self.fields['druh'].required = False

class FotografieForm(BaseArchivovanyObjektForm):
    class Meta(BaseArchivovanyObjektForm.Meta):
        model = Fotografie
        fields = BaseArchivovanyObjektForm.Meta.fields + ['typ_fotografie', 'vyska', 'sirka']
        help_texts = {**BaseArchivovanyObjektForm.Meta.help_texts,
                        'typ_fotografie': 'Např. portrét, krajina, reportážní, skupinová.',
                        'vyska': 'Výška fotografie v cm.',
                        'sirka': 'Šířka fotografie v cm.'
                       }

class OsobaForm(forms.ModelForm):
    class Meta:
        model = Osoba
        fields = ['jmeno', 'prijmeni', 'narozeni', 'umrti', 'pohlavi']
        widgets = {
            'narozeni': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'umrti': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        help_texts = {
            'narozeni': 'Zadejte datum ve formátu RRRR-MM-DD.',
            'umrti': 'Zadejte datum ve formátu RRRR-MM-DD (pokud je známo).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['narozeni'].required = False
        self.fields['umrti'].required = False

class DruhForm(forms.ModelForm):
    class Meta:
        model = Druh
        fields = ['nazev', 'popis']
        widgets = {
            'popis': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'nazev': 'Zadejte jedinečný název pro nový druh dokumentu.',
            'popis': 'Volitelný popis pro tento druh dokumentu.'
        } 