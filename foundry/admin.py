import inspect

from django.db.models import CharField, Count
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.importlib import import_module
from django.contrib.admin import SimpleListFilter
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin as FlatPageAdminOld
from django.contrib.flatpages.admin import FlatpageForm as FlatpageFormOld
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.admin.options import IS_POPUP_VAR
from django.forms.widgets import Select

from ckeditor.widgets import CKEditorWidget
from preferences.admin import PreferencesAdmin
from sites_groups.widgets import SitesGroupsWidget
from jmbo.models import ModelBase
from jmbo.admin import ModelBaseAdmin
from jmbo.view_modifiers import ViewModifier

from foundry.models import Listing, Link, MenuLinkPosition, Menu, \
    NavbarLinkPosition, Navbar, GeneralPreferences, GeneralPreferences, \
    RegistrationPreferences, LoginPreferences, Member, DefaultAvatar, \
    PasswordResetPreferences, Country, Page, ChatRoom, BlogPost, Notification, \
    FoundryComment, CommentReport, PageView, NaughtyWordPreferences, \
    ViewProxy, ListingContent, ListingPinned
from foundry.widgets import SelectCommaWidget, DragDropOrderingWidget, RadioImageSelect
from foundry.utils import get_view_choices
from foundry.templatetags.listing_styles import LISTING_CLASSES


BLOGPOST_PREVIEW_SIZE = 256


class LinkAdminForm(forms.ModelForm):
    view_name = forms.ChoiceField(
        label='View Name',
        help_text="View name to which this link will redirect.",
        required=False
    )
    target = forms.ModelChoiceField(
        ModelBase.objects.all().order_by('title'),
        required=False,
        label='Target',
    )

    class Meta:
        model = Link
        fields = (
            'title', 'subtitle', 'view_name', 'category', 'target', 'url'
        )


    def __init__(self, *args, **kwargs):
        # Set view_name choices to url pattern names
        self.declared_fields['view_name'].choices = [('', '-- Select --'), ] + \
                get_view_choices()

        super(LinkAdminForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance', None)
        if (instance is not None) and instance.target:
            self.fields['target'].initial = instance.target

    def clean(self):
        cleaned_data = super(LinkAdminForm, self).clean()
        n = 0
        for fieldname in ('view_name', 'category', 'target', 'url'):
            if cleaned_data[fieldname]:
                if n:
                    raise forms.ValidationError(
                        "You may set at most one of view_name, category, target or URL."
                    )
                n += 1
        return cleaned_data

    def _post_clean(self):
        super(LinkAdminForm, self)._post_clean()
        target = self.cleaned_data['target']
        if target:
            self.instance.target_content_type = target.content_type
            self.instance.target_object_id = target.id
        else:
            self.instance.target_content_type = None
            self.instance.target_object_id = None


class LinkAdmin(admin.ModelAdmin):
    form = LinkAdminForm
    list_display = ('title', 'subtitle', '_get_absolute_url')

    def _get_absolute_url(self, obj):
        url = obj.get_absolute_url()
        return '<a href="%s" target="public">%s</a>' % (url, url)
    _get_absolute_url.short_description = 'Permalink'
    _get_absolute_url.allow_tags = True


class MenuLinkPositionInline(admin.StackedInline):
    model = MenuLinkPosition


class MenuAdminForm(forms.ModelForm):

    class Meta:
        model = Menu
        widgets = {'sites': SitesGroupsWidget}

    def clean(self):
        for site in self.cleaned_data['sites']:
            q = Menu.objects.filter(slug=self.cleaned_data['slug'], sites=site)
            if self.instance.id:
                q = q.exclude(id=self.instance.id)
            if q.exists():
                raise forms.ValidationError(_(
                    "The slug is already in use by menu %s. To use the same \
                    slug the pages menu not have overlapping sites." % q[0]
                ))
        return self.cleaned_data


class MenuAdmin(admin.ModelAdmin):
    form = MenuAdminForm
    prepopulated_fields = {'slug': ('title',)}
    inlines = [MenuLinkPositionInline]
    list_display = ('title', 'subtitle')
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'slug', 'sites', 'display_title')}),
        (
            'Caching', 
            {
                'fields': ('enable_caching', 'cache_type', 'cache_timeout'),
                'classes': ()
            }
        ),
    )


class NavbarLinkPositionInline(admin.StackedInline):
    model = NavbarLinkPosition


