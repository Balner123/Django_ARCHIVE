from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.db import models, IntegrityError


def main_page(request):
    context = {
        'dokumenty_count': Dokument.objects.count(),
        'fotografie_count': Fotografie.objects.count(),
        'osoby_count': Osoba.objects.count(),
    }
    return render(request, 'archiv_app/main.html', context)

def _generic_list_view(request, ModelClass: type[models.Model], template_name: str, context_object_name: str, order_by_field: str = None):
    queryset = ModelClass.objects.all()
    if order_by_field:
        queryset = queryset.order_by(order_by_field)
    
    context = {
        context_object_name: queryset,
    }
    return render(request, template_name, context)

def dokumenty_list_view(request):
    return _generic_list_view(request, Dokument, 'archiv_app/dokumenty_list.html', 'dokumenty_list')

def fotografie_list_view(request):
    return _generic_list_view(request, Fotografie, 'archiv_app/fotografie_list.html', 'fotografie_list')

def osoby_list_view(request):
    return _generic_list_view(request, Osoba, 'archiv_app/osoby_list.html', 'osoby')

def druhy_list_view(request):
    return _generic_list_view(request, Druh, 'archiv_app/druhy_list.html', 'druhy_list', order_by_field='nazev')

def _druh_pre_delete_check(druh_instance):
    if Dokument.objects.filter(druh=druh_instance).exists():
        return False, f"Druh '{druh_instance.nazev}' nelze smazat, protože je používán alespoň jedním dokumentem."
    return True, ""

def _delete_associated_soubor_callback(instance_being_deleted):
    soubor_obj = getattr(instance_being_deleted, 'soubor', None)
    if soubor_obj:
        soubor_obj.delete()

@require_POST
def _generic_delete_view(request, pk, ModelClass: type[models.Model], 
                         success_url_name: str, 
                         obj_type_name: str,
                         pre_delete_check_callback=None, 
                         pre_main_obj_delete_related_callback=None):
    obj = get_object_or_404(ModelClass, pk=pk)
    obj_repr = str(obj) 

    if pre_delete_check_callback:
        can_delete, message = pre_delete_check_callback(obj)
        if not can_delete:
            messages.error(request, message)
            return redirect(success_url_name)

    try:
        if pre_main_obj_delete_related_callback:
            pre_main_obj_delete_related_callback(obj)

        obj.delete()
        messages.success(request, f"{obj_type_name.capitalize()} '{obj_repr}' byl úspěšně smazán.")
    except IntegrityError:
        messages.error(request, f"{obj_type_name.capitalize()} '{obj_repr}' nelze smazat, protože je používán v jiných záznamech.")
    except Exception as e:
        messages.error(request, f"Chyba při mazání {obj_type_name.lower()} '{obj_repr}': {e}")
    
    return redirect(success_url_name)

@require_POST
def delete_druh_view(request, pk):
    return _generic_delete_view(request, pk, Druh, 
                                success_url_name=reverse_lazy('archiv_app:druhy_list'), 
                                obj_type_name="Druh",
                                pre_delete_check_callback=_druh_pre_delete_check)

@require_POST
def delete_dokument_view(request, pk):
    return _generic_delete_view(request, pk, Dokument, 
                                success_url_name=reverse_lazy('archiv_app:dokumenty_list'), 
                                obj_type_name="Dokument",
                                pre_main_obj_delete_related_callback=_delete_associated_soubor_callback)

@require_POST
def delete_fotografie_view(request, pk):
    return _generic_delete_view(request, pk, Fotografie, 
                                success_url_name=reverse_lazy('archiv_app:fotografie_list'), 
                                obj_type_name="Fotografie",
                                pre_main_obj_delete_related_callback=_delete_associated_soubor_callback)

@require_POST
def delete_osoba_view(request, pk):
    return _generic_delete_view(request, pk, Osoba, 
                                success_url_name=reverse_lazy('archiv_app:osoby_list'), 
                                obj_type_name="Osoba")

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
        "Druh dokumentu" 
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
