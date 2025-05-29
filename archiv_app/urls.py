from django.urls import path
from .views import (
    main_page, 
    dokumenty_list_view, 
    fotografie_list_view, 
    osoby_list_view,
    delete_dokument_view, 
    delete_fotografie_view,
    delete_osoba_view,
    add_object_form_view,
    edit_dokument_view,
    edit_fotografie_view,
    edit_osoba_view,
    add_osoba_view,
    add_druh_view,
    druhy_list_view,
    delete_druh_view,
)

app_name = 'archiv_app'  # Přidání app_name pro jmenné prostory URL

urlpatterns = [
    path('', main_page, name='main'),
    path('dokumenty/', dokumenty_list_view, name='dokumenty_list'),
    path('fotografie/', fotografie_list_view, name='fotografie_list'),
    path('osoby/', osoby_list_view, name='osoby_list'),
    path('dokumenty/edit/<int:pk>/', edit_dokument_view, name='edit_dokument'),
    path('fotografie/edit/<int:pk>/', edit_fotografie_view, name='edit_fotografie'),
    path('osoby/edit/<int:pk>/', edit_osoba_view, name='edit_osoba'),
    path('dokumenty/delete/<int:pk>/', delete_dokument_view, name='delete_dokument'),
    path('fotografie/delete/<int:pk>/', delete_fotografie_view, name='delete_fotografie'),
    path('osoby/delete/<int:pk>/', delete_osoba_view, name='delete_osoba'),
    path('dokumenty/add/', add_object_form_view, {'form_type': 'dokument'}, name='add_dokument'),
    path('fotografie/add/', add_object_form_view, {'form_type': 'fotografie'}, name='add_fotografie'),
    path('osoby/add/', add_osoba_view, name='add_osoba'),
    path('druh/add/', add_druh_view, name='add_druh'),
    path('druhy/', druhy_list_view, name='druhy_list'),
    path('druhy/delete/<int:pk>/', delete_druh_view, name='delete_druh'),
    path('add/', add_object_form_view, {'form_type': None}, name='add_object_form'),
] 