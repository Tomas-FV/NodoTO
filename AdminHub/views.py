from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Pauta, CampoPauta, ItemPauta, OpcionRespuesta, TipoRespuesta, categoriaPauta
from .forms import PautaForm, CampoPautaForm, ItemPautaForm, OpcionRespuestaForm


def ensure_default_tipos_respuesta():
    defaults = [
        ('checkbox', 'Checkbox', 'Selección múltiple'),
        ('texto', 'Texto', 'Respuesta libre en texto'),
        ('numero', 'Número', 'Respuesta numérica'),
        ('escala_4', 'Escala 4', 'Escala de 4 niveles'),
    ]
    for clave, nombre, descripcion in defaults:
        TipoRespuesta.objects.get_or_create(
            clave=clave,
            defaults={'nombre': nombre, 'descripcion': descripcion}
        )


def sync_item_response_schema(item):
    tipo = getattr(item.tipo_respuesta, 'clave', None)

    if tipo == 'escala_4':
        defaults = [
            ('Nunca', 1, 1),
            ('A veces', 2, 2),
            ('Frecuentemente', 3, 3),
            ('Siempre', 4, 4),
        ]
        for etiqueta, valor, orden in defaults:
            opcion, created = OpcionRespuesta.objects.get_or_create(
                item=item,
                etiqueta=etiqueta,
                defaults={'valor': valor, 'orden': orden}
            )
            if not created:
                opcion.valor = valor
                opcion.orden = orden
                opcion.save(update_fields=['valor', 'orden'])
        return

    if tipo not in {'checkbox', 'escala_4'}:
        item.opciones.all().delete()


def dashboard_view(request):
    pautas = Pauta.objects.prefetch_related('campos__items__opciones').all()
    total_pautas = pautas.count()
    total_campos = CampoPauta.objects.count()
    total_items = ItemPauta.objects.count()
    total_opciones = OpcionRespuesta.objects.count()

    context = {
        'pautas': pautas,
        'categorias': categoriaPauta.objects.order_by('nombre'),
        'total_pautas': total_pautas,
        'total_campos': total_campos,
        'total_items': total_items,
        'total_opciones': total_opciones,
        'pauta_form': PautaForm(),
    }
    return render(request, 'dashboard.html', context)


def pauta_list_view(request):
    pautas = Pauta.objects.prefetch_related('campos__items__opciones').all()
    return render(request, 'pauta_list.html', {
        'pautas': pautas,
        'categorias': categoriaPauta.objects.order_by('nombre'),
        'pauta_form': PautaForm(),
    })


def pauta_detail_view(request, pauta_id):
    ensure_default_tipos_respuesta()
    pauta = Pauta.objects.prefetch_related('campos__items__opciones').get(id=pauta_id)
    return render(request, 'pauta_detail.html', {
        'pauta': pauta,
        'campo_form': CampoPautaForm(),
        'tipos_respuesta': TipoRespuesta.objects.exclude(clave='radio'),
    })


def pauta_create_view(request):
    if request.method == 'POST':
        categoria_nombre = (request.POST.get('categoria') or '').strip()
        if not categoria_nombre:
            categoria_nombre = (request.POST.get('categoria_nueva') or '').strip()

        if categoria_nombre:
            request.POST = request.POST.copy()
            request.POST['categoria'] = categoria_nombre

        form = PautaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pauta creada correctamente.')
            return redirect('adminhub_pautas')

        messages.error(request, 'No se pudo crear la pauta. Revisa los campos.')
        return redirect('adminhub_pautas')

    return redirect('adminhub_pautas')


