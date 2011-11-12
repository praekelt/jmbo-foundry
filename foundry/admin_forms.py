from django import forms

from foundry.models import Tile
from foundry.utils import get_view_choices


class TileEditAjaxForm(forms.ModelForm):

    class Meta:
        model = Tile
        fields = ('page', 'column', 'row', 'width', 'view_name', 'enable_ajax')
        widgets = {
            'page':forms.widgets.HiddenInput, 
            'column':forms.widgets.HiddenInput, 
            'row':forms.widgets.HiddenInput, 
            'view_name':forms.widgets.Select
        }

    def __init__(self, *args, **kwargs):
        page = kwargs.pop('page')
        column = kwargs.pop('column')
        super(TileEditAjaxForm, self).__init__(*args, **kwargs)
        self.initial['page'] = page
        self.initial['column'] = column
        self.initial['row'] = 1
        self.fields['view_name'].widget.choices = get_view_choices()

    def clean_width(self):
        value = self.cleaned_data['width']
        if (value < 1) or (value > 16):
            raise forms.ValidationError('Width must be from 1 to 16.')
        return value

    def clean(self):
        cleaned_data = super(TileEditAjaxForm, self).clean()
        # Compute row        
        cleaned_data['row'] = 1
        return cleaned_data