class NavbarAdminForm(forms.ModelForm):

    class Meta:
        model = Navbar
        widgets = {'sites': SitesGroupsWidget}

    def clean(self):
        for site in self.cleaned_data['sites']:
            q = Navbar.objects.filter(slug=self.cleaned_data['slug'], sites=site)
            if self.instance.id:
                q = q.exclude(id=self.instance.id)
            if q.exists():
                raise forms.ValidationError(_(
                    "The slug is already in use by navbar %s. To use the same \
                    slug the navbars may not have overlapping sites." % q[0]
                ))
        return self.cleaned_data


class NavbarAdmin(admin.ModelAdmin):
    form = NavbarAdminForm
    prepopulated_fields = {'slug': ('title',)}
    inlines = [NavbarLinkPositionInline]
    list_display = ('title', 'subtitle')
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'slug', 'sites')}),
        (
            'Caching',
            {
                'fields': ('enable_caching', 'cache_type', 'cache_timeout'),
                'classes': ()
            }
        ),
    )


class ListingAdminForm(forms.ModelForm):
    # Content and pinned fields use "through" and require manual handling
    content_helper = forms.models.ModelMultipleChoiceField(
        label=_('Content'),
        queryset=ModelBase.objects.all().order_by('title'),
        required=False,
        help_text=_("Individual items to display. Setting this will ignore \
any setting for <i>Content Type</i>, <i>Categories</i> and <i>Tags</i>."),
    )
    pinned_helper = forms.models.ModelMultipleChoiceField(
        label=_('Pinned'),
        queryset=ModelBase.objects.all().order_by('title'),
        required=False,
        help_text=_("Individual items to pin to the top of the listing. These \
items are visible across all pages when navigating the listing."),
    )

    class Meta:
        model = Listing
        fields = (
            'title', 'slug', 'subtitle', 'content_type', 'categories', 'tags',
            'content_helper', 'pinned_helper',
            'style', 'count', 'items_per_page',
            'view_modifier', 'display_title_tiled', 'enable_syndication',
            'sites',
        )
        widgets = {
            'sites': SitesGroupsWidget,
            'view_modifier': forms.widgets.RadioSelect,
            'style': RadioImageSelect(choices=(('x','x'),('y','y'))),
        }

    def __init__(self, *args, **kwargs):

        # Initial through values must be set here else the widgets get the
        # initial order wrong.
        instance = kwargs.get('instance')
        if instance:
            if not 'initial' in kwargs:
                kwargs['initial'] = {}
            kwargs['initial']['content_helper'] = \
                [o.modelbase_obj for o in ListingContent.objects.filter(
                    listing=instance).order_by('position')]
            kwargs['initial']['pinned_helper'] = \
                [o.modelbase_obj for o in ListingPinned.objects.filter(
                    listing=instance).order_by('position')]

        super(ListingAdminForm, self).__init__(*args, **kwargs)

        # Limit content_type vocabulary. Cannot do it with limit_choices_to.
        ids = []
        for obj in ContentType.objects.all():
            if (obj.model_class() is not None) and issubclass(obj.model_class(), ModelBase):
               ids.append(obj.id)
        self.fields['content_type']._set_queryset(ContentType.objects.filter(id__in=ids).order_by('name'))

        # Style
        choices = LISTING_CLASSES
        self.fields['style'].widget.choices = [(klass.__name__, klass.__name__, getattr(klass, 'image_path', None)) for klass in LISTING_CLASSES]

        # View modifiers. Inspect apps for modifiers. Iterate since there is
        # no registry.
        choices = [('', 'No ordering or filtering')]
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            if hasattr(mod, 'view_modifiers'):
                for name, klass in inspect.getmembers(mod.view_modifiers, inspect.isclass):
                    if (klass is not ViewModifier) and issubclass(klass, ViewModifier):
                        label = '%s (from %s)' % (name, app)
                        if klass.__doc__:
                            label = label + ' - ' + klass.__doc__
                        choices.append((
                            klass.__module__ + '.' + klass.__name__, label
                        ))
        self.fields['view_modifier'].widget.choices = choices


    def clean(self):
        super(ListingAdminForm, self).clean()
        for site in self.cleaned_data['sites']:
            q = Listing.objects.filter(slug=self.cleaned_data['slug'], sites=site)
            if self.instance.id:
                q = q.exclude(id=self.instance.id)
            if q.exists():
                raise forms.ValidationError(_(
                    "The slug is already in use by listing %s. To use the same \
                    slug the listings may not have overlapping sites." % q[0]
                ))
        return self.cleaned_data

    def save(self, commit=True):
        instance = super(ListingAdminForm, self).save(commit=False)

        # Set through fields. Requires m2m trickery.
        old_save_m2m = self.save_m2m
        def save_m2m():
            old_save_m2m()
            ListingContent.objects.filter(listing=instance).delete()
            for n, obj in enumerate(self.cleaned_data['content_helper']):
                ListingContent.objects.create(
                    modelbase_obj=obj, listing=instance, position=n
                )
            ListingPinned.objects.filter(listing=instance).delete()
            for n, obj in enumerate(self.cleaned_data['pinned_helper']):
                ListingPinned.objects.create(
                    modelbase_obj=obj, listing=instance, position=n
                )
        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class ListingAdmin(admin.ModelAdmin):
    form = ListingAdminForm
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'subtitle', '_get_absolute_url')

    def _get_absolute_url(self, obj):
        url = obj.get_absolute_url()
        return '<a href="%s" target="public">%s</a>' % (url, url)
    _get_absolute_url.short_description = 'Permalink'
    _get_absolute_url.allow_tags = True


