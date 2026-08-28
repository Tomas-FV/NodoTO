
from django.urls import path
from UsersHub import views

urlpatterns = [
    path('pautas/', views.pautas_view, name='pautas'),
    path('pautas/<int:pauta_id>/evaluar/', views.evaluar_pauta_view, name='pautas_evaluar'),
    path('mis-evaluaciones/', views.mis_evaluaciones_view, name='mis_evaluaciones'),
    path('mis-evaluaciones/<int:evaluacion_id>/', views.mi_evaluacion_detalle_view, name='mi_evaluacion_detalle'),
]