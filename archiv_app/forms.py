from django import forms
from .models import Dokument, Fotografie, Soubor, Osoba, Druh

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

class BaseArchivovanyObjektForm(FileUploadMixin, forms.ModelForm):
    """Základní formulář pro ArchivovanyObjekt s FileUploadMixin."""
    osoby_vyber = forms.ModelMultipleChoiceField(
        queryset=Osoba.objects.all().order_by('prijmeni', 'jmeno'),
        widget=forms.SelectMultiple(attrs={'size': 8}),
        label="Osoby spojené s objektem",
        help_text="Vyberte jednu nebo více osob (podržením Ctrl/Cmd). První vybraná osoba bude označena jako hlavní.",
        required=False
    )

    class Meta:
        abstract = True 
        fields = ['popis', 'stari', 'osoby_vyber', 'uploaded_file'] 
        widgets = {
            'popis': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'stari': 'Rok, ze kterého objekt pochází (např. 1950).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance = self.save_uploaded_file(instance)

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
        fields = ['popis', 'stari', 'osoby_vyber', 'uploaded_file', 'druh', 'jazyk']
        help_texts = {**BaseArchivovanyObjektForm.Meta.help_texts,
                        'druh': 'Vyberte druh dokumentu. Pokud požadovaný druh chybí, můžete <a href="#" id="add_new_druh_link" class="text-decoration-none">'
                                '<i class="fas fa-plus-circle me-1"></i>přidat nový druh</a>.',
                        'jazyk': 'Vyberte jazyk dokumentu.'
                       }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['druh'].queryset = Druh.objects.all().order_by('nazev')
        self.fields['druh'].required = False

        help_text_druh = (
            'Vyberte druh dokumentu. ' 
            'Pokud požadovaný druh chybí, můžete <a href="#" id="add_new_druh_link" class="text-decoration-none">'
            '<i class="fas fa-plus-circle me-1"></i>přidat nový druh</a>.'
        )
        self.fields['druh'].help_text = help_text_druh

class FotografieForm(BaseArchivovanyObjektForm):
    class Meta(BaseArchivovanyObjektForm.Meta):
        model = Fotografie
        fields = ['popis', 'stari', 'osoby_vyber', 'uploaded_file', 'typ_fotografie', 'vyska', 'sirka']
        help_texts = {**BaseArchivovanyObjektForm.Meta.help_texts,
                        'typ_fotografie': 'Např. portrét, krajina, reportážní, skupinová.',
                        'vyska': 'Výška fotografie v cm.',
                        'sirka': 'Šířka fotografie v cm.'
                       }

    def save(self, commit=True):
        return super().save(commit=commit)

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