class GeneralPreferencesAdmin(PreferencesAdmin):
    pass


class RegistrationPreferencesAdminForm(forms.ModelForm):
    """Form enabling the use of MultipleChoiceCommaField"""

    class Meta:
        model = RegistrationPreferences
        widgets = {
            'raw_display_fields':SelectCommaWidget,
            'raw_required_fields':SelectCommaWidget,
            'raw_unique_fields':SelectCommaWidget,
            'raw_field_order':DragDropOrderingWidget,
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationPreferencesAdminForm, self).__init__(*args, **kwargs)
        protected_fields = ('id', 'username', 'password')
        choices = [(unicode(f.name), f.name) for f in Member._meta.fields if f.name not in protected_fields]
        self.fields['raw_display_fields'].widget.choices = choices
        choices = [(unicode(f.name), f.name) for f in Member._meta.fields if (f.name not in protected_fields and isinstance(f, CharField))]
        self.fields['raw_unique_fields'].widget.choices = choices
        choices = [(f.name, f.name) for f in Member._meta.fields if f.blank and (f.name not in protected_fields)]
        self.fields['raw_required_fields'].widget.choices = choices

    def clean(self):
        cleaned_data = super(RegistrationPreferencesAdminForm, self).clean()
        # Unique fields must be unique! Check the existing members for possible
        # duplicate values. For example, if mobile number was not a unique
        # field before but it is now, then there may not be two members with
        # the same mobile number.
        unique_fields = [s for s in cleaned_data['raw_unique_fields'].split(',') if s]
        for fieldname in unique_fields:
            li = Member.objects.exclude(**{fieldname: None}).exclude(
                **{fieldname: ''}).values(fieldname).annotate(
                dcount=Count(fieldname)).order_by('-dcount')
            if li and li[0]['dcount'] > 1:
                raise forms.ValidationError(
                    "Cannot set %s to be unique since there is more than one \
member with the same %s %s." % (fieldname, fieldname, li[0][fieldname])
                    )
        return cleaned_data


class RegistrationPreferencesAdmin(PreferencesAdmin):
    form = RegistrationPreferencesAdminForm


class LoginPreferencesAdmin(PreferencesAdmin):
    pass


class PasswordResetPreferencesAdmin(PreferencesAdmin):
    pass


class NaughtyWordPreferencesAdmin(PreferencesAdmin):
    pass


class MemberChangeForm(UserChangeForm):
    class Meta:
        model = Member


class MemberCreationForm(UserCreationForm):
    class Meta:
        model = Member
        fields = ('username',)


class MemberAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'mobile_number', 'first_name', 'last_name',
        '_image'
    )
    search_fields = ['username', 'email']
    form = MemberChangeForm
    add_form = MemberCreationForm
    fieldsets = None

    def _image(self, obj):
        # todo: use correct photologue scale
        if obj.image:
            return """<img src="%s" height="48" width="48" />""" % obj.image.url
        return ""
    _image.short_description = 'Image'
    _image.allow_tags = True


class DefaultAvatarAdmin(admin.ModelAdmin):
    list_display = ('_image',)

    def _image(self, obj):
        # todo: use correct photologue scale
        if obj.image:
            return """<img src="%s" height="48" width="48" />""" % obj.image.url
        return ""
    _image.short_description = 'Image'
    _image.allow_tags = True


class CountryAdmin(admin.ModelAdmin):
    list_display = ('title', 'minimum_age')
    list_editable = ('minimum_age',)
    prepopulated_fields = {'slug': ('title',)}


