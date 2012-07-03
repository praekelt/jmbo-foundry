from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.db.models import get_model
from django.contrib import messages

from foundry.models import Page, Row, Column, Tile, FoundryComment
from foundry.admin_forms import RowEditAjaxForm, ColumnCreateAjaxForm, \
    ColumnEditAjaxForm, TileEditAjaxForm


@staff_member_required
def row_create_ajax(request):
    row = Row(page_id=int(request.REQUEST['page_id']))
    row.save()
    di = dict(
        id=row.id,
        page_render_height=row.page.render_height,
        block_name=row.block_name
    )
    return HttpResponse(simplejson.dumps(di))


@staff_member_required
def row_edit_ajax(request):
    instance = get_object_or_404(Row, id=int(request.REQUEST.get('row_id')))
    if request.method == 'POST':
        form = RowEditAjaxForm(request.POST, instance=instance)      
        if form.is_valid():
            row = form.save()
            di = dict(
                id=row.id, 
                block_name=row.block_name,
            )
            return HttpResponse(simplejson.dumps(di))
    else:
        form = RowEditAjaxForm(instance=instance) 

    extra = dict(form=form)
    return render_to_response(
        'admin/foundry/page/row_edit_ajax.html', 
        extra, 
        context_instance=RequestContext(request)
    )


@staff_member_required
def row_delete_ajax(request):
    row_id = request.REQUEST.get('row_id')
    row = get_object_or_404(Row, id=int(row_id))
    row.delete()
    di = dict(
        status='success', 
    )
    return HttpResponse(simplejson.dumps(di))


@staff_member_required
def column_create_ajax(request):
    if request.method == 'POST':
        form = ColumnCreateAjaxForm(request.POST)
        if form.is_valid():
            column = form.save()
            di = dict(
                id=column.id, 
                width=column.width,
                title=column.title,
                row_id=column.row.id,
                row_render_height=column.row.render_height,
                page_render_height=column.row.page.render_height
            )
            return HttpResponse(simplejson.dumps(di))
    else:
        form = ColumnCreateAjaxForm(initial={'row':int(request.GET['row_id'])})

    extra = dict(form=form)
    return render_to_response(
        'admin/foundry/page/column_create_ajax.html', 
        extra, 
        context_instance=RequestContext(request)
    )


@staff_member_required
def column_edit_ajax(request):
    instance = get_object_or_404(Column, id=int(request.REQUEST.get('column_id')))
    if request.method == 'POST':
        form = ColumnEditAjaxForm(request.POST, instance=instance)      
        if form.is_valid():
            column = form.save()
            di = dict(
                id=column.id, 
                width=column.width,
                title=column.title,
            )
            return HttpResponse(simplejson.dumps(di))
    else:
        form = ColumnEditAjaxForm(instance=instance) 

    extra = dict(form=form)
    return render_to_response(
        'admin/foundry/page/column_edit_ajax.html', 
        extra, 
        context_instance=RequestContext(request)
    )


@staff_member_required
def column_delete_ajax(request):
    column_id = request.REQUEST.get('column_id')
    column = get_object_or_404(Column, id=int(column_id))
    column.delete()
    di = dict(
        status='success', 
    )
    return HttpResponse(simplejson.dumps(di))


@staff_member_required
def tile_create_ajax(request):
    tile = Tile(column_id=request.REQUEST['column_id'])
    tile.save()
    di = dict(
        id=tile.id, 
        column_id=tile.column.id,
        column_render_height=tile.column.render_height,
        row_id=tile.column.row.id,
        row_render_height=tile.column.row.render_height,
        page_render_height=tile.column.row.page.render_height
    )
    return HttpResponse(simplejson.dumps(di))


@staff_member_required
def tile_edit_ajax(request):
    instance = get_object_or_404(Tile, id=int(request.REQUEST.get('tile_id')))
    if request.method == 'POST':
        form = TileEditAjaxForm(request.POST, instance=instance) 
        if form.is_valid():
            tile = form.save()
            di = dict(
                id=tile.id,
                label=tile.label
            )
            return HttpResponse(simplejson.dumps(di))
    else:
        form = TileEditAjaxForm(instance=instance)

    extra = dict(form=form)
    return render_to_response(
        'admin/foundry/page/tile_edit_ajax.html', 
        extra, 
        context_instance=RequestContext(request)
    )


@staff_member_required
def tile_delete_ajax(request):
    tile_id = request.REQUEST.get('tile_id')
    tile = get_object_or_404(Tile, id=int(tile_id))
    tile.delete()
    di = dict(
        status='success', 
    )
    return HttpResponse(simplejson.dumps(di))


@staff_member_required
def persist_sort_ajax(request):
    # Yes, I am aware this code can be more efficient, but it does not execute 
    # regularly.
    model_name = request.REQUEST['model_name']
    model = get_model('foundry', model_name)
    obj = model.objects.get(id=int(request.REQUEST['id']))
    if model_name == 'row':
        objs = [o for o in obj.page.rows]
    elif model_name == 'column':
        objs = [o for o in obj.row.columns]
    elif model_name == 'tile':
        objs = [o for o in obj.column.tiles]
    objs.insert(int(request.REQUEST['index']), objs.pop(objs.index(obj)))
    for n, obj in enumerate(objs):
        obj.index = n
        obj.save()
    return HttpResponse('')


@staff_member_required
def remove_comment(request, comment_id):
    obj = get_object_or_404(FoundryComment, id=comment_id)
    obj.is_removed = True
    obj.moderated = True
    obj.save()
    msg = "The comment has been removed"
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect('/admin')


@staff_member_required
def allow_comment(request, comment_id):
    obj = get_object_or_404(FoundryComment, id=comment_id)
    obj.is_removed = False
    obj.moderated = True
    obj.save()
    msg = "The comment has been allowed"
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect('/admin')
