from django import forms
from core.models import Pauta, categoriaPauta, CampoPauta, ItemPauta, OpcionRespuesta, TipoRespuesta, VersionPauta, ReglaTabulacion


class VersionPautaForm(forms.ModelForm):
    class Meta:
        model = VersionPauta
        fields = ['nombre', 'descripcion', 'edad_min', 'edad_max', 'activa', 'modo_puntuacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3 a 5 años'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la versión...'}),
            'edad_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'edad_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'modo_puntuacion': forms.Select(attrs={'class': 'form-select'}),
        }


class PautaForm(forms.ModelForm):
    categorias = forms.ModelMultipleChoiceField(
        queryset=categoriaPauta.objects.none(),
        required=True,
        label='Categorías',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 4})
    )

    class Meta:
        model = Pauta
        fields = ['nombre', 'categorias', 'descripcion', 'edad_min', 'edad_max', 'modo_puntuacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: SPM-2'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción de la pauta...'}),
            'modo_puntuacion': forms.Select(attrs={'class': 'form-select'}),
            'edad_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Opcional'}),
            'edad_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Opcional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorias'].queryset = categoriaPauta.objects.order_by('nombre')
        if self.instance and self.instance.pk:
            categorias = self.instance.categorias.all()
            if not categorias.exists() and self.instance.categoria_id:
                categorias = categoriaPauta.objects.filter(pk=self.instance.categoria_id)
            self.initial['categorias'] = categorias

    def clean(self):
        cleaned_data = super().clean()
        edad_min = cleaned_data.get('edad_min')
        edad_max = cleaned_data.get('edad_max')
        if edad_min is not None and edad_max is not None and edad_min > edad_max:
            raise forms.ValidationError('La edad mínima no puede ser mayor que la edad máxima.')
        if not cleaned_data.get('categorias'):
            self.add_error('categorias', 'Selecciona al menos una categoría.')
        return cleaned_data

    def save(self, commit=True):
        pauta = super().save(commit=False)
        categorias = self.cleaned_data.get('categorias')
        pauta.categoria = categorias.first()
        if commit:
            pauta.save()
            pauta.categorias.set(categorias)
        return pauta


class CampoPautaForm(forms.ModelForm):
    version = forms.ModelChoiceField(
        queryset=VersionPauta.objects.none(),
        required=False,
        empty_label='Sin versión específica (pauta base)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CampoPauta
        fields = ['nombre', 'descripcion', 'orden', 'version']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Actividades de la vida diaria'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe este bloque o sección de la pauta...'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class ItemPautaForm(forms.ModelForm):
    tipo_respuesta = forms.ModelChoiceField(
        queryset=TipoRespuesta.objects.exclude(clave='radio'),
        required=False,
        empty_label='Sin tipo de respuesta',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    version = forms.ModelChoiceField(
        queryset=VersionPauta.objects.none(),
        required=False,
        empty_label='Sin versión específica (pauta base)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = ItemPauta
        fields = ['texto', 'tipo_respuesta', 'descripcion', 'orden', 'obligatorio', 'version', 'modo_puntuacion']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej: ¿El paciente logra completar la tarea de forma independiente?'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Detalles adicionales del ítem'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'modo_puntuacion': forms.Select(attrs={'class': 'form-select'}),
        }


class OpcionRespuestaForm(forms.ModelForm):
    class Meta:
        model = OpcionRespuesta
        fields = ['etiqueta', 'valor', 'orden']
        widgets = {
            'etiqueta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Siempre'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class ReglaTabulacionForm(forms.ModelForm):
    version = forms.ModelChoiceField(queryset=VersionPauta.objects.none(), required=False, empty_label='Todas las versiones')
    campo = forms.ModelChoiceField(queryset=CampoPauta.objects.none(), required=False, empty_label='Resultado general')

    class Meta:
        model = ReglaTabulacion
        fields = ['version', 'campo', 'puntaje_minimo', 'puntaje_maximo', 'etiqueta', 'interpretacion', 'orden']
        widgets = {
            'version': forms.Select(attrs={'class': 'form-select'}),
            'campo': forms.Select(attrs={'class': 'form-select'}),
            'puntaje_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'puntaje_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
            'etiqueta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Riesgo moderado'}),
            'interpretacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
