from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from preferences.admin import PreferencesAdmin
from jmbo.models import ModelBase
from jmbo.admin import ModelBaseAdmin

from foundry.models import Listing, Link, MenuLinkPosition, Menu, \
    NavbarLinkPosition, Navbar, GeneralPreferences, GeneralPreferences, \
    RegistrationPreferences, LoginPreferences, Member, DefaultAvatar, \
    PasswordResetPreferences, Country, Page, ChatRoom, BlogPost, Notification, \
    FoundryComment
from foundry.widgets import SelectCommaWidget
from foundry.utils import get_view_choices


class LinkAdminForm(forms.ModelForm):
    view_name = forms.ChoiceField(
        label='View Name',
        help_text="View name to which this link will redirect. This takes \
precedence over url field below.",
        required=False
    )

    class Meta:
        model = Link

    def __init__(self, *args, **kwargs):
        """
        Set view_name choices to url pattern names
        """
        self.declared_fields['view_name'].choices = [('', '-- Select --'), ] + \
                get_view_choices()

        super(LinkAdminForm, self).__init__(*args, **kwargs)


class LinkAdmin(admin.ModelAdmin):
    form = LinkAdminForm


class MenuLinkPositionInline(admin.StackedInline):
    model = MenuLinkPosition


class MenuAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [MenuLinkPositionInline]
    list_display = ('title', 'subtitle')
   

class NavbarLinkPositionInline(admin.StackedInline):
    model = NavbarLinkPosition


class NavbarAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [NavbarLinkPositionInline]
    list_display = ('title', 'subtitle')


class ListingAdminForm(forms.ModelForm):
    #content_type = forms.MultipleChoiceField()

    class Meta:
        model = Listing
        fields = (
            'title', 'slug', 'subtitle', 'content_type', 'category', 'content', 
            'style', 'count', 'display_likes', 'items_per_page', 'sites'
        )       

    def __init__(self, *args, **kwargs):
        super(ListingAdminForm, self).__init__(*args, **kwargs)

        # Limit content_type vocabulary. Cannot do it with limit_choices_to.
        ids = []
        for obj in ContentType.objects.all():       
            if issubclass(obj.model_class(), ModelBase):
               ids.append(obj.id) 
        self.fields['content_type']._set_queryset(ContentType.objects.filter(id__in=ids).order_by('name'))

        # Order
        field = self.fields['content']
        field._set_queryset(field._queryset.order_by('title'))

    def clean(self):
        cleaned_data = super(ListingAdminForm, self).clean()
        n = 0
        for fieldname in ('content_type', 'content', 'category'):
            if cleaned_data[fieldname]:
                if n:
                    raise forms.ValidationError(
                        "You may set at most one of content type, content or category."
                    )
                n += 1
        return cleaned_data


class ListingAdmin(admin.ModelAdmin):
    form = ListingAdminForm
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'subtitle')


class GeneralPreferencesAdmin(PreferencesAdmin):
    pass


class RegistrationPreferencesAdminForm(forms.ModelForm):
    """Form enabling the use of MultipleChoiceCommaField"""

    class Meta:
        model = RegistrationPreferences
        widgets = {
            'raw_display_fields':SelectCommaWidget,
            'raw_required_fields':SelectCommaWidget,
            'raw_unique_fields':SelectCommaWidget
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationPreferencesAdminForm, self).__init__(*args, **kwargs)
        protected_fields = ('id', 'username', 'password')
        choices = [(unicode(f.name), f.name) for f in Member._meta.fields if f.name not in protected_fields]
        self.fields['raw_display_fields'].widget.choices = choices
        self.fields['raw_unique_fields'].widget.choices = choices
        choices = [(f.name, f.name) for f in Member._meta.fields if f.blank and (f.name not in protected_fields)]
        self.fields['raw_required_fields'].widget.choices = choices


class RegistrationPreferencesAdmin(PreferencesAdmin):
    form = RegistrationPreferencesAdminForm


class LoginPreferencesAdmin(PreferencesAdmin):
    pass


class PasswordResetPreferencesAdmin(PreferencesAdmin):
    pass


class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'mobile_number', 'first_name', 'last_name', 
        '_image'
    )
    search_fields = ['username', 'email']

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


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'slug', 'is_homepage')
    prepopulated_fields = {'slug': ('title',)}
   
    def response_add(self, request, obj, post_url_continue='../%s/'):
        if '_addanother' not in request.POST and '_popup' not in request.POST:
            request.POST['_continue'] = 1 
        return super(PageAdmin, self).response_add(request, obj, post_url_continue)


class ChatRoomAdmin(ModelBaseAdmin):
    pass


class BlogPostAdmin(ModelBaseAdmin):
    list_display = ('title', 'owner')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'link', 'created')


class FoundryCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_object', 'user', 'comment')
    search_fields = ('user__username', 'comment',)


admin.site.register(Link, LinkAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Navbar, NavbarAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(GeneralPreferences, GeneralPreferencesAdmin)
admin.site.register(RegistrationPreferences, RegistrationPreferencesAdmin)
admin.site.register(LoginPreferences, LoginPreferencesAdmin)
admin.site.register(PasswordResetPreferences, PasswordResetPreferencesAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(DefaultAvatar, DefaultAvatarAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(FoundryComment, FoundryCommentAdmin)
