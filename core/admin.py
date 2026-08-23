from django.contrib import admin
from .models import (
    Usuario,
    Paciente,
    categoriaPauta,
    Pauta,
    VersionPauta,
    CampoPauta,
    TipoRespuesta,
    tipoItemPauta,
    ItemPauta,
    OpcionRespuesta,
    Evaluacion,
    RespuestaEvaluacion,
    ReglaTabulacion,
    ResultadoCampo,
    membresia,
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'membresia')
    list_filter = ('rol', 'membresia')
    search_fields = ('username', 'email', 'run')


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'run', 'telefono', 'terapeuta')
    search_fields = ('nombre', 'apellido', 'run')
    list_filter = ('terapeuta',)


@admin.register(categoriaPauta)
class CategoriaPautaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rango_edad')
    search_fields = ('nombre', 'rango_edad', 'descripcion')


@admin.register(Pauta)
class PautaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'modo_puntuacion', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'categoria__nombre')
    list_filter = ('categoria',)
    ordering = ('-fecha_creacion',)


@admin.register(VersionPauta)
class VersionPautaAdmin(admin.ModelAdmin):
    list_display = ('pauta', 'nombre', 'edad_min', 'edad_max', 'modo_puntuacion', 'activa')
    search_fields = ('pauta__nombre', 'nombre', 'descripcion')
    list_filter = ('pauta', 'activa')
    ordering = ('pauta__nombre', 'edad_min')


@admin.register(CampoPauta)
class CampoPautaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pauta', 'orden')
    search_fields = ('nombre', 'pauta__nombre')
    list_filter = ('pauta',)


@admin.register(TipoRespuesta)
class TipoRespuestaAdmin(admin.ModelAdmin):
    list_display = ('clave', 'nombre')
    search_fields = ('clave', 'nombre', 'descripcion')


@admin.register(tipoItemPauta)
class TipoItemPautaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre', 'descripcion')


@admin.register(ItemPauta)
class ItemPautaAdmin(admin.ModelAdmin):
    list_display = ('texto', 'pauta', 'campo', 'tipo_respuesta', 'modo_puntuacion', 'obligatorio', 'orden')
    search_fields = ('texto', 'descripcion', 'pauta__nombre', 'campo__nombre')
    list_filter = ('pauta', 'campo', 'tipo_respuesta', 'obligatorio')


@admin.register(OpcionRespuesta)
class OpcionRespuestaAdmin(admin.ModelAdmin):
    list_display = ('item', 'etiqueta', 'valor', 'orden')
    search_fields = ('etiqueta', 'item__texto')
    list_filter = ('item__pauta', 'item__campo')


@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ('nombre_participante', 'pauta', 'version', 'terapeuta', 'estado', 'puntaje_total', 'fecha_completado')
    search_fields = ('nombre_participante', 'pauta__nombre', 'terapeuta__username')
    list_filter = ('estado', 'pauta', 'terapeuta')


@admin.register(RespuestaEvaluacion)
class RespuestaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('evaluacion', 'item', 'respuesta', 'valor')
    search_fields = ('respuesta', 'item__texto')
    list_filter = ('evaluacion__pauta', 'item')


@admin.register(ReglaTabulacion)
class ReglaTabulacionAdmin(admin.ModelAdmin):
    list_display = ('pauta', 'version', 'campo', 'puntaje_minimo', 'puntaje_maximo', 'etiqueta', 'orden')
    search_fields = ('pauta__nombre', 'etiqueta', 'interpretacion')
    list_filter = ('pauta', 'version', 'campo')


@admin.register(ResultadoCampo)
class ResultadoCampoAdmin(admin.ModelAdmin):
    list_display = ('evaluacion', 'campo', 'puntaje_obtenido', 'puntaje_maximo', 'porcentaje', 'etiqueta')
    search_fields = ('evaluacion__nombre_participante', 'campo__nombre', 'etiqueta')
    list_filter = ('evaluacion__pauta', 'campo', 'etiqueta')


@admin.register(membresia)
class MembresiaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')
    search_fields = ('nombre',)