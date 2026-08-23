from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='adminhub_view'),
    path('pautas/', views.pauta_list_view, name='adminhub_pautas'),
    path('pautas/crear/', views.pauta_create_view, name='adminhub_pauta_create'),
    path('pautas/<int:pauta_id>/', views.pauta_detail_view, name='adminhub_pauta_detail'),
    path('pautas/<int:pauta_id>/editar/', views.pauta_edit_view, name='adminhub_pauta_edit'),
    path('pautas/<int:pauta_id>/eliminar/', views.pauta_delete_view, name='adminhub_pauta_delete'),
    path('pautas/<int:pauta_id>/versiones/crear/', views.version_create_view, name='adminhub_version_create'),
    path('pautas/<int:pauta_id>/versiones/<int:version_id>/editar/', views.version_edit_view, name='adminhub_version_edit'),
    path('pautas/<int:pauta_id>/versiones/<int:version_id>/eliminar/', views.version_delete_view, name='adminhub_version_delete'),
    path('pautas/<int:pauta_id>/reglas/crear/', views.regla_create_view, name='adminhub_regla_create'),
    path('pautas/<int:pauta_id>/reglas/<int:regla_id>/editar/', views.regla_edit_view, name='adminhub_regla_edit'),
    path('pautas/<int:pauta_id>/reglas/<int:regla_id>/eliminar/', views.regla_delete_view, name='adminhub_regla_delete'),

    path('pautas/<int:pauta_id>/campos/crear/', views.campo_create_view, name='adminhub_campo_create'),
    path('pautas/<int:pauta_id>/campos/<int:campo_id>/editar/', views.campo_edit_view, name='adminhub_campo_edit'),
    path('pautas/<int:pauta_id>/campos/<int:campo_id>/eliminar/', views.campo_delete_view, name='adminhub_campo_delete'),

    path('pautas/<int:pauta_id>/campos/<int:campo_id>/items/crear/', views.item_create_view, name='adminhub_item_create'),
    path('pautas/<int:pauta_id>/campos/<int:campo_id>/items/<int:item_id>/editar/', views.item_edit_view, name='adminhub_item_edit'),
    path('pautas/<int:pauta_id>/campos/<int:campo_id>/items/<int:item_id>/eliminar/', views.item_delete_view, name='adminhub_item_delete'),

    path('pautas/<int:pauta_id>/campos/<int:campo_id>/items/<int:item_id>/opciones/crear/', views.opcion_create_view, name='adminhub_opcion_create'),
    path('pautas/<int:pauta_id>/campos/<int:campo_id>/items/<int:item_id>/opciones/<int:opcion_id>/editar/', views.opcion_edit_view, name='adminhub_opcion_edit'),
    path('pautas/<int:pauta_id>/campos/<int:campo_id>/items/<int:item_id>/opciones/<int:opcion_id>/eliminar/', views.opcion_delete_view, name='adminhub_opcion_delete'),
]
