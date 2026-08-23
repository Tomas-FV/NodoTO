from django.db import models

class membresia(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre
class Usuario(models.Model):
    username = models.CharField(max_length=100)
    run = models.CharField(max_length=12, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=[('terapeuta', 'Terapeuta'), ('admin', 'Administrador')], default='terapeuta')
    membresia = models.ForeignKey(membresia, on_delete=models.SET_NULL, null=True, blank=True)

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
    MODO_PUNTUACION_CHOICES = [
        ('general', 'Puntaje general'),
        ('por_campo', 'Puntaje por campo'),
        ('sin_puntaje', 'Sin puntuación'),
    ]
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(categoriaPauta, on_delete=models.CASCADE, related_name='pautas')
    categorias = models.ManyToManyField(categoriaPauta, related_name='pautas_multiples', blank=True)
    descripcion = models.TextField()
    edad_min = models.PositiveIntegerField(null=True, blank=True)
    edad_max = models.PositiveIntegerField(null=True, blank=True)
    modo_puntuacion = models.CharField(max_length=20, choices=MODO_PUNTUACION_CHOICES, default='general')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    def get_version_for_age(self, edad):
        if edad is None:
            return self.versiones.filter(activa=True).order_by('edad_min').first()
        return self.versiones.filter(
            activa=True,
            edad_min__lte=edad,
        ).order_by('-edad_min').filter(
            models.Q(edad_max__isnull=True) | models.Q(edad_max__gte=edad)
        ).order_by('edad_min').first()


class VersionPauta(models.Model):
    MODO_PUNTUACION_CHOICES = [
        ('heredar', 'Usar configuración de la pauta'),
        ('general', 'Puntaje general'),
        ('por_campo', 'Puntaje por campo'),
        ('sin_puntaje', 'Sin puntuación'),
    ]
    pauta = models.ForeignKey(Pauta, on_delete=models.CASCADE, related_name='versiones')
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    edad_min = models.PositiveIntegerField(default=0)
    edad_max = models.PositiveIntegerField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    modo_puntuacion = models.CharField(max_length=20, choices=MODO_PUNTUACION_CHOICES, default='heredar')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['edad_min', 'nombre']

    def __str__(self):
        if self.edad_max is not None:
            return f"{self.pauta} - {self.nombre} ({self.edad_min}-{self.edad_max} años)"
        return f"{self.pauta} - {self.nombre} ({self.edad_min}+ años)"

    def contiene_edad(self, edad):
        if edad is None:
            return self.activa
        if self.edad_max is None:
            return self.activa and edad >= self.edad_min
        return self.activa and self.edad_min <= edad <= self.edad_max


class CampoPauta(models.Model):
    pauta = models.ForeignKey(Pauta, on_delete=models.CASCADE, related_name='campos')
    version = models.ForeignKey(VersionPauta, on_delete=models.CASCADE, related_name='campos', null=True, blank=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'nombre']

    def __str__(self):
        if self.version:
            return f"{self.version} / {self.nombre}"
        return f"{self.pauta} / {self.nombre}"


class TipoRespuesta(models.Model):
    clave = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class tipoItemPauta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre


class ItemPauta(models.Model):
    MODO_PUNTUACION_CHOICES = [
        ('automatico', 'Automático según respuesta'),
        ('sin_puntaje', 'No puntuar este ítem'),
        ('valor_directo', 'Usar el número respondido como puntaje'),
        ('opciones', 'Usar puntajes de las opciones'),
    ]
    pauta = models.ForeignKey(Pauta, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    version = models.ForeignKey(VersionPauta, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    campo = models.ForeignKey(CampoPauta, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    tipo = models.ForeignKey(tipoItemPauta, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    tipo_respuesta = models.ForeignKey(TipoRespuesta, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    texto = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    obligatorio = models.BooleanField(default=True)
    modo_puntuacion = models.CharField(max_length=20, choices=MODO_PUNTUACION_CHOICES, default='automatico')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'texto']

    def __str__(self):
        return self.texto


class OpcionRespuesta(models.Model):
    item = models.ForeignKey(ItemPauta, on_delete=models.CASCADE, related_name='opciones')
    etiqueta = models.CharField(max_length=150)
    valor = models.IntegerField(default=0)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'valor']

    def __str__(self):
        return f"{self.item} - {self.etiqueta} ({self.valor})"

class Evaluacion(models.Model):
    terapeuta = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='evaluaciones_realizadas')
    pauta = models.ForeignKey(Pauta, on_delete=models.CASCADE, related_name='evaluaciones')
    version = models.ForeignKey(VersionPauta, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluaciones')
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


class ReglaTabulacion(models.Model):
    pauta = models.ForeignKey(Pauta, on_delete=models.CASCADE, related_name='reglas_tabulacion')
    version = models.ForeignKey(VersionPauta, on_delete=models.CASCADE, null=True, blank=True, related_name='reglas_tabulacion')
    campo = models.ForeignKey(CampoPauta, on_delete=models.CASCADE, null=True, blank=True, related_name='reglas_tabulacion')
    puntaje_minimo = models.IntegerField()
    puntaje_maximo = models.IntegerField()
    etiqueta = models.CharField(max_length=120)
    interpretacion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'puntaje_minimo']

    def __str__(self):
        return f"{self.etiqueta} ({self.puntaje_minimo}-{self.puntaje_maximo})"


class ResultadoCampo(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='resultados_campos')
    campo = models.ForeignKey(CampoPauta, on_delete=models.SET_NULL, null=True, blank=True, related_name='resultados')
    puntaje_obtenido = models.IntegerField(default=0)
    puntaje_maximo = models.IntegerField(null=True, blank=True)
    porcentaje = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    etiqueta = models.CharField(max_length=120, blank=True)
    interpretacion = models.TextField(blank=True)

    class Meta:
        ordering = ['campo__orden', 'campo__nombre']
        constraints = [
            models.UniqueConstraint(fields=['evaluacion', 'campo'], name='unique_resultado_campo_evaluacion')
        ]

    def __str__(self):
        return f"{self.evaluacion} - {self.campo or 'General'}"