class PageViewForm(forms.ModelForm):

    class Meta:
        model = PageView

    def __init__(self, *args, **kwargs):
        super(PageViewForm, self).__init__(*args, **kwargs)
        self.fields['view_name'].widget = forms.widgets.Select(
            choices=[('', '')] + get_view_choices()
        )


class PageViewInline(admin.StackedInline):
    form = PageViewForm
    model = PageView


class PageAdminForm(forms.ModelForm):

    class Meta:
        model = Page
        widgets = {'sites': SitesGroupsWidget}

    def clean(self):
        for site in self.cleaned_data['sites']:
            q = Page.objects.filter(slug=self.cleaned_data['slug'], sites=site)
            if self.instance.id:
                q = q.exclude(id=self.instance.id)
            if q.exists():
                raise forms.ValidationError(_(
                    "The slug is already in use by page %s. To use the same \
                    slug the pages may not have overlapping sites." % q[0]
                ))
        return self.cleaned_data


class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    list_display = ('title', 'subtitle', 'slug', 'is_homepage')
    prepopulated_fields = {'slug': ('title',)}
    #inlines = (PageViewInline,)

    def response_add(self, request, obj, post_url_continue=None):
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST['_continue'] = 1
        return super(PageAdmin, self).response_add(request, obj, post_url_continue)


class ChatRoomAdmin(ModelBaseAdmin):

    def _actions(self, obj):
        result = super(ChatRoomAdmin, self)._actions(obj)
        return result + '<a href="/admin/foundry/foundrycomment/?object_pk=%s">View messages</a>' % obj.pk
    _actions.short_description = 'Actions'
    _actions.allow_tags = True


class BlogPostAdmin(ModelBaseAdmin):
    list_display = ('title', 'preview', 'publish_on', 'retract_on', \
        '_get_absolute_url', 'owner', 'created', '_actions'
    )

    def preview(self, obj):
        preview = strip_tags(obj.content)
        if len(preview) > BLOGPOST_PREVIEW_SIZE:
            try:
                pos = preview.rindex(" ", 0, BLOGPOST_PREVIEW_SIZE)
            except ValueError:  # in case there is no space
                pos = BLOGPOST_PREVIEW_SIZE
            preview = preview[:pos] + '...'
        return preview
    preview.short_description = 'Preview'
    preview.allow_tags = True


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'link', 'created')
    raw_id_fields = ('member',)


class JmboContentTypeListFilter(SimpleListFilter):
    title = _("Jmbo content type")
    parameter_name = 'jmbo_content_type'

    def lookups(self, request, model_admin):
        result = []
        for obj in ContentType.objects.all().order_by('name'):
            model = obj.model_class()
            if (model is not None) and issubclass(model, ModelBase):
                result.append(('%s.%s' % (obj.app_label, obj.model), str(obj)))
        return result

    def queryset(self, request, queryset):
        if self.value():
            app_label, model = self.value().split('.')
            return queryset.filter(content_type__app_label=app_label, content_type__model=model)
        return queryset


class FoundryCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_object', 'user', 'comment')
    search_fields = ('user__username', 'comment',)
    list_filter = (JmboContentTypeListFilter,)


class CommentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'reporter')


# Override the flatpages admin form to use CKEditor
class FlatpageForm(FlatpageFormOld):
    content = forms.CharField(widget=CKEditorWidget)

    class Meta:
        model = FlatPage


class FlatPageAdmin(FlatPageAdminOld):
    form = FlatpageForm


class ViewProxyAdminForm(forms.ModelForm):
    """A form is required because of issues when specifying the choices in the
    model."""

    class Meta:
        model = ViewProxy
        widgets = {"view_name": Select}

    def __init__(self, *args, **kwargs):
        super(ViewProxyAdminForm, self).__init__(*args, **kwargs)
        self.fields["view_name"].widget.choices = get_view_choices()


class ViewProxyAdmin(ModelBaseAdmin):
    form = ViewProxyAdminForm


admin.site.register(Link, LinkAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Navbar, NavbarAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(GeneralPreferences, GeneralPreferencesAdmin)
admin.site.register(RegistrationPreferences, RegistrationPreferencesAdmin)
admin.site.register(LoginPreferences, LoginPreferencesAdmin)
admin.site.register(PasswordResetPreferences, PasswordResetPreferencesAdmin)
admin.site.register(NaughtyWordPreferences, NaughtyWordPreferencesAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(DefaultAvatar, DefaultAvatarAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(FoundryComment, FoundryCommentAdmin)
admin.site.register(CommentReport, CommentReportAdmin)
admin.site.register(ViewProxy, ViewProxyAdmin)
# We have to unregister the normal admin, and then reregister ours
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
