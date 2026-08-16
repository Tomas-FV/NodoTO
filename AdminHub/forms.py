from django import forms
from core.models import Pauta, categoriaPauta, CampoPauta, ItemPauta, OpcionRespuesta, TipoRespuesta


class PautaForm(forms.ModelForm):
    categoria = forms.CharField(
        max_length=100,
        required=True,
        label='Categoría',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Infanto-juvenil'})
    )

    class Meta:
        model = Pauta
        fields = ['nombre', 'categoria', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: SPM-2'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción de la pauta...'}),
        }

    def clean_categoria(self):
        nombre = (self.cleaned_data.get('categoria') or '').strip()
        if not nombre:
            raise forms.ValidationError('La categoría es obligatoria.')

        categoria_obj, _ = categoriaPauta.objects.get_or_create(
            nombre=nombre,
            defaults={
                'rango_edad': 'General',
                'descripcion': 'Categoría creada desde el panel administrativo.'
            }
        )
        return categoria_obj

    def save(self, commit=True):
        pauta = super().save(commit=False)
        categoria_obj = self.cleaned_data.get('categoria')
        if categoria_obj is not None and not isinstance(categoria_obj, categoriaPauta):
            categoria_obj = categoriaPauta.objects.get_or_create(
                nombre=str(categoria_obj),
                defaults={
                    'rango_edad': 'General',
                    'descripcion': 'Categoría creada desde el panel administrativo.'
                }
            )[0]
        pauta.categoria = categoria_obj
        if commit:
            pauta.save()
        return pauta


class CampoPautaForm(forms.ModelForm):
    class Meta:
        model = CampoPauta
        fields = ['nombre', 'descripcion', 'orden']
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

    class Meta:
        model = ItemPauta
        fields = ['texto', 'tipo_respuesta', 'descripcion', 'orden', 'obligatorio']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej: ¿El paciente logra completar la tarea de forma independiente?'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Detalles adicionales del ítem'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
