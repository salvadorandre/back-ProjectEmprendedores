
from dataclasses import field
from .models import Tratamiento, Medicamento, TratamientoMedicamento, PacienteTratamiento, RegistroMedication
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
    def to_representation(self, instance):
        
        representation = super().to_representation(instance)

        representation['doctor'] = {
            'id': instance.doctor.id,
            'especialidad': instance.doctor.especialidad,
            'colegiado': instance.doctor.colegiado,
            'usuario': {
                'id': instance.doctor.user.id,
                'email': instance.doctor.user.email,
                'is_active': instance.doctor.user.is_active
            }
        }
        
        return representation


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


class RegistroMedicationSerializer(serializers.ModelSerializer):

    class Meta: 
        model = RegistroMedication
        fields = '__all__'

    def to_representation(self, instance): 

        representation = super().to_representation(instance)

        representation['tratamiento_medicamento'] = {
            'id': instance.tratamiento_medicamento.id,
            'tratamiento': instance.tratamiento_medicamento.tratamiento.titulo,
            'medicamento': instance.tratamiento_medicamento.medicamento.nombre_medicamento,
            'dosis': instance.tratamiento_medicamento.dosis,
            'horario': instance.tratamiento_medicamento.horario,
            'instrucciones': instance.tratamiento_medicamento.instrucciones,
        };

        representation['paciente'] = {
            'id': instance.paciente.id,
            'user': instance.paciente.user.email, 
            'fecha_nac': instance.paciente.fecha_nac,
            'descripcion': instance.paciente.descripcion,
            'telefono': instance.paciente.telefono,
            'user': {
                'id': instance.paciente.user.id,
                'email': instance.paciente.user.email,
            } 
        } 
        return representation

    def validate_paciente_tratamiento(self, value): 
        if value is None: 
            raise serializers.ValidationError('El paciente_tratamiento es requerido');
        
        return value;
    
    def validate_paciente(self, value): 
        if value is None: 
            raise serializers.ValidationError('El paciente es requerido');
        
        return value; 
    
    def validate_fecha_toma(self, value):
        if value is None: 
            raise serializers.ValidationError('La fecha de toma es requerida');
        if value > date.today(): 
            raise serializers.ValidationError('La fecha de toma no puede ser mayor a la fecha actual');
        return value; 
    
    def validate_hora(self, value): 
        if value is None: 
            raise serializers.ValidationError('La hora es requerida');
        return value; 
    
    