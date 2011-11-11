from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import simplejson

from foundry.models import Page, Tile
from foundry.admin_forms import TileEditAjaxForm

@staff_member_required
def tile_edit_ajax(request, page_id):
    page = get_object_or_404(Page, id=int(page_id))
    instance = None
    tile_id = request.REQUEST.get('tile_id')
    column = request.REQUEST.get('column')
    if tile_id:
        instance = get_object_or_404(Tile, id=int(tile_id))
    if request.method == 'POST':
        form = TileEditAjaxForm(
            request.POST, instance=instance, page=page, column=int(column)
        ) 
        if form.is_valid():
            tile = form.save()
            di = dict(
                status='success', 
                id=tile.id, 
                view_name=tile.view_name,
                width=tile.width,
            )
            return HttpResponse(simplejson.dumps(di))
    else:
        form = TileEditAjaxForm(
            instance=instance, page=page, column=int(column)
        ) 

    extra = dict(form=form)
    return render_to_response('admin/foundry/page/tile_edit_ajax.html', extra, context_instance=RequestContext(request))
