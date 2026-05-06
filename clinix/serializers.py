
from dataclasses import field
from .models import Tratamiento, Medicamento, TratamientoMedicamento, PacienteTratamiento
from rest_framework import serializers
from datetime import date


class MedicamentoSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Medicamento
        fields = '__all__'; 

    def validate_nombre_medicamento(self, value): 

        #valida que el nombre del medicamento no sea demasiado corto o no haya nada dentro

        if(len(value) <= 0): 
            raise serializers.ValidationError('El nombre del medicamento es requerido')
        return value

    def validate_descripcion(self, value): 
        if(len(value) <= 0): 
            raise serializers.ValidationError('La descripcion del medicamento es requerida')
        return value

class TratamientoSerializer(serializers.ModelSerializer): 

    class Meta: 
        model = Tratamiento
        fields = '__all__'
        read_only_fields = ('uuid', 'created_at', 'updated_at')

    def validate_titulo(self, value): 
        if len(value.strip()) <= 0: 
            raise serializers.ValidationError('El titulo del tratamiento es requerido')
        return value

    def validate_descripcion(self, value): 
        if len(value.strip()) <= 0: 
            raise serializers.ValidationError('La descripcion del tratamiento es requerida')
        return value 

    def validate_doctor(self, value): 
        if value is None: 
            raise serializers.ValidationError('El doctor del tratamiento es requerido')
        return value 

class PacienteTratamientoSerializer(serializers.ModelSerializer): 
    
    class Meta: 
        model = PacienteTratamiento
        fields = '__all__'

    def validate_paciente(self, value): 
        if value is None: 
            raise serializers.ValidationError('El paciente del tratamiento es requerido')
        return value

    def validate_tratamiento(self, value): 
        if value is None: 
            raise serializers.ValidationError('El tratamiento es requerido')
        return value 

class TratamientoMedicamentoSerializer(serializers.ModelSerializer): 

    class Meta: 
        model = TratamientoMedicamento
        fields = '__all__'

    def validate_tratamiento(self, value): 

        if value is None: 
            raise serializers.ValidationError('El tratamiento es requerido');
        return value;

    def validate_medicamento(self, value): 
        if value is None: 
            raise serializers.ValidationError('El medicamento es requerido');
        return value;
    
    def validate_dosis(self, value): 
        if value is None: 
            raise serializers.ValidationError('La dosis es requerida');
        return value;

    def validate_horario(self, value): 
        if value is None: 
            raise serializers.ValidationError('El horario es requerido');
        return value;

    def validate_instrucciones(self, value): 
        if value is None: 
            raise serializers.ValidationError('Las instrucciones son requeridas');
        return value; 


