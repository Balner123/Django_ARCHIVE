from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from polymorphic.models import PolymorphicModel

class Osoba(models.Model):
    jmeno = models.CharField(max_length=100, blank=False, null=False, help_text="Jméno osoby", verbose_name="Jméno")
    prijmeni = models.CharField(max_length=100, blank=False, null=False, help_text="Příjmení osoby", verbose_name="Příjmení")
    narozeni = models.DateField(null=True, blank=True, help_text="Datum narození osoby", verbose_name="Datum narození")
    umrti = models.DateField(null=True, blank=True, help_text="Datum úmrtí osoby", verbose_name="Datum úmrtí")
    pohlavi = models.CharField(max_length=10, choices=[('M', 'Muž'), ('F', 'Žena')], blank=True, null=True, help_text="Pohlaví osoby", verbose_name="Pohlaví")

    class Meta:
        ordering = ['prijmeni', 'jmeno']
        verbose_name = "Osoba"
        verbose_name_plural = "Osoby"
    
    def __str__(self):
        return f"{self.jmeno} {self.prijmeni}"


class Soubor(models.Model):
    file = models.FileField(upload_to='archivovane_soubory/', help_text="Soubor k archivaci", verbose_name="Soubor")
    class Meta:
        verbose_name = "Soubor"
        verbose_name_plural = "Soubory"
    
    def __str__(self):
        return self.file.name

class Druh(models.Model):
    nazev = models.CharField(max_length=100, help_text="Název druhu dokumentu", verbose_name="Název druhu")
    popis = models.TextField(blank=True, help_text="Popis druhu dokumentu", verbose_name="Popis druhu")
    class Meta:
        ordering = ['nazev']
        verbose_name = 'Druh dokumentu'
        verbose_name_plural = 'Druhy dokumentů'

    def __str__(self):
        return self.nazev

class ArchivovanyObjekt(PolymorphicModel):
    TYPY_OBJEKTU = [
        ('dokument', 'Dokument'),
        ('fotografie', 'Fotografie'),
    ]

    typ = models.CharField(max_length=20, choices=TYPY_OBJEKTU,help_text="Typ objektu", verbose_name="Typ objektu")
    osoba = models.ForeignKey(Osoba, on_delete=models.SET_NULL, null=True, blank=True,help_text="Osoba, s objektem spojená", verbose_name="Osoba")
    soubor = models.ForeignKey(Soubor, on_delete=models.SET_NULL, null=True, blank=True, help_text="Soubor k archivaci", verbose_name="Soubor")
    datum_archivace = models.DateField(default=timezone.now, help_text="Datum archivace objektu", verbose_name="Datum archivace")
    popis = models.TextField(blank=True, help_text="Popis objektu", verbose_name="Popis")
    stari = models.IntegerField(help_text="Z jakého roku objekt pochází", verbose_name="Stáří")

    osoby = models.ManyToManyField(Osoba, related_name="objekty", blank=True, help_text="Osoby spojené s objektem", verbose_name="Osoby")
    class Meta:
        ordering = ['-datum_archivace', 'typ']
        verbose_name = 'Archivovaný objekt'
        verbose_name_plural = 'Archivované objekty'
    
    def __str__(self):
        return f"{self.typ.capitalize()} #{self.id}"

class Dokument(ArchivovanyObjekt):
    JAZYK_CHOICES = [
        ('cs', 'Čeština'),
        ('sk', 'Slovenština'),
        ('en', 'Angličtina'),
        ('de', 'Němčina'),
        ('pl', 'Polština'),
        ('fr', 'Francouzština'),
        ('la', 'Latina'),
        ('ru', 'Ruština'),
        # Přidejte další jazyky podle potřeby
        ('jin', 'Jiný'),
    ]

    druh = models.ForeignKey(
        Druh,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, # Pokud je druh volitelný
        verbose_name='Druh dokumentu',
        help_text='Vyberte druh dokumentu.'
    )
    jazyk = models.CharField(
        max_length=3, # Upravte max_length podle délky vašich zkratek
        choices=JAZYK_CHOICES,
        verbose_name='Jazyk dokumentu',
        help_text='Vyberte jazyk, ve kterém je dokument napsán.',
        blank=False, # Nastavte na False, pokud je jazyk povinný
        default='cs', # Volitelně nastavte výchozí jazyk
        error_messages={'blank': 'Jazyk dokumentu musí být vybrán.'} # Pokud je povinnýllled
    )
    def save(self, *args, **kwargs):
        self.typ = 'dokument'
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumenty"
        ordering = ['-datum_archivace', 'jazyk']

class Fotografie(ArchivovanyObjekt):
    typ_fotografie = models.CharField(
        max_length=50,
        verbose_name='Typ fotografie',
        help_text='Např. portrét, krajina, reportážní, skupinová.',
        blank=True
    )
    vyska = models.PositiveIntegerField(
        verbose_name='Výška (cm)',
        validators=[MinValueValidator(1)],
        help_text='Zadejte výšku fotografie (musí být > 0).',
        error_messages={'blank': 'Výška fotografie musí být vyplněna.'}
    )
    sirka = models.PositiveIntegerField(
        verbose_name='Šířka (cm)',
        validators=[MinValueValidator(1)],
        help_text='Zadejte šířku fotografie (musí být > 0).',
        error_messages={'blank': 'Šířka fotografie musí být vyplněna.'} 
    )

    def save(self, *args, **kwargs):
        self.typ = 'fotografie'
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Fotografie"
        verbose_name_plural = "Fotografie"
        ordering = ['-datum_archivace', 'typ_fotografie']


