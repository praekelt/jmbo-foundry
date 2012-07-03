from django import forms
from django.db.models.aggregates import Sum
from django.contrib.contenttypes.models import ContentType

from foundry.models import Menu, Navbar, Listing, Row, Column, Tile
from foundry.utils import get_view_choices


class RowEditAjaxForm(forms.ModelForm):

    class Meta:
        model = Row
        fields = ('block_name',)


class ColumnCreateAjaxForm(forms.ModelForm):

    class Meta:
        model = Column
        fields = ('row', 'width', 'title', 'designation')
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
        fields = ('row', 'width', 'title', 'designation')
        widgets = {
            'row':forms.widgets.HiddenInput, 
        }

    def clean_width(self):
        value = self.cleaned_data['width']
        if (value < 1) or (value > 16):
            raise forms.ValidationError('Width must be a value from 1 to 16.')
        return value   


class TileEditAjaxForm(forms.ModelForm):
    target = forms.ChoiceField(
        choices=[], 
        required=False, 
        help_text="A navbar, menu or listing."
    )

    class Meta:
        model = Tile
        fields = (
            'column', 'target', 'view_name', 'class_name', 'enable_ajax',
            'condition_expression'
        )
        widgets = {
            'column':forms.widgets.HiddenInput, 
            'target':forms.widgets.Select,
            'view_name':forms.widgets.Select
        }

    def __init__(self, *args, **kwargs):
        super(TileEditAjaxForm, self).__init__(*args, **kwargs)
        
        # Target choices
        choices = []
        for klass in (Menu, Navbar, Listing):
            ctid = ContentType.objects.get(app_label='foundry', model=klass.__name__.lower()).id
            for o in klass.objects.filter(sites__in=kwargs['instance'].column.row.page.sites.all()).distinct():
                title = o.title
                subtitle = getattr(o, 'subtitle', None)
                if subtitle:
                    title = '%s (%s)' % (title, subtitle)
                choices.append( ('%s_%s' % (ctid, o.id), '%s: %s' % (klass.__name__, title)) )
        self.fields['target'].choices = [('', '-- Select --')] + choices

        # Initial target
        if self.instance and self.instance.target:            
            self.fields['target'].initial = '%s_%s' % \
                (self.instance.target_content_type.id, self.instance.target_object_id)

        self.fields['view_name'].widget.choices = [('', '-- Select --')] + get_view_choices()

    def clean(self):
        cleaned_data = super(TileEditAjaxForm, self).clean()

        # One of target and view_name is required
        if not (cleaned_data['target'] or cleaned_data['view_name']):
            raise forms.ValidationError("Select either Target or View Name.")

        # target and view_name are mutually exclusive
        if cleaned_data['target'] and cleaned_data['view_name']:
            raise forms.ValidationError("Select either Target or View Name, not both.")
        return cleaned_data


    def save(self, commit=True):        
        instance = super(TileEditAjaxForm, self).save(commit)

        # Set target
        target = self.cleaned_data['target']
        if target:
            ctid, oid = target.split('_')
            instance.target = ContentType.objects.get(id=ctid).get_object_for_this_type(id=oid)
        else:
            instance.target = None

        if commit:
            instance.save()

        return instance

