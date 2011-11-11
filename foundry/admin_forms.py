from django import forms

from foundry.models import Tile


class TileEditAjaxForm(forms.ModelForm):

    class Meta:
        model = Tile
        fields = ('page', 'column', 'row', 'width', 'view_name', 'enable_ajax')
        widgets = {
            'page':forms.widgets.HiddenInput, 
            'column':forms.widgets.HiddenInput, 
            'row':forms.widgets.HiddenInput, 
        }

    def __init__(self, *args, **kwargs):
        page = kwargs.pop('page')
        column = kwargs.pop('column')
        super(TileEditAjaxForm, self).__init__(*args, **kwargs)
        self.initial['page'] = page
        self.initial['column'] = column
        self.initial['row'] = 1

    def clean(self):
        cleaned_data = super(TileEditAjaxForm, self).clean()
        # Compute row        
        cleaned_data['row'] = 1
        return cleaned_data
