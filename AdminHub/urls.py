from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='adminhub_view'),
    path('preview-404/', views.preview_404_view, name='adminhub_preview_404'),
    path('usuarios/', views.usuario_list_view, name='adminhub_usuarios'),
    path('usuarios/crear/', views.usuario_create_view, name='adminhub_usuario_create'),
    path('usuarios/<int:usuario_id>/editar/', views.usuario_edit_view, name='adminhub_usuario_edit'),
    path('usuarios/<int:usuario_id>/estado/', views.usuario_toggle_active_view, name='adminhub_usuario_toggle_active'),
    path('usuarios/<int:usuario_id>/clave/', views.usuario_reset_password_view, name='adminhub_usuario_reset_password'),
    path('reportes/', views.reporte_list_view, name='adminhub_reportes'),
    path('reportes/<int:reporte_id>/actualizar/', views.reporte_update_view, name='adminhub_reporte_update'),
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
