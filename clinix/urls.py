
from django.urls import path, include
from .api import MedicamentoView, TratamientoView, PacienteTratamientoView, TratamientoMedicamentoView; 

urlpatterns = [

    path('medicamentos/', MedicamentoView.as_view(), name='medicamentos'),
    path('medicamentos/<int:id>/', MedicamentoView.as_view(), name='medicamento_detalle'),    

    path('tratamientos/', TratamientoView.as_view(), name='tratamientos'), 
    path('tratamientos/<uuid:id>/', TratamientoView.as_view(), name='tratamiento_detalle'), 

    path('paciente-tratamiento/', PacienteTratamientoView.as_view(), name='paciente_tratamiento'), 
    path('paciente-tratamiento/<int:id>/', PacienteTratamientoView.as_view(), name='paciente_tratamiento_detalle'), 

    path('tratamiento-medicamento/', TratamientoMedicamentoView.as_view(), name='tratamiento_medicamento'), 
    path('tratamiento-medicamento/<int:id>/', TratamientoMedicamentoView.as_view(), name='tratamiento_medicamento_detalle'), 
]