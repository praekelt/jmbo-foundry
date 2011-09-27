import types

from django.forms.widgets import CheckboxSelectMultiple
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
