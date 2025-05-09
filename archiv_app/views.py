from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, Http404
from django.views.decorators.http import require_POST
from django.contrib import messages # Pro zobrazení zpráv uživateli
from .models import Dokument, Fotografie, Osoba, Soubor
from .forms import DokumentForm, FotografieForm, OsobaForm, DruhForm # Import formulářů
from django.urls import reverse_lazy, reverse
from django.conf import settings
import os

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

            pass

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

# Nové pohledy pro osoby
def osoby_list_view(request):
    """View to list all persons."""
    osoby_queryset = Osoba.objects.all()


    context = {
        'osoby': osoby_queryset,
    }
    return render(request, 'archiv_app/osoby_list.html', context)

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

# --- Nové pohledy pro přidávání objektů ---


def add_object_form_view(request, form_type=None):

    FormClass = None
    form_title = "Přidat nový objekt"
    template_name = 'archiv_app/object_form.html' 

    if form_type == 'dokument':
        FormClass = DokumentForm
        form_title = "Přidat nový dokument"
    elif form_type == 'fotografie':
        FormClass = FotografieForm
        form_title = "Přidat novou fotografii"
    else:
        messages.error(request, "Neznámý typ objektu pro přidání.")

        return redirect('archiv_app:main') 

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            messages.success(request, f"{form_type.capitalize()} '{instance}' byl úspěšně přidán.")
            if form_type == 'dokument':
                return redirect('archiv_app:dokumenty_list')
            elif form_type == 'fotografie':
                return redirect('archiv_app:fotografie_list')
        else:
            messages.error(request, "Prosím, opravte chyby ve formuláři.")
    else:
        form = FormClass()

    return render(request, template_name, {
        'form': form, 
        'form_title': form_title, 
        'object_type': form_type, 
        'type': form_type, 
        'is_edit': False
    })

# --- Pohledy pro úpravy ---
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

# View for adding a new Person
def add_osoba_view(request):
    form_title = "Přidat novou osobu"
    template_name = 'archiv_app/object_form.html'

    if request.method == 'POST':
        form = OsobaForm(request.POST) # No request.FILES needed for OsobaForm
        if form.is_valid():
            instance = form.save()
            messages.success(request, f"Osoba '{instance}' byla úspěšně přidána.")
            return redirect('archiv_app:osoby_list') # Redirect to the list of persons
        else:
            messages.error(request, "Prosím, opravte chyby ve formuláři.")
    else:
        form = OsobaForm()

    return render(request, template_name, {
        'form': form, 
        'form_title': form_title, 
        'type': 'osoba', # For the cancel button logic in object_form.html
        'is_edit': False
    })

def add_druh_view(request):
    form_title = "Přidat nový druh dokumentu"
    template_name = 'archiv_app/object_form.html' 

    if request.method == 'POST':
        form = DruhForm(request.POST)
        if form.is_valid():
            instance = form.save()
            messages.success(request, f"Druh dokumentu '{instance}' byl úspěšně přidán.")
            # Redirect back to the previous page, or to where it makes sense.
            # For now, let's redirect to add_object_form with type=dokument.
            # A more sophisticated approach might use request.META.get('HTTP_REFERER')
            # or pass a 'next' parameter.
            # We also need to ensure the user was adding a document.
            # For simplicity, we redirect to the add dokument form.
            # This assumes the user came from there. 
            # A better way is to pass a 'next' URL parameter.
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                # Fallback if next is not provided, perhaps list of Druh objects or main page.
                # For now, back to the add_dokument form.
                return redirect(reverse('archiv_app:add_dokument'))
        else:
            messages.error(request, "Prosím, opravte chyby ve formuláři.")
    else:
        form = DruhForm()

    return render(request, template_name, {
        'form': form,
        'form_title': form_title,
        'type': 'druh', # For cancel button or other logic in object_form if needed
        'is_edit': False,
        'next': request.GET.get('next', reverse('archiv_app:add_dokument')) # Pass next to template for cancel button
    })
