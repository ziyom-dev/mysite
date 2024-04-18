# views.py

from django import forms
from django.conf import settings
from Customer.models import User
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms.choosers import BaseFilterForm, LocaleFilterMixin
from wagtail.admin.ui.tables import TitleColumn
from wagtail.admin.views.generic.chooser import (BaseChooseView,
                                                 ChooseResultsViewMixin,
                                                 ChooseViewMixin,
                                                 CreationFormMixin,)
from wagtail.admin.viewsets.chooser import ChooserViewSet
from wagtail.models import TranslatableMixin


class UserSearchFilterMixin(forms.Form):

    q = forms.CharField(
        label=_("Search term"),
        widget=forms.TextInput(attrs={"placeholder": _("Search")}),
        required=False,
    )

    def filter(self, objects):
        objects = super().filter(objects)
        search_query = self.cleaned_data.get("q")
        
        objects = objects.filter(is_superuser=False)

        if search_query:
            objects = objects.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query)
            )
            self.is_searching = True
            self.search_query = search_query
        return objects

class BaseUserChooseView(BaseChooseView):

    @property
    def columns(self):
        return [
            TitleColumn(
                name="username",
                label=_("Username"),
                accessor="username",
                url_name=self.chosen_url_name,
                link_attrs={"data-chooser-modal-choice": True},
            ),
            TitleColumn(
                name="get_full_name",
                label=_("Name"),
                accessor="get_full_name",
                url_name=self.chosen_url_name,
                link_attrs={"data-chooser-modal-choice": True},
            ),
            TitleColumn(
                name="email",
                label=_("Email"),
                accessor="email",
                url_name=self.chosen_url_name,
                link_attrs={"data-chooser-modal-choice": True},
            ),
        ]

    def get_filter_form_class(self):
        bases = [UserSearchFilterMixin, BaseFilterForm]

        i18n_enabled = getattr(settings, "WAGTAIL_I18N_ENABLED", False)
        if i18n_enabled and issubclass(self.model_class, TranslatableMixin):
            bases.insert(0, LocaleFilterMixin)

        return type(
            "FilterForm",
            tuple(bases),
            {},
        )
        
class UserChooseView(ChooseViewMixin, CreationFormMixin, BaseUserChooseView):
    pass

class UserChooseResultsView(ChooseResultsViewMixin, CreationFormMixin, BaseUserChooseView):
    pass

class UserChooserViewSet(ChooserViewSet):
    model = User

    choose_view_class = UserChooseView
    choose_results_view_class = UserChooseResultsView

    icon = "user"
    choose_one_text = _("Choose a user")
    choose_another_text = _("Choose another user")
    edit_item_text = _("Edit this user")


user_chooser_viewset = UserChooserViewSet("user_chooser")



# Attribute GroupChooser
class AttributeGroupSearchFilterMixin(forms.Form):
    q = forms.CharField(
        label=_("Search term"),
        widget=forms.TextInput(attrs={"placeholder": _("Search by Attribute Group Name")}),
        required=False,
    )

    def filter(self, objects):
        search_query = self.cleaned_data.get("q")
        if search_query:
            objects = objects.filter(
                Q(name__icontains=search_query)
            )
        return objects
    
class BaseAttributeGroupChooseView(BaseChooseView):
    def get_filter_form_class(self):
        bases = [AttributeGroupSearchFilterMixin, BaseFilterForm]

        i18n_enabled = getattr(settings, "WAGTAIL_I18N_ENABLED", False)
        if i18n_enabled and issubclass(self.model_class, TranslatableMixin):
            bases.insert(0, LocaleFilterMixin)

        return type(
            "FilterForm",
            tuple(bases),
            {},
        )
        
class AttributeGroupChooseView(ChooseViewMixin, CreationFormMixin, BaseAttributeGroupChooseView):
    pass

class AttributeGroupChooseResultsView(ChooseResultsViewMixin, CreationFormMixin, BaseAttributeGroupChooseView):
    pass

class AttributeGroupChooserViewSet(ChooserViewSet):
    model = "ecommerce.AttributeGroup"
    
    form_fields = ["name"]
    
    choose_one_text = _("Choose a group")
    choose_another_text = _("Choose another group")
    edit_item_text = _("Edit this group")
    
    choose_view_class = AttributeGroupChooseView
    choose_results_view_class = AttributeGroupChooseResultsView

attribute_group_chooser_viewset = AttributeGroupChooserViewSet('attribute_group_chooser')




# Attribute Value Chooser
class AttributeValueSearchFilterMixin(forms.Form):
    q = forms.CharField(
        label=_("Search term"),
        widget=forms.TextInput(attrs={"placeholder": _("Search by Attribute Value")}),
        required=False,
    )

    def filter(self, objects):
        search_query = self.cleaned_data.get("q")
        if search_query:
            objects = objects.filter(
                Q(value__icontains=search_query)
            )
        return objects
    
class BaseAttributeValueChooseView(BaseChooseView):
    def get_filter_form_class(self):
        bases = [AttributeValueSearchFilterMixin, BaseFilterForm]

        i18n_enabled = getattr(settings, "WAGTAIL_I18N_ENABLED", False)
        if i18n_enabled and issubclass(self.model_class, TranslatableMixin):
            bases.insert(0, LocaleFilterMixin)

        return type(
            "FilterForm",
            tuple(bases),
            {},
        )
    
class AttributeValueChooseView(ChooseViewMixin, CreationFormMixin, BaseAttributeValueChooseView):
    pass

