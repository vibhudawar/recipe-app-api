"""
Django Admin Customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# for only future proofing, used in translation
from django.utils.translation import gettext_lazy as _

from core import models

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for the users."""
    # order the list by id
    ordering = ['id']
    # display the fields name and email
    list_display = ['email', 'name']
    # set the fields that will be visible/ can be toggled in the admin page
    fieldsets = (
        # title section is passed as None 
        (None, {'fields': ('email', 'password')}),
        (
            # title of the section
            _('Permissions'),
            {
                'fields':(
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        # title of the section
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fields = (
        (None, {
            # classes are used just for css and design
            'classes': ('wide',),
            'fields': (
                'email'
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

# register the user model in the admin site
admin.site.register(models.User, UserAdmin)


