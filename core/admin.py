from django.contrib import admin
from .models import Usuario, Paciente, Pauta, ItemPauta, Evaluacion

admin.site.register(Usuario)
admin.site.register(Paciente)
admin.site.register(Pauta)
admin.site.register(ItemPauta)
admin.site.register(Evaluacion)