class AttributeValueChooseResultsView(ChooseResultsViewMixin, CreationFormMixin, BaseAttributeValueChooseView):
    pass

class AttributeValueChooserViewSet(ChooserViewSet):
    model = "ecommerce.AttributeValue"
    form_fields = ["attribute", "value"]
    url_filter_parameters = ["attribute"]
    preserve_url_parameters = ["multiple", "attribute"]
    
    choose_one_text = _("Choose a value")
    choose_another_text = _("Choose another value")
    edit_item_text = _("Edit this value")
    
    choose_view_class = AttributeValueChooseView
    choose_results_view_class = AttributeValueChooseResultsView

attribute_value_chooser_viewset = AttributeValueChooserViewSet('attribute_value_chooser')


# Attribute Chooser
class AttributeSearchFilterMixin(forms.Form):
    q = forms.CharField(
        label=_("Search term"),
        widget=forms.TextInput(attrs={"placeholder": _("Search by attribute name")}),
        required=False,
    )

    def filter(self, objects):
        search_query = self.cleaned_data.get("q")
        if search_query:
            objects = objects.filter(
                Q(name__icontains=search_query)
            )
        return objects
    
class BaseAttributeChooseView(BaseChooseView):
    def get_filter_form_class(self):
        bases = [AttributeSearchFilterMixin, BaseFilterForm]

        i18n_enabled = getattr(settings, "WAGTAIL_I18N_ENABLED", False)
        if i18n_enabled and issubclass(self.model_class, TranslatableMixin):
            bases.insert(0, LocaleFilterMixin)

        return type(
            "FilterForm",
            tuple(bases),
            {},
        )
    
class AttributeChooseView(ChooseViewMixin, CreationFormMixin, BaseAttributeChooseView):
    pass

class AttributeChooseResultsView(ChooseResultsViewMixin, CreationFormMixin, BaseAttributeChooseView):
    pass

class AttributeChooserViewSet(ChooserViewSet):
    model = "ecommerce.Attribute"
    form_fields = ["group", "name"]
    url_filter_parameters = ["group"]
    preserve_url_parameters = ["multiple", "group"]
    
    choose_view_class = AttributeChooseView
    choose_results_view_class = AttributeChooseResultsView
    
    
    choose_one_text = _("Choose an attribute")
    choose_another_text = _("Choose another attribute")
    edit_item_text = _("Edit this attribute")
    

attribute_chooser_viewset = AttributeChooserViewSet('attribute_chooser')


# Category Chooser
class CategorySearchFilterMixin(forms.Form):
    q = forms.CharField(
        label=_("Search term"),
        widget=forms.TextInput(attrs={"placeholder": _("Search by Category name")}),
        required=False,
    )

    def filter(self, objects):
        search_query = self.cleaned_data.get("q")
        if search_query:
            objects = objects.filter(
                Q(name__icontains=search_query)
            )
        return objects
    
class BaseCategoryChooseView(BaseChooseView):
    def get_filter_form_class(self):
        bases = [CategorySearchFilterMixin, BaseFilterForm]

        i18n_enabled = getattr(settings, "WAGTAIL_I18N_ENABLED", False)
        if i18n_enabled and issubclass(self.model_class, TranslatableMixin):
            bases.insert(0, LocaleFilterMixin)

        return type(
            "FilterForm",
            tuple(bases),
            {},
        )

class CategoryChooseView(ChooseViewMixin, CreationFormMixin, BaseCategoryChooseView):
    pass

class CategoryChooseResultsView(ChooseResultsViewMixin, CreationFormMixin, BaseCategoryChooseView):
    pass

class CategoryChooserViewSet(ChooserViewSet):
    model = "ecommerce.Category"
    url_filter_parameters = ["parent","level"]
    preserve_url_parameters = ["multiple", "parent", "level"]
    
    choose_view_class = CategoryChooseView
    choose_results_view_class = CategoryChooseResultsView
    

category_chooser_viewset = CategoryChooserViewSet('category_chooser')

# UserAdress


class AddressSearchFilterMixin(forms.Form):
    q = forms.CharField(
        label=_("Search term"),
        widget=forms.TextInput(attrs={"placeholder": _("Search by Address name")}),
        required=False,
    )

    def filter(self, objects):
        search_query = self.cleaned_data.get("q")
        if search_query:
            objects = objects.filter(
                Q(title__icontains=search_query)
            )
        return objects
    
class BaseAddressChooseView(BaseChooseView):
    def get_filter_form_class(self):
        bases = [AddressSearchFilterMixin, BaseFilterForm]

        i18n_enabled = getattr(settings, "WAGTAIL_I18N_ENABLED", False)
        if i18n_enabled and issubclass(self.model_class, TranslatableMixin):
            bases.insert(0, LocaleFilterMixin)

        return type(
            "FilterForm",
            tuple(bases),
            {},
        )

class AddressChooseView(ChooseViewMixin, CreationFormMixin, BaseAddressChooseView):
    pass

class AddressChooseResultsView(ChooseResultsViewMixin, CreationFormMixin, BaseAddressChooseView):
    pass

class AddressChooserViewSet(ChooserViewSet):
    model = "Customer.Address"
    url_filter_parameters = ["user"]
    preserve_url_parameters = ["multiple", "user"]
    
    choose_view_class = AddressChooseView
    choose_results_view_class = AddressChooseResultsView
    

address_chooser_viewset = AddressChooserViewSet('address_chooser')
