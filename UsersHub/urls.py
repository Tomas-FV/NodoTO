
from django.urls import path
from UsersHub import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('pautas/', views.pautas_view, name='pautas'),
    path('sobrenodoto/', views.sobrenodoto_view, name='sobrenodoto'),
]