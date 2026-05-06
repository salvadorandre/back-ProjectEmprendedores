
from rest_framework.decorators import permission_classes
from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction; 
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import TratamientoSerializer, MedicamentoSerializer, PacienteTratamientoSerializer, TratamientoMedicamentoSerializer; 
from .models import Medicamento, Tratamiento, PacienteTratamiento, TratamientoMedicamento
#Integracion de los endpoints para el manejo de las citas 

# Endpoint para los medicamentos 

@extend_schema(tags=['Medicamentos'])
class MedicamentoView(APIView): 
    serializer_class = MedicamentoSerializer


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

                serializer = MedicamentoSerializer(data=data);

                if serializer.is_valid(): 
                    serializer.save()

                    return Response({
                        "data" : serializer.data, 
                        "message" : "Medicamento creado exitosamente",
                        "status" : 201,
                    }, status=status.HTTP_201_CREATED);

                else: 
                    return Response({
                        "error" : serializer.errors, 
                        "message" : "Error al crear el medicamento",
                        "status" : 400,
                    }, status=status.HTTP_400_BAD_REQUEST);

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


@extend_schema(tags=['Tratamientos'])

class TratamientoView(APIView) : 
    serializer_class = TratamientoSerializer

    def get(self, request, id=None): 
        # Si envían un ID (que en este caso es un UUID), buscamos solo ese tratamiento
        if id is not None: 
            try: 
                # Buscamos por 'uuid' porque esa es tu llave primaria (primary_key=True)
                tratamiento = Tratamiento.objects.get(uuid=id) 
                
                # ¡Usamos el serializador para convertirlo a diccionario!
                serializer = TratamientoSerializer(tratamiento)

                return Response({ 
                    'tratamiento': serializer.data, 
                    'message': 'Tratamiento obtenido exitosamente', 
                    'status': 200,
                }, status=status.HTTP_200_OK) 

            except Tratamiento.DoesNotExist: 
                return Response({ 
                    'message': 'El tratamiento no existe', 
                    'status': 404,
                }, status=status.HTTP_404_NOT_FOUND) 

        # Si no envían ID, traemos todos los tratamientos
        else: 
            tratamientos = Tratamiento.objects.all()
            
            # many=True le dice al serializador que es una lista de objetos
            serializer = TratamientoSerializer(tratamientos, many=True)

            return Response({ 
                'tratamientos': serializer.data, 
                'message': 'Tratamientos obtenidos exitosamente', 
                'status': 200,
            }, status=status.HTTP_200_OK)

    
    def post(self, request): 

        #validar con el serializador 

        data = request.data; 

        serializer = TratamientoSerializer(data=data); 

        if serializer.is_valid(): 
            serializer.save()

            return Response({ 
                'data': serializer.data, 
                'message': 'Tratamiento creado exitosamente', 
                'status': 201, 
            }, status=status.HTTP_201_CREATED); 
        else: 
            return Response({ 
                'error': serializer.errors, 
                'message': 'Error al crear el tratamiento', 
                'status': 400, 
            }, status=status.HTTP_400_BAD_REQUEST); 

    def put(self, request, id): 

        try: 

            tratamiento = Tratamiento.objects.get(uuid=id); 
            serializer = TratamientoSerializer(tratamiento, data=request.data);

            if serializer.is_valid(): 

                serializer.save();

                return Response({ 
                    'message': 'Tratamiento actualizado exitosamente', 
                    'status': 200, 
                }, status=status.HTTP_200_OK); 
            
            else: 
                return Response({ 
                    'error': serializer.errors, 
                    'message': 'Error al actualizar el tratamiento', 
                    'status': 400, 
                }, status=status.HTTP_400_BAD_REQUEST); 

        except Exception as e: 
            return Response({ 
                'message': 'Error al actualizar el tratamiento', 
                'error': str(e), 
                'status': 500, 
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 

    def delete(self, request, id): 

        try: 
            with transaction.atomic(): 

                tratamiento = Tratamiento.objects.get(uuid=id); 
                tratamiento.is_active = False; 
                tratamiento.save(); 

                return Response({ 
                    'message': 'Tratamiento eliminado exitosamente', 
                    'status': 200,
                }, status=status.HTTP_200_OK); 

        except Exception as e: 
            return Response({ 
                'message': 'Error al eliminar el tratamiento', 
                'error': str(e), 
                'status': 500,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 


@extend_schema(tags=['Pacientes-Tratamiento'])
class PacienteTratamientoView(APIView): 

    serializer_class = PacienteTratamientoSerializer;

    def get(self, request, id=None): 

        if id is not None : 

            try: 

                paciente_tratamiento = PacienteTratamiento.objects.get(id=id); 

                serializer = PacienteTratamientoSerializer(paciente_tratamiento); 

                return Response({ 
                    'data': serializer.data, 
                    'message': 'Paciente tratamiento obtenido exitosamente', 
                    'status': 200, 
                }, status=status.HTTP_200_OK); 
            
            except PacienteTratamiento.DoesNotExist:
                return Response({
                    'message': 'El paciente tratamiento no existe',
                    'status': 404,
                }, status=status.HTTP_404_NOT_FOUND)
            except Exception as e: 
                return Response({ 
                    'message': 'Error al obtener el paciente tratamiento', 
                    'error': str(e), 
                    'status': 500, 
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 
        
        else: 

            paciente_tratamientos = PacienteTratamiento.objects.all(); 

            serializer = PacienteTratamientoSerializer(paciente_tratamientos, many=True); 

            return Response({ 
                'data': serializer.data, 
                'message': 'Pacientes tratamientos obtenidos exitosamente', 
                'status': 200, 
            }, status=status.HTTP_200_OK); 
    
    def post(self, request): 

        try: 

            serializer = PacienteTratamientoSerializer(data=request.data); 

            if serializer.is_valid(): 
                serializer.save(); 

                return Response({ 
                    'data': serializer.data, 
                    'message': 'Paciente tratamiento creado exitosamente', 
                    'status': 201, 
                }, status=status.HTTP_201_CREATED); 
            
            else: 
                return Response({ 
                    'error': serializer.errors, 
                    'message': 'Error al crear el paciente tratamiento', 
                    'status': 400, 
                }, status=status.HTTP_400_BAD_REQUEST); 

        except Exception as e: 
            return Response({ 
                'message': 'Error al crear el paciente tratamiento', 
                'error': str(e), 
                'status': 500, 
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 
    
    def put(self, request, id): 

        try: 

            paciente_tratamiento = PacienteTratamiento.objects.get(id=id); 
            serializer = PacienteTratamientoSerializer(paciente_tratamiento, data=request.data);

            if serializer.is_valid(): 

                serializer.save();

                return Response({ 
                    'message': 'Paciente tratamiento actualizado exitosamente', 
                    'status': 200, 
                }, status=status.HTTP_200_OK); 
            
            else: 
                return Response({ 
                    'error': serializer.errors, 
                    'message': 'Error al actualizar el paciente tratamiento', 
                    'status': 400, 
                }, status=status.HTTP_400_BAD_REQUEST); 

        except PacienteTratamiento.DoesNotExist:
            return Response({
                'message': 'El paciente tratamiento no existe',
                'status': 404,
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e: 
            return Response({ 
                'message': 'Error al actualizar el paciente tratamiento', 
                'error': str(e), 
                'status': 500, 
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 
    

    def delete(self, request, id): 

        try: 

            paciente_tratamiento = PacienteTratamiento.objects.get(id=id); 
            paciente_tratamiento.is_active = False; 
            paciente_tratamiento.save();

            return Response({ 
                'message': 'Paciente tratamiento eliminado exitosamente', 
                'status': 200, 
            }, status=status.HTTP_200_OK); 

        except PacienteTratamiento.DoesNotExist:
            return Response({
                'message': 'El paciente tratamiento no existe',
                'status': 404,
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e: 
            return Response({ 
                'message': 'Error al eliminar el paciente tratamiento', 
                'error': str(e), 
                'status': 500, 
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 

@extend_schema(tags=['Tratamientos-Medicamentos'])

class TratamientoMedicamentoView(APIView): 

    serializer_class = TratamientoMedicamentoSerializer;

    def get(self, request, id=None):

        try: 
            if id is not None: 

                tratamiento_medicamento = TratamientoMedicamento.objects.get(id=id);

                serializer = TratamientoMedicamentoSerializer(tratamiento_medicamento);

                return Response({ 
                    'data': serializer.data, 
                    'message': 'Tratamiento medicamento obtenido exitosamente', 
                    'status': 200, 
                }, status=status.HTTP_200_OK); 
            
            else: 
                tratamientos_medicamentos = TratamientoMedicamento.objects.all(); 

                serializer = TratamientoMedicamentoSerializer(tratamientos_medicamentos, many=True);

                return Response({ 
                    'data': serializer.data, 
                    'message': 'Tratamientos medicamentos obtenidos exitosamente', 
                    'status': 200, 
                }, status=status.HTTP_200_OK); 
        
        except TratamientoMedicamento.DoesNotExist:
            return Response({
                'message': 'El tratamiento medicamento no existe',
                'status': 404,
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e: 
            return Response({ 
                'message': 'Error al obtener el tratamiento medicamento', 
                'error': str(e), 
                'status': 500, 
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 
    
    def post(self, request): 

        try: 

            with transaction.atomic(): 

                serializer = TratamientoMedicamentoSerializer(data=request.data);

                if serializer.is_valid(): 

                    serializer.save(); 

                    return Response({ 
                        'data': serializer.data, 
                        'message': 'Tratamiento medicamento creado exitosamente', 
                        'status': 201, 
                    }, status=status.HTTP_201_CREATED); 
                
                else: 
                    return Response({ 
                        'error': serializer.errors, 
                        'message': 'Error al crear el tratamiento medicamento', 
                        'status': 400, 
                    }, status=status.HTTP_400_BAD_REQUEST); 
        
        except Exception as e: 
            return Response({ 
                'message': 'Error al crear el tratamiento medicamento', 
                'error': str(e), 
                'status': 500, 
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR); 
    

    def put(self, request, id): 

        try: 
            with transaction.atomic(): 

                tratamiento_medicamento = TratamientoMedicamento.objects.get(id=id); 
                
                serializer = TratamientoMedicamentoSerializer(tratamiento_medicamento, data=request.data);

                if serializer.is_valid(): 
                    serializer.save();
                    return Response({ 
                        'message': 'Tratamiento medicamento actualizado exitosamente', 
                        'status': 200, 
                    }, status=status.HTTP_200_OK); 
                
                else: 
                    return Response({ 
                        'error': serializer.errors, 
                        'message': 'Error al actualizar el tratamiento medicamento', 
                        'status': 400, 
                    }, status=status.HTTP_400_BAD_REQUEST); 
        
        except TratamientoMedicamento.DoesNotExist:
            return Response({
                'message': 'El tratamiento medicamento no existe',
                'status': 404,
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e: 
            return Response({ 
                'message': 'Error al actualizar el tratamiento medicamento', 
                'error': str(e), 
                'status': 500, 
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR);

    def delete(self, request, id):
        try:
            with transaction.atomic():
                tratamiento_medicamento = TratamientoMedicamento.objects.get(id=id)
                # O un borrado físico, o borrado lógico si la tabla tuviera is_active
                tratamiento_medicamento.delete() 

                return Response({
                    'message': 'Tratamiento medicamento eliminado exitosamente',
                    'status': 200,
                }, status=status.HTTP_200_OK)

        except TratamientoMedicamento.DoesNotExist:
            return Response({
                'message': 'El tratamiento medicamento no existe',
                'status': 404,
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': 'Error al eliminar el tratamiento medicamento',
                'error': str(e),
                'status': 500,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            