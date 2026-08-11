from django.db import models


class Usuario(models.Model):
    username = models.CharField(max_length=100)
    run = models.CharField(max_length=12, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Paciente(models.Model):
    terapeuta = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pacientes')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    run = models.CharField(max_length=12, unique=True)
    diagnostico = models.CharField(max_length=150)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class categoriaPauta(models.Model):
    nombre = models.CharField(max_length=100)
    rango_edad = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre


class Pauta(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(categoriaPauta, on_delete=models.CASCADE, related_name='pautas')
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class tipoItemPauta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre


class ItemPauta(models.Model):
    pauta = models.ForeignKey(Pauta, on_delete=models.CASCADE, related_name='items')
    tipo = models.ForeignKey(tipoItemPauta, on_delete=models.CASCADE, related_name='items')
    texto = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.texto


class Evaluacion(models.Model):
    terapeuta = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='evaluaciones_realizadas')
    pauta = models.ForeignKey(Pauta, on_delete=models.CASCADE, related_name='evaluaciones')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True, blank=True, related_name='evaluaciones')
    nombre_participante = models.CharField(max_length=150, blank=True)
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    puntaje_total = models.IntegerField(default=0)
    interpretacion = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[('borrador', 'Borrador'), ('completada', 'Completada')],
        default='borrador'
    )

    def __str__(self):
        if self.paciente:
            return f"Evaluación de {self.paciente} con {self.pauta}"
        return f"Evaluación de {self.nombre_participante or 'participante'} con {self.pauta}"


class RespuestaEvaluacion(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='respuestas')
    item = models.ForeignKey(ItemPauta, on_delete=models.CASCADE, related_name='respuestas')
    respuesta = models.CharField(max_length=100)
    valor = models.IntegerField(default=0)

    class Meta:
        unique_together = ('evaluacion', 'item')

    def __str__(self):
        return f"{self.item} -> {self.respuesta}"