from django.shortcuts import render
from .models import Dokument, Fotografie, Osoba

# Create your views here.
def main_page(request):
    """View for the main page of the archive site."""
    # Get counts for each model to display on the main page
    context = {
        'dokumenty_count': Dokument.objects.count(),
        'fotografie_count': Fotografie.objects.count(),
        'osoby_count': Osoba.objects.count(),
    }
    return render(request, 'archiv_app/main.html', context)
