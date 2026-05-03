
from django.urls import path, include
from .api import MedicamentoView; 

urlpatterns = [
    
    path('medicamentos/', MedicamentoView.as_view(), name='medicamentos'),
]