from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from core.models import Pauta, Usuario, Evaluacion, RespuestaEvaluacion


def home_view(request):
    return render(request, 'index.html')


def pautas_view(request):
    pautas = Pauta.objects.prefetch_related('campos__items__opciones').all()
    return render(request, 'pautas.html', {'pautas': pautas})


def evaluar_pauta_view(request, pauta_id):
    pauta = get_object_or_404(Pauta.objects.prefetch_related('campos__items__opciones'), id=pauta_id)

    if request.method != 'POST':
        return redirect('pautas')

    nombre_participante = request.POST.get('nombre_participante', '').strip() or 'Participante sin nombre'
    observaciones = request.POST.get('observaciones', '').strip()

    terapeuta = Usuario.objects.order_by('id').first()
    if terapeuta is None:
        terapeuta = Usuario.objects.create(
            username='terapeuta_default',
            run='11111111-1',
            email='terapeuta@nodoto.local',
            password='nodoto123',
            rol='terapeuta',
        )

    respuestas_a_guardar = []
    errores_validacion = []

    for item in pauta.items.all():
        tipo_clave = getattr(getattr(item, 'tipo_respuesta', None), 'clave', None)
        valores_enviados = request.POST.getlist(f'item_{item.id}')

        if not valores_enviados:
            continue

        if tipo_clave == 'checkbox':
            try:
                ids_validos = [int(valor) for valor in valores_enviados]
            except (TypeError, ValueError):
                errores_validacion.append(f'El ítem "{item.texto}" tiene valores de opción inválidos.')
                continue

            opciones_seleccionadas = item.opciones.filter(id__in=ids_validos)
            if not opciones_seleccionadas.exists():
                errores_validacion.append(f'El ítem "{item.texto}" no tiene opciones válidas seleccionadas.')
                continue

            etiquetas = list(opciones_seleccionadas.order_by('orden', 'valor').values_list('etiqueta', flat=True))
            valor = sum(opciones_seleccionadas.values_list('valor', flat=True))
            respuesta_texto = ', '.join(etiquetas) if etiquetas else ', '.join(map(str, ids_validos))
            respuestas_a_guardar.append((item, respuesta_texto, valor))
            continue

        valor_enviado = valores_enviados[0].strip()
        if not valor_enviado:
            continue

        if tipo_clave == 'texto':
            respuestas_a_guardar.append((item, valor_enviado, 0))
            continue

        if tipo_clave == 'numero':
            try:
                valor = int(valor_enviado)
            except (TypeError, ValueError):
                errores_validacion.append(f'El ítem "{item.texto}" debe contener un número válido.')
                continue
            respuestas_a_guardar.append((item, str(valor), valor))
            continue

        try:
            opcion_id = int(valor_enviado)
        except (TypeError, ValueError):
            errores_validacion.append(f'El ítem "{item.texto}" requiere una opción válida seleccionada.')
            continue

        opcion = item.opciones.filter(id=opcion_id).first()
        if opcion is not None:
            respuestas_a_guardar.append((item, opcion.etiqueta, opcion.valor))
            continue

        respuestas_a_guardar.append((item, valor_enviado, 0))

    if errores_validacion:
        pautas = Pauta.objects.prefetch_related('campos__items__opciones').all()
        return render(request, 'pautas.html', {
            'pautas': pautas,
            'modal_error_pauta_id': pauta.id,
            'modal_error_messages': errores_validacion,
        })

    evaluacion = Evaluacion.objects.create(
        terapeuta=terapeuta,
        pauta=pauta,
        nombre_participante=nombre_participante,
        observaciones=observaciones,
        estado='completada',
        fecha_completado=timezone.now(),
    )

    puntaje_total = 0
    for item, respuesta_texto, valor in respuestas_a_guardar:
        RespuestaEvaluacion.objects.create(
            evaluacion=evaluacion,
            item=item,
            respuesta=respuesta_texto,
            valor=valor,
        )
        puntaje_total += valor

    evaluacion.puntaje_total = puntaje_total
    evaluacion.save(update_fields=['puntaje_total'])

    messages.success(request, f'Evaluación realizada correctamente para {pauta.nombre}.')
    return redirect('pautas')


def sobrenodoto_view(request):
    return render(request, 'sobrenodoto.html')