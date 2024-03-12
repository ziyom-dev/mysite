from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.models import ClusterableModel
from wagtail.admin.panels import TabbedInterface, FieldRowPanel, ObjectList, FieldPanel, InlinePanel
from django.utils.translation import gettext_lazy as _


# Create your models here.
class User(AbstractUser, ClusterableModel):
    phone_number = PhoneNumberField(region="UZ", unique=True)
    
    favorites_panels = [
        InlinePanel('favorite_products', heading="Favorite Products", label="Favorite Product"),
    ]
    
    main_panels = [
        FieldPanel("phone_number"),
        FieldPanel("first_name"),
        FieldPanel("last_name"),
    ]
    
    edit_handler = TabbedInterface(
        [
            ObjectList(main_panels, heading='Главные'),
            ObjectList(favorites_panels, heading='Избранные товары'),
        ]
    )
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="ecommerce_user_set",  # Изменённое related_name
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="ecommerce_user_set",  # Изменённое related_name
        related_query_name="user",
    )

    
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.phone_number} ({self.first_name} {self.last_name})"
        else:
            return str(self.phone_number)