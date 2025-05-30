from django.views.decorators.http import require_POST
from django.contrib import messages # Pro zobrazení zpráv uživateli
from .models import Dokument, Fotografie, Osoba, Soubor, Druh
from .forms import DokumentForm, FotografieForm, OsobaForm, DruhForm # Import formulářů
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect


# Create your views here.
def main_page(request):
    """View for the main page of the archive site - now only statistics."""
    context = {
        'dokumenty_count': Dokument.objects.count(),
        'fotografie_count': Fotografie.objects.count(),
        'osoby_count': Osoba.objects.count(),
    }
    return render(request, 'archiv_app/main.html', context)

def dokumenty_list_view(request):
    """View to list all documents."""
    dokumenty = Dokument.objects.all()
    context = {
        'dokumenty_list': dokumenty,
    }
    return render(request, 'archiv_app/dokumenty_list.html', context)

def fotografie_list_view(request):
    """View to list all photographs."""
    fotografie = Fotografie.objects.all()
    context = {
        'fotografie_list': fotografie,
    }
    return render(request, 'archiv_app/fotografie_list.html', context)

def osoby_list_view(request):
    """View to list all persons."""
    osoby_queryset = Osoba.objects.all()

    context = {
        'osoby': osoby_queryset,
    }
    return render(request, 'archiv_app/osoby_list.html', context)

def druhy_list_view(request):
    """View to list all Druh objects."""
    druhy = Druh.objects.all().order_by('nazev')
    context = {
        'druhy_list': druhy,
    }
    return render(request, 'archiv_app/druhy_list.html', context)




@require_POST
def delete_druh_view(request, pk):
    """View to delete a Druh object."""
    druh = get_object_or_404(Druh, pk=pk)
    try:
        # Zjistíme, zda je tento druh používán v nějakých dokumentech
        if Dokument.objects.filter(druh=druh).exists():
            messages.error(request, f"Druh '{druh.nazev}' nelze smazat, protože je používán alespoň jedním dokumentem.")
        else:
            nazev_druhu = druh.nazev
            druh.delete()
            messages.success(request, f"Druh '{nazev_druhu}' byl úspěšně smazán.")
    except Exception as e:
        messages.error(request, f"Chyba při mazání druhu: {e}")
    return redirect('archiv_app:druhy_list')

@require_POST
def delete_dokument_view(request, pk):
    """View to delete a document."""
    dokument = get_object_or_404(Dokument, pk=pk)

    try:
        # Pokud soubor existuje, smažeme ho nejprve z disku
        if dokument.soubor and dokument.soubor.file:
            dokument.soubor.file.delete(save=False) 
        
        if dokument.soubor:
            dokument.soubor = None 
            dokument.save() 

        dokument.delete()
        messages.success(request, f"Dokument '{dokument.popis if dokument.popis else f'ID {dokument.pk}'}' byl úspěšně smazán.")
    except Exception as e:
        messages.error(request, f"Chyba při mazání dokumentu: {e}")
    return redirect('archiv_app:dokumenty_list')

@require_POST
def delete_fotografie_view(request, pk):
    """View to delete a photograph."""
    fotografie = get_object_or_404(Fotografie, pk=pk)

    try:
        if fotografie.soubor and fotografie.soubor.file:
            fotografie.soubor.file.delete(save=False)
        
        if fotografie.soubor:
            fotografie.soubor = None 
            fotografie.save()

        fotografie.delete()
        messages.success(request, f"Fotografie '{fotografie.popis if fotografie.popis else f'ID {fotografie.pk}'}' byla úspěšně smazána.")
    except Exception as e:
        messages.error(request, f"Chyba při mazání fotografie: {e}")
    return redirect('archiv_app:fotografie_list')

@require_POST
def delete_osoba_view(request, pk):
    """View to delete a person."""
    osoba = get_object_or_404(Osoba, pk=pk)

    try:

        jmeno_osoby = str(osoba) 
        osoba.delete()
        messages.success(request, f"Osoba '{jmeno_osoby}' byla úspěšně smazána.")
    except Exception as e:

        messages.error(request, f"Chyba při mazání osoby: {e}")
    return redirect('archiv_app:osoby_list')


def _generic_add_view(request, FormClass, success_url_name, form_title, object_type_name_singular, template_name='archiv_app/object_form.html'):
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            messages.success(request, f"{object_type_name_singular.capitalize()} '{instance}' byl úspěšně přidán.")
            return redirect(success_url_name)
        else:
            messages.error(request, "Prosím, opravte chyby ve formuláři.")
    else:
        form = FormClass()

    return render(request, template_name, {
        'form': form,
        'form_title': form_title,
        'type': object_type_name_singular.lower(), 
        'is_edit': False,
        'next': success_url_name
    })

def add_dokument_view(request):
    return _generic_add_view(
        request,
        DokumentForm,
        reverse_lazy('archiv_app:dokumenty_list'),
        "Přidat nový dokument",
        "Dokument"
    )

def add_fotografie_view(request):
    return _generic_add_view(
        request,
        FotografieForm,
        reverse_lazy('archiv_app:fotografie_list'),
        "Přidat novou fotografii",
        "Fotografie"
    )

def add_osoba_view(request):
    return _generic_add_view(
        request,
        OsobaForm,
        reverse_lazy('archiv_app:osoby_list'),
        "Přidat novou osobu",
        "Osoba"
    )

def add_druh_view(request):
    return _generic_add_view(
        request,
        DruhForm,
        reverse_lazy('archiv_app:druhy_list'),
        "Přidat nový druh dokumentu",
        "Druh dokumentu" # Nebo jen "Druh"
    )

def _generic_edit_view(request, pk, ModelClass, FormClass, success_url_name, form_title_prefix, template_name='archiv_app/object_form.html'):
    obj = get_object_or_404(ModelClass, pk=pk)
    form_title = f"{form_title_prefix} '{obj}'"

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"{ModelClass.__name__} '{obj}' byl úspěšně upraven.")
            return redirect(success_url_name)
        else:
            messages.error(request, "Prosím, opravte chyby ve formuláři.")
    else:
        form = FormClass(instance=obj)

    return render(request, template_name, {
        'form': form, 
        'object': obj, 
        'form_title': form_title, 
        'is_edit': True,
        'type': ModelClass.__name__.lower() 
    })

def edit_dokument_view(request, pk):
    return _generic_edit_view(
        request, pk, Dokument, DokumentForm, 
        reverse_lazy('archiv_app:dokumenty_list'), 
        "Upravit dokument"
    )

def edit_fotografie_view(request, pk):
    return _generic_edit_view(
        request, pk, Fotografie, FotografieForm, 
        reverse_lazy('archiv_app:fotografie_list'), 
        "Upravit fotografii"
    )

def edit_osoba_view(request, pk):
    return _generic_edit_view(
        request, pk, Osoba, OsobaForm, 
        reverse_lazy('archiv_app:osoby_list'), 
        "Upravit osobu",

    )
