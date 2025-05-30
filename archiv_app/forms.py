from django import forms
from django.core.exceptions import ValidationError
from .models import Dokument, Fotografie, Soubor, Osoba, Druh, STOLETÍ_CHOICES, ArchivovanyObjekt

TEXTAREA_ROWS = 3
OSOBA_SELECT_SIZE = 8
MIN_YEAR = 1000
MAX_YEAR = 2100

# Společné widget atributy
DATE_WIDGET_ATTRS = {'type': 'date', 'class': 'form-control'}
TEXTAREA_WIDGET_ATTRS = {'rows': TEXTAREA_ROWS, 'class': 'form-control'}
NUMBER_WIDGET_ATTRS = {'class': 'form-control', 'min': MIN_YEAR, 'max': MAX_YEAR}

class FileUploadMixin(forms.Form):
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
    popis = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), 
        label="Popis objektu", 
        required=False
    )
    
    osoby_vyber = forms.ModelMultipleChoiceField(
        queryset=Osoba.objects.all().order_by('prijmeni', 'jmeno'),
        widget=forms.SelectMultiple(attrs={'size': 8}),
        label="Osoby spojené s objektem",
        help_text="Vyberte jednu nebo více osob (podržením Ctrl/Cmd). První vybraná osoba bude označena jako hlavní.",
        required=False
    )

    # Zjednodušená datační pole - bez složitého typ_datace
    datum_vzniku_presne = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False, 
        label="Přesné datum vzniku"
    )
    rok_vzniku = forms.IntegerField(
        widget=forms.NumberInput(attrs={'min': 1000, 'max': 2100}),
        required=False, 
        label="Rok vzniku"
    )
    stoleti_vzniku = forms.ChoiceField(
        choices=[('', '---------')] + STOLETÍ_CHOICES,
        required=False, 
        label="Století vzniku"
    )

    class Meta:
        model = ArchivovanyObjekt 
        fields = ['popis', 'datum_vzniku_presne', 'rok_vzniku', 'stoleti_vzniku', 'osoby_vyber', 'uploaded_file']

    def clean(self):
        cleaned_data = super().clean()
        datum_presne = cleaned_data.get('datum_vzniku_presne')
        rok = cleaned_data.get('rok_vzniku')
        stoleti = cleaned_data.get('stoleti_vzniku')

        filled_fields = sum(1 for field in [datum_presne, rok, stoleti] if field)
        
        if filled_fields == 0:
            raise ValidationError("Musíte vyplnit alespoň jedno z datačních polí (datum, rok nebo století).")
        elif filled_fields > 1:
            raise ValidationError("Vyplňte pouze jedno datační pole.")
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance = self.save_uploaded_file(instance)

        # Zpracování osob
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['druh'].queryset = Druh.objects.all().order_by('nazev')

class FotografieForm(BaseArchivovanyObjektForm):
    class Meta(BaseArchivovanyObjektForm.Meta):
        model = Fotografie
        fields = BaseArchivovanyObjektForm.Meta.fields + ['typ_fotografie', 'vyska', 'sirka']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class OsobaForm(forms.ModelForm):
    class Meta:
        model = Osoba
        fields = ['jmeno', 'prijmeni', 'narozeni', 'umrti', 'pohlavi']
        widgets = {
            'narozeni': forms.DateInput(attrs=DATE_WIDGET_ATTRS),
            'umrti': forms.DateInput(attrs=DATE_WIDGET_ATTRS),
        }

class DruhForm(forms.ModelForm):
    class Meta:
        model = Druh
        fields = ['nazev', 'popis']
        widgets = {
            'popis': forms.Textarea(attrs=TEXTAREA_WIDGET_ATTRS),
        }