
from rest_framework.decorators import permission_classes
from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction; 
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Medicamento
#Integracion de los endpoints para el manejo de las citas 

# Endpoint para los medicamentos 

@extend_schema(tags=['Medicamentos'])
class MedicamentoView(APIView): 


    @extend_schema(
        summary="Obtener todos los medicamentos",
        description="Obtiene todos los medicamentos de la base de datos.",
        parameters=[
            OpenApiParameter(
                name="nombre", 
                type=OpenApiTypes.STR, 
                location=OpenApiParameter.QUERY, 
                description="Filtrar por nombre del medicamento (Ejemplo: paracetamol)",
                required=True
            ),
        ],
        responses={
            200: OpenApiResponse(description="Medicamentos obtenidos exitosamente"),
            401: OpenApiResponse(description="No autorizado"),
        }
    )
    def get(self, request, id=None): 
        # Si envían un ID, retornamos un solo elemento
        if id is not None:
            try:
                med = Medicamento.objects.get(id=id)
                data = {
                    'id': med.id, 
                    'nombre_medicamento': med.nombre_medicamento, 
                    'descripcion': med.descripcion, 
                    'imagen': med.imagen.url if med.imagen else None,
                }
                return Response({
                    'medicamento': data, 
                    'message': 'Medicamento obtenido exitosamente', 
                    'status': 200,
                }, status=status.HTTP_200_OK)
            except Medicamento.DoesNotExist:
                return Response({
                    'error': 'El medicamento no existe',
                    'status': 404
                }, status=status.HTTP_404_NOT_FOUND)

        # Si NO envían un ID, listamos todos
        medicamentos = Medicamento.objects.all()
        data = []

        for med in medicamentos: 
            data.append({
                'id': med.id, 
                'nombre_medicamento': med.nombre_medicamento, 
                'descripcion': med.descripcion, 
                'imagen': med.imagen.url if med.imagen else None,
            })

        return Response({
            'medicamentos': data, 
            'message': 'Medicamentos obtenidos exitosamente', 
            'status': 200,
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Crear un nuevo medicamento",
        description="Crea un nuevo medicamento en el sistema. Debe enviarse como form-data si incluye una imagen.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "doctor": {"type": "integer", "description": "ID del doctor al que pertenece"},
                    "nombre_medicamento": {"type": "string", "example": "Paracetamol 500mg"},
                    "descripcion": {"type": "string", "example": "Analgésico y antipirético"},
                    "imagen": {"type": "string", "format": "binary", "description": "Archivo de imagen"}
                },
                "required": ["doctor", "nombre_medicamento", "descripcion"]
            }
        },
        responses={
            201: OpenApiResponse(description="Medicamento creado exitosamente"),
            401: OpenApiResponse(description="No autorizado"),
        }
    )
    def post(self, request): 

        data = request.data;
        
        try:
            with transaction.atomic(): 

                medicamento = Medicamento.objects.create(
                    doctor_id = data['doctor'], 
                    nombre_medicamento = data['nombre_medicamento'],
                    descripcion = data['descripcion'],
                    imagen = data.get('imagen'),
                ); 

                return Response({
                    'message': 'Medicamento creado exitosamente', 
                    'status': 201,
                }, status=status.HTTP_201_CREATED); 

        except Exception as e: 
            return Response({
                'message': 'Error al crear el medicamento', 
                'error': str(e),
                'status': 500,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 
            
    @extend_schema(
        summary="Actualizar un medicamento",
        description="Actualiza un medicamento",
        responses={
            200: OpenApiResponse(description="Medicamento actualizado exitosamente"),
            401: OpenApiResponse(description="No autorizado"),
        }
    )
    def put(self, request, id): 

        data = request.data; 

        try: 
            with transaction.atomic(): 

                medicamento = Medicamento.objects.get(id=id); 
                medicamento.nombre_medicamento = data['nombre_medicamento']; 
                medicamento.descripcion = data['descripcion']; 
                medicamento.imagen = data['imagen']; 
                medicamento.save(); 

                return Response({ 
                    'message': 'Medicamento actualizado exitosamente', 
                    'status': 200,
                }, status=status.HTTP_200_OK); 

        except Exception as e: 
            return Response({ 
                'message': 'Error al actualizar el medicamento', 
                'error': str(e), 
                'status': 500,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 

    #eliminado logico, no se eliminara el medicamento
    @extend_schema(
        summary="Eliminar un medicamento",
        description="Elimina un medicamento",
        responses={
            200: OpenApiResponse(description="Medicamento eliminado exitosamente"),
            401: OpenApiResponse(description="No autorizado"),
        }
    )
    def delete(self, request, id): 

        try: 
            with transaction.atomic(): 

                medicamento = Medicamento.objects.get(id=id); 
                medicamento.is_active = False; 
                medicamento.save(); 

                return Response({ 
                    'message': 'Medicamento eliminado exitosamente', 
                    'status': 200,
                }, status=status.HTTP_200_OK); 

        except Exception as e: 
            return Response({ 
                'message': 'Error al eliminar el medicamento', 
                'error': str(e), 
                'status': 500,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 


    

