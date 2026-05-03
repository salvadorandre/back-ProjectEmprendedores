from django.contrib import admin
from .models import Paciente, Doctor, Medicamento, Tratamiento, PacienteTratamiento, TratamientoMedicamento, RegistroMedication
# Register your models here.

admin.site.register(Paciente)
admin.site.register(Doctor)
admin.site.register(Medicamento)
admin.site.register(Tratamiento)
admin.site.register(PacienteTratamiento)
admin.site.register(TratamientoMedicamento)
admin.site.register(RegistroMedication)
