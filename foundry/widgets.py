import types
import datetime

from django.forms.widgets import CheckboxSelectMultiple, MultiWidget, Select
from django.utils.datastructures import MultiValueDict

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
