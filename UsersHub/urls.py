
from django.urls import path
from UsersHub import views

urlpatterns = [
    path('', views.home_view, name='home'),
]