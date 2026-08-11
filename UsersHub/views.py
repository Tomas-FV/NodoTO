from django.shortcuts import render

# Create your views here.

def home_view(request):
    return render(request, 'index.html')

def pautas_view(request):
    return render(request, 'pautas.html')

def sobrenodoto_view(request):
    return render(request, 'sobrenodoto.html')