def pauta_edit_view(request, pauta_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    if request.method == 'POST':
        categoria_nombre = (request.POST.get('categoria') or '').strip()
        if not categoria_nombre:
            categoria_nombre = (request.POST.get('categoria_nueva') or '').strip()

        if categoria_nombre:
            request.POST = request.POST.copy()
            request.POST['categoria'] = categoria_nombre

        form = PautaForm(request.POST, instance=pauta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pauta actualizada correctamente.')
            return redirect('adminhub_pautas')

        messages.error(request, 'No se pudo actualizar la pauta. Revisa los campos.')
        return redirect('adminhub_pautas')

    return redirect('adminhub_pautas')


def pauta_delete_view(request, pauta_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    if request.method == 'POST':
        pauta.delete()
        messages.success(request, 'Pauta eliminada correctamente.')
    return redirect('adminhub_pautas')


def campo_create_view(request, pauta_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    if request.method == 'POST':
        form = CampoPautaForm(request.POST)
        if form.is_valid():
            campo = form.save(commit=False)
            campo.pauta = pauta
            campo.save()
            messages.success(request, 'Campo creado correctamente.')
        else:
            messages.error(request, 'No se pudo crear el campo.')
    return redirect('adminhub_pauta_detail', pauta_id=pauta.id)


def campo_edit_view(request, pauta_id, campo_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    campo = get_object_or_404(CampoPauta, id=campo_id, pauta=pauta)
    if request.method == 'POST':
        form = CampoPautaForm(request.POST, instance=campo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campo actualizado correctamente.')
        else:
            messages.error(request, 'No se pudo actualizar el campo.')
    return redirect('adminhub_pauta_detail', pauta_id=pauta.id)


def campo_delete_view(request, pauta_id, campo_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    campo = get_object_or_404(CampoPauta, id=campo_id, pauta=pauta)
    if request.method == 'POST':
        campo.delete()
        messages.success(request, 'Campo eliminado correctamente.')
    return redirect('adminhub_pauta_detail', pauta_id=pauta.id)


def item_create_view(request, pauta_id, campo_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    campo = get_object_or_404(CampoPauta, id=campo_id, pauta=pauta)
    if request.method == 'POST':
        form = ItemPautaForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.pauta = pauta
            item.campo = campo
            item.save()
            sync_item_response_schema(item)
            messages.success(request, 'Ítem creado correctamente.')
        else:
            messages.error(request, 'No se pudo crear el ítem.')
    return redirect('adminhub_pauta_detail', pauta_id=pauta.id)


def item_edit_view(request, pauta_id, campo_id, item_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    campo = get_object_or_404(CampoPauta, id=campo_id, pauta=pauta)
    item = get_object_or_404(ItemPauta, id=item_id, campo=campo, pauta=pauta)
    if request.method == 'POST':
        form = ItemPautaForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            sync_item_response_schema(item)
            messages.success(request, 'Ítem actualizado correctamente.')
        else:
            messages.error(request, 'No se pudo actualizar el ítem.')
    return redirect('adminhub_pauta_detail', pauta_id=pauta.id)


def item_delete_view(request, pauta_id, campo_id, item_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    campo = get_object_or_404(CampoPauta, id=campo_id, pauta=pauta)
    item = get_object_or_404(ItemPauta, id=item_id, campo=campo, pauta=pauta)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Ítem eliminado correctamente.')
    return redirect('adminhub_pauta_detail', pauta_id=pauta.id)


def opcion_create_view(request, pauta_id, campo_id, item_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    campo = get_object_or_404(CampoPauta, id=campo_id, pauta=pauta)
    item = get_object_or_404(ItemPauta, id=item_id, campo=campo, pauta=pauta)
    if request.method == 'POST':
        tipo_actual = getattr(item.tipo_respuesta, 'clave', None)
        if tipo_actual not in {'checkbox', 'escala_4'}:
            messages.error(request, 'Este tipo de respuesta no admite opciones. Solo se permite para checkbox y escala 4.')
            return redirect('adminhub_pauta_detail', pauta_id=pauta.id)

        form = OpcionRespuestaForm(request.POST)
        if form.is_valid():
            opcion = form.save(commit=False)
            opcion.item = item
            opcion.save()
            messages.success(request, 'Opción creada correctamente.')
        else:
            messages.error(request, 'No se pudo crear la opción.')
    return redirect('adminhub_pauta_detail', pauta_id=pauta.id)


def opcion_edit_view(request, pauta_id, campo_id, item_id, opcion_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    campo = get_object_or_404(CampoPauta, id=campo_id, pauta=pauta)
    item = get_object_or_404(ItemPauta, id=item_id, campo=campo, pauta=pauta)
    opcion = get_object_or_404(OpcionRespuesta, id=opcion_id, item=item)
    if request.method == 'POST':
        form = OpcionRespuestaForm(request.POST, instance=opcion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Opción actualizada correctamente.')
        else:
            messages.error(request, 'No se pudo actualizar la opción.')
    return redirect('adminhub_pauta_detail', pauta_id=pauta.id)


def opcion_delete_view(request, pauta_id, campo_id, item_id, opcion_id):
    pauta = get_object_or_404(Pauta, id=pauta_id)
    campo = get_object_or_404(CampoPauta, id=campo_id, pauta=pauta)
    item = get_object_or_404(ItemPauta, id=item_id, campo=campo, pauta=pauta)
    opcion = get_object_or_404(OpcionRespuesta, id=opcion_id, item=item)
    if request.method == 'POST':
        opcion.delete()
        messages.success(request, 'Opción eliminada correctamente.')
    return redirect('adminhub_pauta_detail', pauta_id=pauta.id)
