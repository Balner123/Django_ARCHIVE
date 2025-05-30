from django.urls import path
from .views import *


app_name = 'archiv_app'

urlpatterns = [
    path('', main_page, name='main'),
    path('dokumenty/', dokumenty_list_view, name='dokumenty_list'),
    path('fotografie/', fotografie_list_view, name='fotografie_list'),
    path('osoby/', osoby_list_view, name='osoby_list'),
    path('druhy/', druhy_list_view, name='druhy_list'),
    
    path('dokumenty/edit/<int:pk>/', edit_dokument_view, name='edit_dokument'),
    path('fotografie/edit/<int:pk>/', edit_fotografie_view, name='edit_fotografie'),
    path('osoby/edit/<int:pk>/', edit_osoba_view, name='edit_osoba'),
    
    path('dokumenty/delete/<int:pk>/', delete_dokument_view, name='delete_dokument'),
    path('fotografie/delete/<int:pk>/', delete_fotografie_view, name='delete_fotografie'),
    path('osoby/delete/<int:pk>/', delete_osoba_view, name='delete_osoba'),
    path('druhy/delete/<int:pk>/', delete_druh_view, name='delete_druh'),
    
    path('dokumenty/add/', add_dokument_view, name='add_dokument'),
    path('fotografie/add/', add_fotografie_view, name='add_fotografie'),
    path('osoby/add/', add_osoba_view, name='add_osoba'),
    path('druh/add/', add_druh_view, name='add_druh'),
] 