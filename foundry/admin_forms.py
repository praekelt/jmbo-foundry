from django import forms
from django.db.models.aggregates import Sum

from foundry.models import Column, Tile
from foundry.utils import get_view_choices


class ColumnCreateAjaxForm(forms.ModelForm):

    class Meta:
        model = Column
        fields = ('row', 'width')
        widgets = {
            'row':forms.widgets.HiddenInput, 
        }

    def clean_width(self):
        """Check that width does not exceed maximum for the row"""        
        value = self.cleaned_data['width']
        row = self.cleaned_data['row']
        total_width = row.column_set.all().aggregate(Sum('width'))['width__sum'] or 0
        max_width = 16 - total_width       
        min_width = min(max_width, 1)
        if (value < min_width) or (value > max_width):
            raise forms.ValidationError('Width must be a value from %s to %s.' % (min_width, max_width))
        return value   


class ColumnEditAjaxForm(forms.ModelForm):

    class Meta:
        model = Column
        fields = ('row', 'width')
        widgets = {
            'row':forms.widgets.HiddenInput, 
        }

    def clean_width(self):
        value = self.cleaned_data['width']
        if (value < 1) or (value > 16):
            raise forms.ValidationError('Width must be a value from 1 to 16.')
        return value   


class TileEditAjaxForm(forms.ModelForm):

    class Meta:
        model = Tile
        fields = ('column', 'view_name', 'class_name', 'enable_ajax')
        widgets = {
            'column':forms.widgets.HiddenInput, 
            'view_name':forms.widgets.Select
        }

    def __init__(self, *args, **kwargs):
        super(TileEditAjaxForm, self).__init__(*args, **kwargs)
        self.fields['view_name'].widget.choices = get_view_choices()

