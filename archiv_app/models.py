from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from polymorphic.models import PolymorphicModel
from django.db.models import Q

class Osoba(models.Model):
    jmeno = models.CharField(
        max_length=100, 
        blank=False, 
        help_text="Jméno osoby", 
        verbose_name="Jméno", 
        error_messages={'blank': 'Jméno osoby nesmí být prázdné.'})
    
    prijmeni = models.CharField(
        max_length=100, 
        blank=False, 
        help_text="Příjmení osoby", 
        verbose_name="Příjmení", 
        error_messages={'blank': 'Příjmení osoby nesmí být prázdné.'})
    
    narozeni = models.DateField(
        null=True, blank=True, 
        help_text="Datum narození osoby", 
        verbose_name="Datum narození")
    
    umrti = models.DateField(
        null=True, blank=True, 
        help_text="Datum úmrtí osoby", 
        verbose_name="Datum úmrtí")
    
    pohlavi = models.CharField(
        max_length=1, 
        choices=[('M', 'Muž'), ('F', 'Žena')], 
        blank=True, null=True, 
        help_text="Pohlaví osoby", 
        verbose_name="Pohlaví")

    class Meta:
        ordering = ['prijmeni', 'jmeno']
        verbose_name = "Osoba"
        verbose_name_plural = "Osoby"
    
    def __str__(self):
        return f"{self.jmeno} {self.prijmeni}"

    @property
    def cele_jmeno(self):
        return f"{self.jmeno} {self.prijmeni}"

    def get_archiválie_count(self):
        count = ArchivovanyObjekt.objects.filter(
            Q(osoba=self) | Q(osoby=self)
        ).distinct().count()
        return count


class Soubor(models.Model):
    file = models.FileField(upload_to='archivovane_soubory/', help_text="Soubor k archivaci", verbose_name="Soubor")
    class Meta:
        verbose_name = "Soubor"
        verbose_name_plural = "Soubory"
    
    def __str__(self):
        return self.file.name

class Druh(models.Model):
    nazev = models.CharField(
        max_length=100, blank=False, 
        help_text="Název druhu dokumentu", 
        verbose_name="Název druhu", 
        error_messages={'blank': 'Název druhu dokumentu nesmí být prázdný.'})
    
    popis = models.TextField(
        blank=True, 
        help_text="Popis druhu dokumentu", 
        verbose_name="Popis druhu")
    class Meta:
        ordering = ['nazev']
        verbose_name = 'Druh dokumentu'
        verbose_name_plural = 'Druhy dokumentů'

    def __str__(self):
        return self.nazev

STOLETÍ_CHOICES = [
    ('15', '15. století'),
    ('16', '16. století'),
    ('17', '17. století'),
    ('18', '18. století'),
    ('19', '19. století'),
    ('20', '20. století'),
    ('21', '21. století'),
]

class ArchivovanyObjekt(PolymorphicModel):
    TYPY_OBJEKTU = [
        ('dokument', 'Dokument'),
        ('fotografie', 'Fotografie'),
    ]

    typ = models.CharField(max_length=20, choices=TYPY_OBJEKTU, blank=False, help_text="Typ objektu", verbose_name="Typ objektu", error_messages={'blank': 'Typ objektu musí být vybrán.'})
    osoba = models.ForeignKey(Osoba, on_delete=models.SET_NULL, null=True, blank=True,help_text="Osoba, s objektem spojená", verbose_name="Osoba")
    soubor = models.ForeignKey(Soubor, on_delete=models.CASCADE, null=True, blank=True, help_text="Soubor k archivaci", verbose_name="Soubor")
    datum_archivace = models.DateField(default=timezone.now, help_text="Datum archivace objektu", verbose_name="Datum archivace")
    popis = models.TextField(blank=True, help_text="Popis objektu", verbose_name="Popis")
    
    # Původní pole 'stari' je nahrazeno těmito třemi:
    datum_vzniku_presne = models.DateField(
        verbose_name="Přesné datum vzniku", 
        null=True, blank=True, 
        help_text="Přesné datum vzniku objektu (DD.MM.RRRR)."
    )
    rok_vzniku = models.PositiveIntegerField(
        verbose_name="Rok vzniku", 
        null=True, blank=True, 
        help_text="Rok vzniku objektu (např. 1950).",
        validators=[MinValueValidator(1000), MaxValueValidator(timezone.now().year + 5)]
    )
    stoleti_vzniku = models.CharField(
        max_length=2, 
        choices=STOLETÍ_CHOICES, 
        verbose_name="Století vzniku", 
        null=True, blank=True, 
        help_text="Století, ve kterém objekt vznikl."
    )

    osoby = models.ManyToManyField(Osoba, related_name="objekty", blank=True, help_text="Osoby spojené s objektem", verbose_name="Osoby")

    class Meta:
        ordering = ['-datum_archivace', 'typ']
        verbose_name = 'Archivovaný objekt'
        verbose_name_plural = 'Archivované objekty'
        
    def get_datace_display(self):
        if self.datum_vzniku_presne:
            return self.datum_vzniku_presne.strftime("%d.%m.%Y")
        elif self.rok_vzniku:
            return str(self.rok_vzniku)
        elif self.stoleti_vzniku:
            return self.get_stoleti_vzniku_display()
        return "-"
    get_datace_display.short_description = "Datace vzniku"

    def __str__(self):
        return f"{self.typ.capitalize()} #{self.id} ({self.get_datace_display()})"
    
    def delete(self, *args, **kwargs):
        if self.soubor and self.soubor.file:
            self.soubor.file.delete(save=False)
        super().delete(*args, **kwargs)

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
        ('jin', 'Jiný'),
    ]

    druh = models.ForeignKey(
        Druh,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, 
        verbose_name='Druh dokumentu',
        help_text='Vyberte druh dokumentu.'
    )
    jazyk = models.CharField(
        max_length=3, 
        choices=JAZYK_CHOICES,
        verbose_name='Jazyk dokumentu',
        help_text='Vyberte jazyk, ve kterém je dokument napsán.',
        blank=False, 
        default='cs', 
        error_messages={'blank': 'Jazyk dokumentu musí být vybrán.'} 
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


