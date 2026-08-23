from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from core.models import Pauta, Usuario, Evaluacion, RespuestaEvaluacion, ResultadoCampo, ReglaTabulacion


def home_view(request):
    return render(request, 'index.html')


def pautas_view(request):
    pautas = Pauta.objects.prefetch_related('versiones', 'campos__items__opciones').all()
    resultado = None
    resultado_id = request.session.pop('resultado_evaluacion_id', None)
    if resultado_id:
        resultado = Evaluacion.objects.select_related('pauta', 'version').prefetch_related(
            'resultados_campos__campo'
        ).filter(id=resultado_id).first()
    resultado_modo = _modo_puntuacion(resultado.pauta, resultado.version) if resultado else None
    return render(request, 'pautas.html', {
        'pautas': pautas,
        'resultado': resultado,
        'resultado_modo': resultado_modo,
    })


def _modo_puntuacion(pauta, version):
    if version and version.modo_puntuacion != 'heredar':
        return version.modo_puntuacion
    return pauta.modo_puntuacion


def _regla_para_resultado(pauta, version, campo, puntaje):
    reglas = ReglaTabulacion.objects.filter(pauta=pauta, puntaje_minimo__lte=puntaje, puntaje_maximo__gte=puntaje)
    reglas = reglas.filter(Q(version=version) | Q(version__isnull=True))
    reglas = reglas.filter(Q(campo=campo) | Q(campo__isnull=True)).order_by('-campo', '-version', 'orden')
    return reglas.first()


def _puntaje_maximo_item(item):
    if item.modo_puntuacion == 'sin_puntaje':
        return 0
    if item.tipo_respuesta and item.tipo_respuesta.clave in {'checkbox', 'escala_4'}:
        return sum(item.opciones.values_list('valor', flat=True))
    return None


def evaluar_pauta_view(request, pauta_id):
    pauta = get_object_or_404(Pauta.objects.prefetch_related('versiones', 'campos__items__opciones'), id=pauta_id)
    edad = request.POST.get('edad')
    try:
        edad = int(edad) if edad not in (None, '') else None
    except ValueError:
        edad = None

    version_id = request.POST.get('version_id')
    version = None

    if version_id:
        version = pauta.versiones.filter(id=version_id).first()
    elif pauta.versiones.exists():
        version = pauta.get_version_for_age(edad) if edad is not None else None

    campos = pauta.campos.filter(Q(version__isnull=True) | Q(version=version)).distinct() if version else pauta.campos.filter(version__isnull=True)
    items = pauta.items.filter(Q(version__isnull=True) | Q(version=version)).distinct() if version else pauta.items.filter(version__isnull=True)

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

    for item in items:
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
            if item.modo_puntuacion == 'sin_puntaje':
                valor = 0
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
            if item.modo_puntuacion == 'sin_puntaje':
                valor = 0
            respuestas_a_guardar.append((item, str(valor), valor))
            continue

        try:
            opcion_id = int(valor_enviado)
        except (TypeError, ValueError):
            errores_validacion.append(f'El ítem "{item.texto}" requiere una opción válida seleccionada.')
            continue

        opcion = item.opciones.filter(id=opcion_id).first()
        if opcion is not None:
            valor = opcion.valor if item.modo_puntuacion != 'sin_puntaje' else 0
            respuestas_a_guardar.append((item, opcion.etiqueta, valor))
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
        version=version,
        nombre_participante=nombre_participante,
        observaciones=observaciones,
        estado='completada',
        fecha_completado=timezone.now(),
    )

    puntaje_total = 0
    puntajes_por_campo = {}
    maximos_por_campo = {}
    for item, respuesta_texto, valor in respuestas_a_guardar:
        RespuestaEvaluacion.objects.create(
            evaluacion=evaluacion,
            item=item,
            respuesta=respuesta_texto,
            valor=valor,
        )
        puntaje_total += valor
        campo_id = item.campo_id
        puntajes_por_campo[campo_id] = puntajes_por_campo.get(campo_id, 0) + valor
        maximo = _puntaje_maximo_item(item)
        if maximo is not None:
            maximos_por_campo[campo_id] = maximos_por_campo.get(campo_id, 0) + maximo

    for campo in campos:
        puntaje = puntajes_por_campo.get(campo.id, 0)
        maximo = maximos_por_campo.get(campo.id)
        porcentaje = (puntaje * 100 / maximo) if maximo else None
        regla = _regla_para_resultado(pauta, version, campo, puntaje)
        ResultadoCampo.objects.create(
            evaluacion=evaluacion,
            campo=campo,
            puntaje_obtenido=puntaje,
            puntaje_maximo=maximo,
            porcentaje=porcentaje,
            etiqueta=regla.etiqueta if regla else '',
            interpretacion=regla.interpretacion if regla else '',
        )

    evaluacion.puntaje_total = puntaje_total
    if _modo_puntuacion(pauta, version) == 'sin_puntaje':
        puntaje_total = 0
    evaluacion.puntaje_total = puntaje_total
    evaluacion.save(update_fields=['puntaje_total'])

    messages.success(request, f'Evaluación realizada correctamente para {pauta.nombre}.')
    request.session['resultado_evaluacion_id'] = evaluacion.id
    request.session.modified = True
    return redirect(reverse('pautas'))


def sobrenodoto_view(request):
    return render(request, 'sobrenodoto.html')