from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario que usa email como identificador único."""

    def create_user(self, email, password=None, **extra_fields):
        """Crea y retorna un usuario con email y contraseña."""
        if not email:
            raise ValueError('El usuario debe tener un email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Crea y retorna un superusuario."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuario personalizado que usa email como identificador único."""
    email = models.EmailField('correo electrónico', unique=True)
    google_id = models.CharField('ID de Google', max_length=255, blank=True, null=True, unique=True)
    is_doctor = models.BooleanField('es doctor', default=False)
    is_paciente = models.BooleanField( 'es paciente', default=False)

    # Campos requeridos por Django
    is_active = models.BooleanField('activo', default=True)
    is_staff = models.BooleanField('es staff', default=False)
    date_joined = models.DateTimeField('fecha de registro', auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.email
