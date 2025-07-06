# from django.contrib import admin
# from .models import *
# # Register your models here.
# class UserDetails(admin.ModelAdmin):
#     # name = 'first_name'+'last'
#     list_display = (
#         'id',
#         'full_name',
#         'email',
#         'role',
#         'phone',
#         'is_staff'
#     )

# admin.site.register(CustomUser,UserDetails)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = CustomUser
    list_display = ('id','first_name', 'last_name','username', 'email', 'password','tagline','bio','profile_pic','website', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'role','tagline','bio','profile_pic','website')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'phone', 'role', 'password1', 'password2','tagline','bio','profile_pic','website'
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)