from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


class UsuarioAdmin(UserAdmin):
    """Configuración del panel de admin para el modelo Usuario."""

    model = Usuario
    list_display = ('email', 'is_doctor', 'is_paciente', 'is_active', 'is_staff')
    list_filter = ('is_doctor', 'is_paciente', 'is_active', 'is_staff')
    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Google', {'fields': ('google_id',)}),
        ('Roles', {'fields': ('is_doctor', 'is_paciente')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_doctor', 'is_paciente'),
        }),
    )


admin.site.register(Usuario, UsuarioAdmin)
