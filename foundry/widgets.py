import types
import datetime
import re

from django.forms.widgets import CheckboxSelectMultiple, MultiWidget, Select, \
    HiddenInput
from django.utils.datastructures import MultiValueDict
from django.utils import simplejson as json

class SelectCommaWidget(CheckboxSelectMultiple):

    def render(self, name, value, attrs=None, choices=()):        
        if not isinstance(value, types.ListType):
            value = value.split(',')
        return super(SelectCommaWidget, self).render(name, value, attrs=attrs, choices=choices)

    def value_from_datadict(self, data, files, name):
        result = super(SelectCommaWidget, self).value_from_datadict(
            data, files, name
        )
        if isinstance(result, types.ListType):
            return ','.join(result)
        return result


class OldSchoolDateWidget(MultiWidget):
    """Date picker that should work on limited browsers"""

    def __init__(self, attrs=None):
        widgets = (
            Select(choices=([('', 'Day'),] + [(i,i) for i in range(1, 32)])),
            Select(choices=([('', 'Month'),] + [(i,i) for i in range(1, 13)])),
            Select(choices=([('', 'Year'),] + [(i,i) for i in reversed(range(datetime.datetime.now().year - 100, datetime.datetime.now().year - 4))])),
        )
        super(OldSchoolDateWidget, self).__init__(widgets, attrs)

    def value_from_datadict(self, data, files, name):
        d, m, y = super(OldSchoolDateWidget, self).value_from_datadict(data, files, name)
        try:
            return datetime.date(int(y), int(m), int(d))
        except ValueError:
            return None

    def decompress(self, value):
        if value is not None:
            return [value.day, value.month, value.year]
        return ['', '', '']


class DragDropOrderingWidget(MultiWidget):
    """Allows fields to be dragged and dropped to arrange their order"""
    script = '''<script type="text/javascript">
        $(document).ready(function() {
            var input_el = $("#%s");
            var list_el = input_el.next("ul.dragdrop");
            list_el.dragsort({dragSelector: "span",
                dragEnd: function() {
                    var new_order = "{";
                    list_el.children("li").each(function(index, el) {
                        new_order += '"' + el.getAttribute("name") + '": ' + index + ','; 
                    });
                    input_el.val(new_order.substr(0, new_order.length - 1) + "}");
                },
                placeHolderTemplate: "<li></li>"});
        });
    </script>'''

    class Media:
        css = {
            'all': ('admin/css/dragdrop.css',)
        }
        js = ('admin/thirdparty/jquery.dragsort-0.5.1.min.js', )

    def __init__(self, attrs=None):
        _widgets = (
            HiddenInput,
        )
        super(DragDropOrderingWidget, self).__init__(_widgets, attrs)

    def value_from_datadict(self, data, files, name):
        return super(DragDropOrderingWidget, self).value_from_datadict(data, files, name)[0]

    def decompress(self, value):
        if isinstance(value, (list, tuple)):
            self.key_order = json.loads(value[0])
            return value
        self.key_order = json.loads(value)
        return [value]
    
    def format_output(self, rendered_widgets):
        para = ""
        for f in sorted(self.key_order, key=lambda key: self.key_order[key]):
            para += '''<li name="%s"><span>%s</span></li>''' % (f, f)
        return u'''%s<ul class="dragdrop">%s</ul>%s''' % (rendered_widgets[0], para,
            DragDropOrderingWidget.script % (re.search(r'id="(?P<id>\w+)"', rendered_widgets[0]).group('id')))
        