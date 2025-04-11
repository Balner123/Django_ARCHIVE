from django.db import models
from polymorphic.models import PolymorphicModel

from django.db import models

class Osoba(models.Model):
    jmeno = models.CharField(max_length=100)
    prijmeni = models.CharField(max_length=100)
    narozeni = models.DateField(null=True, blank=True)
    umrti = models.DateField(null=True, blank=True)
    pohlavi = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.jmeno} {self.prijmeni}"


class Soubor(models.Model):
    file = models.FileField(upload_to='archivovane_soubory/')

    def __str__(self):
        return self.file.name


class ArchivovanyObjekt(PolymorphicModel):
    TYPY_OBJEKTU = [
        ('dokument', 'Dokument'),
        ('fotografie', 'Fotografie'),
    ]

    typ = models.CharField(max_length=20, choices=TYPY_OBJEKTU)
    osoba = models.ForeignKey(Osoba, on_delete=models.SET_NULL, null=True, blank=True)
    soubor = models.ForeignKey(Soubor, on_delete=models.SET_NULL, null=True, blank=True)
    datum_archivace = models.DateField()
    popis = models.TextField(blank=True)
    stari = models.IntegerField()

    # Vazba N:M na Osoby (týká se)
    osoby = models.ManyToManyField(Osoba, related_name="objekty", blank=True)

    def __str__(self):
        return f"{self.typ.capitalize()} #{self.id}"


class Druh(models.Model):
    nazev = models.CharField(max_length=100)
    popis = models.TextField(blank=True)

    def __str__(self):
        return self.nazev


class Dokument(ArchivovanyObjekt):
    druh = models.ForeignKey(Druh, on_delete=models.SET_NULL, null=True)
    jazyk = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumenty"


class Fotografie(ArchivovanyObjekt):
    typ_fotografie = models.CharField(max_length=50)
    vyska = models.PositiveIntegerField()
    sirka = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Fotografie"
        verbose_name_plural = "Fotografie"
