from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.urls import reverse
from datetime import date
from .models import *

TEXTAREA_ROWS = 3
OSOBA_SELECT_SIZE = 8
MIN_YEAR = 1000
MAX_YEAR = 2100


DATE_WIDGET_ATTRS = {'type': 'date', 'class': 'form-control'}
TEXTAREA_WIDGET_ATTRS = {'rows': TEXTAREA_ROWS, 'class': 'form-control'}
NUMBER_WIDGET_ATTRS = {'class': 'form-control', 'min': MIN_YEAR, 'max': MAX_YEAR}

DATACE_CHOICES = [
    ('', '--------- Vyberte typ datace ---------'),
    ('datum', 'Přesné datum'),
    ('rok', 'Rok'),
    ('stoleti', 'Století'),
]

class FileUploadMixin(forms.Form):
    uploaded_file = forms.FileField(
        label="Soubor k nahrání", 
        required=False, 
        help_text="Vyberte soubor pro archivaci."
    )

    def save_uploaded_file(self, instance):
        uploaded_file_data = self.cleaned_data.get('uploaded_file')
        if uploaded_file_data:
            if instance.pk and hasattr(instance, 'soubor') and instance.soubor:
                old_soubor_to_delete = instance.soubor
                instance.soubor = None
                old_soubor_to_delete.delete()

            soubor_obj = Soubor.objects.create(file=uploaded_file_data)
            instance.soubor = soubor_obj
        return instance

