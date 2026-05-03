from rest_framework import serializers
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'email', 'google_id', 'is_doctor', 'is_paciente', 'password', 'is_active', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'google_id': {'required': False},
            'is_active': {'read_only': True},
            'date_joined': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        # Handle password update properly
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
