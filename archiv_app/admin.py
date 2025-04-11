from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter
)

from .models import (
    Osoba, Soubor, ArchivovanyObjekt,
    Dokument, Fotografie, Druh
)

# 🧍‍♀️ Osoba
@admin.register(Osoba)
class OsobaAdmin(admin.ModelAdmin):
    list_display = ("jmeno", "prijmeni", "narozeni", "umrti", "pohlavi")
    search_fields = ("jmeno", "prijmeni")


# 📂 Soubor
@admin.register(Soubor)
class SouborAdmin(admin.ModelAdmin):
    list_display = ("file",)


# 📑 Druh
@admin.register(Druh)
class DruhAdmin(admin.ModelAdmin):
    list_display = ("nazev",)
    search_fields = ("nazev",)


# 🧾 Dokument – podtřída
@admin.register(Dokument)
class DokumentAdmin(PolymorphicChildModelAdmin):
    base_model = Dokument
    show_in_index = True
    list_display = ("id", "jazyk", "druh")


# 📸 Fotografie – podtřída
@admin.register(Fotografie)
class FotografieAdmin(PolymorphicChildModelAdmin):
    base_model = Fotografie
    show_in_index = True
    list_display = ("id", "typ_fotografie", "vyska", "sirka")


# 📦 Archivovaný objekt – nadtřída (rodič)
@admin.register(ArchivovanyObjekt)
class ArchivovanyObjektAdmin(PolymorphicParentModelAdmin):
    base_model = ArchivovanyObjekt
    child_models = (Dokument, Fotografie)
    list_filter = (PolymorphicChildModelFilter,)
    list_display = ("id", "typ", "osoba", "datum_archivace", "stari")