class BaseArchivovanyObjektForm(FileUploadMixin, forms.ModelForm):
    popis = forms.CharField(
        widget=forms.Textarea(attrs=TEXTAREA_WIDGET_ATTRS), 
        label="Popis objektu", 
        required=False
    )
    
    osoby_vyber = forms.ModelMultipleChoiceField(
        queryset=Osoba.objects.all().order_by('prijmeni', 'jmeno'),
        widget=forms.SelectMultiple(attrs={'size': OSOBA_SELECT_SIZE}),
        label="Osoby spojené s objektem",
        help_text="Vyberte jednu nebo více osob (podržením Ctrl/Cmd). První vybraná osoba bude označena jako hlavní.",
        required=False
    )

    typ_datace = forms.ChoiceField(
        choices=DATACE_CHOICES,
        required=True,
        label="Typ datace vzniku",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    datum_vzniku_presne = forms.DateField(
        widget=forms.DateInput(attrs=DATE_WIDGET_ATTRS),
        required=False, 
        label="Přesné datum vzniku"
    )
    rok_vzniku = forms.IntegerField(
        widget=forms.NumberInput(attrs=NUMBER_WIDGET_ATTRS),
        required=False, 
        label="Rok vzniku"
    )
    stoleti_vzniku = forms.ChoiceField(
        choices=[('', '---------')] + STOLETÍ_CHOICES,
        required=False, 
        label="Století vzniku",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = ArchivovanyObjekt 
        fields = ['popis', 'typ_datace', 'datum_vzniku_presne', 'rok_vzniku', 'stoleti_vzniku', 'osoby_vyber', 'uploaded_file']

    def _add_create_button_to_help_text(self, field_name, add_url_name, button_text):
        if field_name in self.fields:
            current_help_text = self.fields[field_name].help_text or ""
            if not isinstance(current_help_text, str):
                 current_help_text = str(current_help_text)

            add_url = reverse(add_url_name)
            button_html = f' <a href="{add_url}" target="_blank" class="btn btn-sm btn-outline-secondary ms-2">{button_text}</a>'
            self.fields[field_name].help_text = mark_safe(current_help_text + button_html)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_create_button_to_help_text('osoby_vyber', 'archiv_app:add_osoba', 'Přidat osobu')

        if self.instance and self.instance.pk:
            if self.instance.datum_vzniku_presne:
                self.fields['typ_datace'].initial = 'datum'
            elif self.instance.rok_vzniku:
                self.fields['typ_datace'].initial = 'rok'
            elif self.instance.stoleti_vzniku:
                self.fields['typ_datace'].initial = 'stoleti'

    def clean(self):
        cleaned_data = super().clean()
        typ_datace = cleaned_data.get('typ_datace')
        datum_presne = cleaned_data.get('datum_vzniku_presne')
        rok = cleaned_data.get('rok_vzniku')
        stoleti = cleaned_data.get('stoleti_vzniku')

        if not typ_datace: 
            raise ValidationError("Musíte zvolit typ datace.")

        if typ_datace == 'datum':
            if not datum_presne:
                self.add_error('datum_vzniku_presne', "Při typu datace 'Přesné datum' musí být datum vyplněno.")
            if rok or stoleti:
                self.add_error('typ_datace', "Pokud je zvoleno 'Přesné datum', pole Rok a Století musí být prázdná.")
        
        elif typ_datace == 'rok':
            if not rok:
                self.add_error('rok_vzniku', "Při typu datace 'Rok' musí být rok vyplněn.")
            if datum_presne or stoleti:
                self.add_error('typ_datace', "Pokud je zvolen 'Rok', pole Přesné datum a Století musí být prázdná.")

        elif typ_datace == 'stoleti':
            if not stoleti:
                self.add_error('stoleti_vzniku', "Při typu datace 'Století' musí být století vyplněno.")
            if datum_presne or rok:
                self.add_error('typ_datace', "Pokud je zvoleno 'Století', pole Přesné datum a Rok musí být prázdná.")
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance = self.save_uploaded_file(instance)

        typ_datace = self.cleaned_data.get('typ_datace')

        if typ_datace == 'datum':
            instance.rok_vzniku = None
            instance.stoleti_vzniku = None
        elif typ_datace == 'rok':
            instance.datum_vzniku_presne = None
            instance.stoleti_vzniku = None
        elif typ_datace == 'stoleti':
            instance.datum_vzniku_presne = None
            instance.rok_vzniku = None
        elif not typ_datace: 
            instance.datum_vzniku_presne = None
            instance.rok_vzniku = None
            instance.stoleti_vzniku = None

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

    def clean_datum_vzniku_presne(self):
        datum = self.cleaned_data.get('datum_vzniku_presne')
        if datum:
            if datum > date.today():
                raise ValidationError("Datum vzniku nemůže být v budoucnosti.")
            if datum.year < MIN_YEAR:
                raise ValidationError(f"Rok v datu vzniku musí být {MIN_YEAR} nebo pozdější.")
        return datum

class DokumentForm(BaseArchivovanyObjektForm):
    class Meta(BaseArchivovanyObjektForm.Meta):
        model = Dokument
        fields = BaseArchivovanyObjektForm.Meta.fields + ['druh', 'jazyk']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['druh'].queryset = Druh.objects.all().order_by('nazev')
        self._add_create_button_to_help_text('druh', 'archiv_app:add_druh', 'Přidat druh')

class FotografieForm(BaseArchivovanyObjektForm):
    class Meta(BaseArchivovanyObjektForm.Meta):
        model = Fotografie
        fields = BaseArchivovanyObjektForm.Meta.fields + ['typ_fotografie', 'vyska', 'sirka']

class OsobaForm(forms.ModelForm):
    class Meta:
        model = Osoba
        fields = ['jmeno', 'prijmeni', 'narozeni', 'umrti', 'pohlavi']
        widgets = {
            'narozeni': forms.DateInput(attrs=DATE_WIDGET_ATTRS),
            'umrti': forms.DateInput(attrs=DATE_WIDGET_ATTRS),
        }

    def clean(self):
        cleaned_data = super().clean()
        narozeni = cleaned_data.get('narozeni')
        umrti = cleaned_data.get('umrti')
        today = date.today()

        if narozeni:
            if narozeni > today:
                self.add_error('narozeni', "Datum narození nemůže být v budoucnosti.")
            if narozeni.year < MIN_YEAR:
                self.add_error('narozeni', f"Rok narození musí být {MIN_YEAR} nebo pozdější.")

        if umrti:
            if umrti > today:
                self.add_error('umrti', "Datum úmrtí nemůže být v budoucnosti.")
            if umrti.year < MIN_YEAR:
                 self.add_error('umrti', f"Rok úmrtí musí být {MIN_YEAR} nebo pozdější.")

        if narozeni and umrti:
            if umrti < narozeni:
                self.add_error('umrti', "Datum úmrtí nemůže být před datem narození.")
            elif umrti == narozeni:
                self.add_error('umrti', "Datum úmrtí nemůže být stejné jako datum narození.")

        return cleaned_data

class DruhForm(forms.ModelForm):
    class Meta:
        model = Druh
        fields = ['nazev', 'popis']
        widgets = {
            'popis': forms.Textarea(attrs=TEXTAREA_WIDGET_ATTRS),
        }