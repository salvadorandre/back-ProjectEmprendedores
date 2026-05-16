
from rest_framework.decorators import permission_classes
from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction; 
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import TratamientoSerializer, MedicamentoSerializer, PacienteTratamientoSerializer, TratamientoMedicamentoSerializer
from .models import Medicamento, Tratamiento, PacienteTratamiento, TratamientoMedicamento, RegistroMedication, Paciente, Doctor
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers
#Integracion de los endpoints para el manejo de las citas 

# Endpoint para los medicamentos 

@extend_schema(tags=['Medicamentos'])
class MedicamentoView(APIView): 
    permission_classes = [IsAuthenticated]
    serializer_class = MedicamentoSerializer


    @extend_schema(
        summary="Obtener todos los medicamentos o uno por ID",
        description="Si se envía un ID en la URL, retorna un solo medicamento. Si no, retorna todos los medicamentos.",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID del medicamento (opcional)",
                required=False
            ),
        ],
        responses={
            200: OpenApiResponse(description="Medicamento(s) obtenido(s) exitosamente"),
            404: OpenApiResponse(description="El medicamento no existe"),
        }
    )
    def get(self, request, id=None): 
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return Response({
                'error': 'El usuario no tiene un perfil de doctor asociado',
                'status': 403
            }, status=status.HTTP_403_FORBIDDEN)

        # Si envían un ID, retornamos un solo elemento
        if id is not None:
            try:
                doctor = request.user.doctor;
                med = Medicamento.objects.get(id=id, doctor = doctor, is_active=True);
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
                    'error': 'El medicamento no existe o no tienes permiso para verlo',
                    'status': 404
                }, status=status.HTTP_404_NOT_FOUND)

        # Si NO envían un ID, listamos solo los del doctor logueado
        medicamentos = Medicamento.objects.filter(doctor=doctor)
        data = []

        for med in medicamentos: 
            data.append({
                'id': med.id, 
                'doctor': med.doctor.id, 
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
        description="Crea un nuevo medicamento. Enviar como form-data si incluye imagen, o JSON sin imagen.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "doctor": {"type": "integer", "description": "ID del doctor propietario", "example": 1},
                    "nombre_medicamento": {"type": "string", "description": "Nombre del medicamento (max 20 caracteres)", "example": "Paracetamol 500mg"},
                    "descripcion": {"type": "string", "description": "Descripción del medicamento", "example": "Analgésico y antipirético para dolor leve a moderado"},
                    "imagen": {"type": "string", "format": "binary", "description": "Imagen del medicamento (opcional)"},
                    "is_active": {"type": "boolean", "description": "Estado activo (default: true)", "example": True}
                },
                "required": ["doctor", "nombre_medicamento", "descripcion"]
            }
        },
        responses={
            201: OpenApiResponse(description="Medicamento creado exitosamente"),
            400: OpenApiResponse(description="Error de validación en los datos"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def post(self, request): 

        data = request.data;
        
        try:
            with transaction.atomic(): 

                # Solo el doctor es el dueño de sus medicamentos 
                doctor = request.user.doctor;
                data['doctor'] = doctor.id;
                
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
        summary="Actualizar un medicamento por ID",
        description="Actualiza los campos de un medicamento existente. Se debe enviar el ID en la URL.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID del medicamento a actualizar", required=True),
        ],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "nombre_medicamento": {"type": "string", "example": "Ibuprofeno 400mg"},
                    "descripcion": {"type": "string", "example": "Antiinflamatorio no esteroideo"},
                    "imagen": {"type": "string", "format": "binary", "description": "Nueva imagen del medicamento"}
                },
                "required": ["nombre_medicamento", "descripcion", "imagen"]
            }
        },
        responses={
            200: OpenApiResponse(description="Medicamento actualizado exitosamente"),
            500: OpenApiResponse(description="Error al actualizar (medicamento no encontrado u otro error)"),
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
        summary="Eliminar un medicamento (borrado lógico)",
        description="Realiza un borrado lógico del medicamento (is_active=False). No lo elimina de la base de datos.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID del medicamento a eliminar", required=True),
        ],
        responses={
            200: OpenApiResponse(description="Medicamento eliminado exitosamente"),
            500: OpenApiResponse(description="Error al eliminar el medicamento"),
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
    permission_classes = [IsAuthenticated]    
    serializer_class = TratamientoSerializer

    @extend_schema(
        summary="Obtener todos los tratamientos o uno por UUID",
        description="Si se envía un UUID en la URL, retorna un solo tratamiento. Si no, retorna todos.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.UUID, location=OpenApiParameter.PATH, description="UUID del tratamiento (opcional)", required=False),
        ],
        responses={
            200: OpenApiResponse(description="Tratamiento(s) obtenido(s) exitosamente"),
            404: OpenApiResponse(description="El tratamiento no existe"),
        }
    )
    def get(self, request, id=None): 
        if id is not None: 
            try: 
                doctor = request.user.doctor;
                tratamiento = Tratamiento.objects.get(uuid=id, doctor=doctor, is_active=True) 
                
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

    
    @extend_schema(
        summary="Crear un nuevo tratamiento",
        description="Crea un nuevo tratamiento asociado a un doctor.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "doctor": {"type": "integer", "description": "ID del doctor que crea el tratamiento", "example": 1},
                    "titulo": {"type": "string", "description": "Título del tratamiento (max 20 caracteres)", "example": "Tratamiento Cardio"},
                    "descripcion": {"type": "string", "description": "Descripción detallada del tratamiento", "example": "Tratamiento para pacientes con problemas cardíacos leves"}
                },
                "required": ["doctor", "titulo", "descripcion"]
            }
        },
        responses={
            201: OpenApiResponse(description="Tratamiento creado exitosamente"),
            400: OpenApiResponse(description="Error de validación en los datos"),
        }
    )
    def post(self, request): 

        #validar con el serializador 

        data = request.data; 

        # Solo el doctor es el dueño de sus tratamientos 
        doctor = request.user.doctor; 
        data['doctor'] = doctor.id; 

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

    @extend_schema(
        summary="Actualizar un tratamiento por UUID",
        description="Actualiza los campos de un tratamiento existente. Se debe enviar el UUID en la URL.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.UUID, location=OpenApiParameter.PATH, description="UUID del tratamiento a actualizar", required=True),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "doctor": {"type": "integer", "description": "ID del doctor", "example": 1},
                    "titulo": {"type": "string", "example": "Tratamiento Actualizado"},
                    "descripcion": {"type": "string", "example": "Descripción actualizada del tratamiento"}
                },
                "required": ["doctor", "titulo", "descripcion"]
            }
        },
        responses={
            200: OpenApiResponse(description="Tratamiento actualizado exitosamente"),
            400: OpenApiResponse(description="Error de validación"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
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

    @extend_schema(
        summary="Eliminar un tratamiento (borrado lógico)",
        description="Desactiva un tratamiento (is_active=False). No lo elimina de la base de datos.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.UUID, location=OpenApiParameter.PATH, description="UUID del tratamiento a eliminar", required=True),
        ],
        responses={
            200: OpenApiResponse(description="Tratamiento eliminado exitosamente"),
            500: OpenApiResponse(description="Error al eliminar el tratamiento"),
        }
    )
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
    permission_classes = [IsAuthenticated]
    serializer_class = PacienteTratamientoSerializer;

    @extend_schema(
        summary="Obtener asignaciones paciente-tratamiento",
        description="Si se envía un ID, retorna una sola asignación. Si no, retorna todas.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID de la asignación paciente-tratamiento (opcional)", required=False),
        ],
        responses={
            200: OpenApiResponse(description="Asignación(es) obtenida(s) exitosamente"),
            404: OpenApiResponse(description="La asignación no existe"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
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
    
    @extend_schema(
        summary="Crear una asignación paciente-tratamiento",
        description="Asocia un paciente con un tratamiento existente.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "paciente": {"type": "integer", "description": "ID del paciente", "example": 1},
                    "tratamiento": {"type": "string", "format": "uuid", "description": "UUID del tratamiento", "example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
                    "is_active": {"type": "boolean", "description": "Estado activo (default: true)", "example": True}
                },
                "required": ["paciente", "tratamiento"]
            }
        },
        responses={
            201: OpenApiResponse(description="Asignación creada exitosamente"),
            400: OpenApiResponse(description="Error de validación"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
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
    
    @extend_schema(
        summary="Actualizar una asignación paciente-tratamiento",
        description="Actualiza una asignación existente por su ID.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID de la asignación a actualizar", required=True),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "paciente": {"type": "integer", "description": "ID del paciente", "example": 1},
                    "tratamiento": {"type": "string", "format": "uuid", "description": "UUID del tratamiento", "example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
                    "is_active": {"type": "boolean", "description": "Estado activo", "example": True}
                },
                "required": ["paciente", "tratamiento"]
            }
        },
        responses={
            200: OpenApiResponse(description="Asignación actualizada exitosamente"),
            400: OpenApiResponse(description="Error de validación"),
            404: OpenApiResponse(description="La asignación no existe"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
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
    

    @extend_schema(
        summary="Eliminar asignación paciente-tratamiento (borrado lógico)",
        description="Desactiva la asignación (is_active=False). No la elimina de la base de datos.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID de la asignación a eliminar", required=True),
        ],
        responses={
            200: OpenApiResponse(description="Asignación eliminada exitosamente"),
            404: OpenApiResponse(description="La asignación no existe"),
            500: OpenApiResponse(description="Error al eliminar"),
        }
    )
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
    permission_classes = [IsAuthenticated]; 
    serializer_class = TratamientoMedicamentoSerializer;

    @extend_schema(
        summary="Obtener asignaciones tratamiento-medicamento",
        description="Si se envía un ID, retorna una sola asignación. Si no, retorna todas.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID de la asignación (opcional)", required=False),
        ],
        responses={
            200: OpenApiResponse(description="Asignación(es) obtenida(s) exitosamente"),
            404: OpenApiResponse(description="La asignación no existe"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
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
    
    @extend_schema(
        summary="Crear una asignación tratamiento-medicamento",
        description="Asocia un medicamento a un tratamiento con dosis, horario e instrucciones.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "tratamiento": {"type": "string", "format": "uuid", "description": "UUID del tratamiento", "example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
                    "medicamento": {"type": "integer", "description": "ID del medicamento", "example": 1},
                    "dosis": {"type": "string", "description": "Dosis del medicamento (max 20 caracteres)", "example": "500mg"},
                    "frecuencia": {"type": "string", "description": "Frecuencia de toma (max 30 caracteres)", "example": "Diario"},
                    "horario": {"type": "string", "description": "Horario de toma (max 20 caracteres)", "example": "Cada 8 horas"},
                    "instrucciones": {"type": "string", "description": "Instrucciones de uso", "example": "Tomar después de cada comida con un vaso de agua"}
                },
                "required": ["tratamiento", "medicamento", "dosis", "frecuencia", "horario", "instrucciones"]
            }
        },
        responses={
            201: OpenApiResponse(description="Asignación creada exitosamente"),
            400: OpenApiResponse(description="Error de validación"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
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
    

    @extend_schema(
        summary="Actualizar una asignación tratamiento-medicamento",
        description="Actualiza una asignación existente por su ID.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID de la asignación a actualizar", required=True),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "tratamiento": {"type": "string", "format": "uuid", "description": "UUID del tratamiento", "example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
                    "medicamento": {"type": "integer", "description": "ID del medicamento", "example": 1},
                    "dosis": {"type": "string", "example": "1000mg"},
                    "frecuencia": {"type": "string", "example": "Cada 12 horas"},
                    "horario": {"type": "string", "example": "Cada 12 horas"},
                    "instrucciones": {"type": "string", "example": "Tomar en ayunas"}
                },
                "required": ["tratamiento", "medicamento", "dosis", "frecuencia", "horario", "instrucciones"]
            }
        },
        responses={
            200: OpenApiResponse(description="Asignación actualizada exitosamente"),
            400: OpenApiResponse(description="Error de validación"),
            404: OpenApiResponse(description="La asignación no existe"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
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

    @extend_schema(
        summary="Eliminar asignación tratamiento-medicamento (borrado físico)",
        description="Elimina permanentemente la relación entre un tratamiento y un medicamento.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID de la asignación a eliminar", required=True),
        ],
        responses={
            200: OpenApiResponse(description="Asignación eliminada exitosamente"),
            404: OpenApiResponse(description="La asignación no existe"),
            500: OpenApiResponse(description="Error al eliminar"),
        }
    )
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

@extend_schema(tags=['Dashboard Paciente'])
class DashboardPacienteView(APIView):
    """
    Vista para el Dashboard del Paciente.
    Muestra un resumen de tratamientos activos, medicación de hoy y próxima dosis.
    Solo accesible por el propio paciente o administradores.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obtener métricas diarias y resumen del paciente",
        description="Retorna un resumen ejecutivo para el dashboard del paciente, incluyendo adherencia diaria y próxima dosis.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID del paciente", required=True),
        ],
        responses={
            200: inline_serializer(
                name='DashboardPacienteResponse',
                fields={
                    'nombre': serializers.CharField(),
                    'tratamientos_activos': serializers.IntegerField(),
                    'medicamentos_hoy': serializers.IntegerField(),
                    'medicamentos_tomados_hoy': serializers.IntegerField(),
                    'porcentaje_adherencia': serializers.IntegerField(),
                    'proxima_dosis': inline_serializer(
                        name='ProximaDosisResumen',
                        fields={
                            'medicamento': serializers.CharField(),
                            'hora': serializers.CharField()
                        },
                        allow_null=True
                    )
                }
            ),
            403: OpenApiResponse(description="No tiene permisos para ver este paciente"),
            404: OpenApiResponse(description="Paciente no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, id):
        try:
            paciente = Paciente.objects.select_related('user').get(id=id)
            
            # Validación de seguridad: solo el propio paciente o un admin
            if not request.user.is_staff and paciente.user != request.user:
                return Response({
                    "message": "No tiene permisos para acceder a los datos de este paciente",
                    "status": 403
                }, status=status.HTTP_403_FORBIDDEN)
            
            hoy = timezone.now().date()

            # 1. Tratamientos activos
            tratamientos_activos = PacienteTratamiento.objects.filter(
                paciente=paciente,
                is_active=True
            ).count()

            # 2. Medicamentos de hoy (limitado a tratamientos activos)
            active_treatment_ids = PacienteTratamiento.objects.filter(
                paciente=paciente,
                is_active=True
            ).values_list('tratamiento_id', flat=True)

            registros_hoy = RegistroMedication.objects.filter(
                paciente=paciente,
                fecha_toma=hoy,
                tratamiento_medicamento__tratamiento__in=active_treatment_ids
            )
            
            medicamentos_hoy = registros_hoy.count()
            medicamentos_tomados_hoy = registros_hoy.filter(estado='2').count()

            # 3. Porcentaje de adherencia
            porcentaje_adherencia = int((medicamentos_tomados_hoy / medicamentos_hoy) * 100) if medicamentos_hoy > 0 else 0

            # 4. Próxima dosis (solo pendientes o atrasados)
            proxima_dosis_registro = registros_hoy.filter(
                estado__in=['1', '3']
            ).select_related('tratamiento_medicamento__medicamento').order_by('hora').first()

            proxima_dosis = None
            if proxima_dosis_registro:
                proxima_dosis = {
                    "medicamento": proxima_dosis_registro.tratamiento_medicamento.medicamento.nombre_medicamento,
                    "hora": proxima_dosis_registro.hora.strftime("%H:%M")
                }

            # 5. Nombre
            nombre = paciente.user.email.split('@')[0].capitalize() if paciente.user.email else "Paciente"

            return Response({
                "nombre": nombre,
                "tratamientos_activos": tratamientos_activos,
                "medicamentos_hoy": medicamentos_hoy,
                "medicamentos_tomados_hoy": medicamentos_tomados_hoy,
                "porcentaje_adherencia": porcentaje_adherencia,
                "proxima_dosis": proxima_dosis
            }, status=status.HTTP_200_OK)

        except Paciente.DoesNotExist:
            return Response({"message": "Paciente no encontrado", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Error interno del servidor", "error": str(e), "status": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Paciente.DoesNotExist:
            return Response({
                "message": "Paciente no encontrado",
                "status": 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Error al obtener el dashboard del paciente",
                "error": str(e),
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Obtener tratamientos activos del paciente'])
class TratamientosActivosPacienteView(APIView): 
    """
    Lista de tratamientos actualmente activos para un paciente.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obtener los tratamientos activos del paciente",
        description="Retorna una lista con el detalle de los tratamientos que el paciente tiene actualmente activos, incluyendo médico y cantidad de medicinas.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID del paciente", required=True),
        ],
        responses={
            200: inline_serializer(
                name='TratamientosActivosResponse',
                many=True,
                fields={
                    'tratamiento_id': serializers.CharField(),
                    'titulo': serializers.CharField(),
                    'descripcion': serializers.CharField(),
                    'medicamentos': serializers.IntegerField(),
                    'doctor': serializers.CharField()
                }
            ),
            403: OpenApiResponse(description="No tiene permisos para ver este paciente"),
            404: OpenApiResponse(description="Paciente no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, id): 
        try:
            paciente = Paciente.objects.select_related('user').get(id=id)
            
            # Seguridad: IDOR check
            if not request.user.is_staff and paciente.user != request.user:
                return Response({
                    "message": "No tiene permisos para acceder a los datos de este paciente",
                    "status": 403
                }, status=status.HTTP_403_FORBIDDEN)
            
            tratamientos_activos = PacienteTratamiento.objects.filter(
                paciente=paciente,
                is_active=True
            ).select_related('tratamiento', 'tratamiento__doctor', 'tratamiento__doctor__user').prefetch_related('tratamiento__tratamientomedicamento_set')

            data = []
            for pt in tratamientos_activos: 
                tratamiento = pt.tratamiento
                doctor = tratamiento.doctor
                
                cantidad_medicamentos = tratamiento.tratamientomedicamento_set.count()
                doctor_nombre = doctor.user.email.split('@')[0].capitalize() if doctor.user.email else "Doctor"

                data.append({
                    "tratamiento_id": str(tratamiento.uuid),
                    "titulo": tratamiento.titulo,
                    "descripcion": tratamiento.descripcion,
                    "medicamentos": cantidad_medicamentos,
                    "doctor": f"Dr. {doctor_nombre}"
                })

            return Response(data, status=status.HTTP_200_OK)
            
        except Paciente.DoesNotExist: 
            return Response({"message": "Paciente no encontrado", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e: 
            return Response({"message": "Error interno del servidor", "error": str(e), "status": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Listar tratamientos de un paciente'])
class TratamientosPacienteView(APIView): 
    """
    Lista detallada de todos los tratamientos (activos e inactivos) de un paciente.
    Incluye la lista completa de medicamentos por tratamiento.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listar tratamientos de un paciente",
        description="Retorna una lista exhaustiva de todos los tratamientos asociados al paciente, incluyendo medicamentos, dosis e instrucciones.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID del paciente", required=True),
        ],
        responses={
            200: inline_serializer(
                name='TratamientosPacienteResponse',
                many=True,
                fields={
                    'titulo': serializers.CharField(),
                    'descripcion': serializers.CharField(),
                    'medicamentos': serializers.ListField(
                        child=inline_serializer(
                            name='MedicamentoDetalleSimple',
                            fields={
                                'nombre': serializers.CharField(),
                                'dosis': serializers.CharField(),
                                'horario': serializers.CharField(),
                                'instrucciones': serializers.CharField()
                            }
                        )
                    )
                }
            ),
            403: OpenApiResponse(description="No tiene permisos para ver este paciente"),
            404: OpenApiResponse(description="Paciente no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, id):
        try:
            paciente = Paciente.objects.select_related('user').get(id=id)
            
            # Seguridad: IDOR check
            if not request.user.is_staff and paciente.user != request.user:
                return Response({
                    "message": "No tiene permisos para acceder a los datos de este paciente",
                    "status": 403
                }, status=status.HTTP_403_FORBIDDEN)
            
            tratamientos_asignados = PacienteTratamiento.objects.filter(
                paciente=paciente
            ).select_related('tratamiento').prefetch_related('tratamiento__tratamientomedicamento_set__medicamento')

            data = []
            for pt in tratamientos_asignados: 
                tratamiento = pt.tratamiento
                medicamentos_list = []
                for tm in tratamiento.tratamientomedicamento_set.all():
                    medicamentos_list.append({
                        "nombre": tm.medicamento.nombre_medicamento,
                        "dosis": tm.dosis,
                        "horario": tm.horario,
                        "instrucciones": tm.instrucciones
                    })

                data.append({
                    "titulo": tratamiento.titulo,
                    "descripcion": tratamiento.descripcion,
                    "medicamentos": medicamentos_list
                })

            return Response(data, status=status.HTTP_200_OK)
            
        except Paciente.DoesNotExist:
            return Response({"message": "Paciente no encontrado", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Error interno del servidor", "error": str(e), "status": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Historial de Medicación'])
class HistorialMedicacionView(APIView):
    """
    Historial reciente de tomas de medicamentos.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obtener historial de medicación del paciente",
        description="Retorna los últimos 20 registros de medicación con fecha, periodo del día (Mañana, Tarde, Noche) y estado de completación.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID del paciente", required=True),
        ],
        responses={
            200: inline_serializer(
                name='HistorialMedicacionResponse',
                many=True,
                fields={
                    'medicationName': serializers.CharField(),
                    'completedAt': serializers.CharField(),
                    'period': serializers.CharField(),
                    'completed': serializers.BooleanField(),
                    'scheduledTime': serializers.CharField()
                }
            ),
            403: OpenApiResponse(description="No tiene permisos para ver este paciente"),
            404: OpenApiResponse(description="Paciente no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, id):
        try:
            paciente = Paciente.objects.select_related('user').get(id=id)

            # Seguridad: IDOR check
            if not request.user.is_staff and paciente.user != request.user:
                return Response({
                    "message": "No tiene permisos para acceder a los datos de este paciente",
                    "status": 403
                }, status=status.HTTP_403_FORBIDDEN)

            queryset = RegistroMedication.objects.filter(
                paciente=paciente
            ).select_related(
                'tratamiento_medicamento__medicamento',
                'tratamiento_medicamento__tratamiento'
            ).order_by('-fecha_toma', '-hora')[:20]

            data = []
            for registro in queryset:
                tm = registro.tratamiento_medicamento
                hora = registro.hora
                completed = str(registro.estado) == '2'

                if 0 <= hora.hour < 12:
                    period = "Mañana"
                elif 12 <= hora.hour < 18:
                    period = "Tarde"
                else:
                    period = "Noche"

                data.append({
                    "medicationName": tm.medicamento.nombre_medicamento,
                    "completedAt": f"{registro.fecha_toma} {registro.hora}",
                    "period": period,
                    "completed": completed,
                "message": "Paciente no encontrado",
                "status": 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Error al obtener el historial",
                "error": str(e),
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Estadísticas de Adherencia'])
class EstadisticaAdherenciaView(APIView):
    """
    Estadísticas de adherencia del paciente.
    Proporciona un porcentaje global y desglosado por tratamiento.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obtener estadística de adherencia del paciente",
        description="Calcula el porcentaje de adherencia global y por cada tratamiento activo asignado al paciente.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID del paciente", required=True),
        ],
        responses={
            200: inline_serializer(
                name='EstadisticaAdherenciaResponse',
                fields={
                    'global': serializers.IntegerField(help_text="Porcentaje de adherencia total"),
                    'por_tratamiento': serializers.ListField(
                        child=inline_serializer(
                            name='AdherenciaTratamiento',
                            fields={
                                'tratamiento': serializers.CharField(),
                                'adherencia': serializers.IntegerField()
                            }
                        )
                    )
                }
            ),
            403: OpenApiResponse(description="No tiene permisos para ver este paciente"),
            404: OpenApiResponse(description="Paciente no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, id):
        try:
            paciente = Paciente.objects.select_related('user').get(id=id)

            # Seguridad: IDOR check
            if not request.user.is_staff and paciente.user != request.user:
                return Response({
                    "message": "No tiene permisos para acceder a los datos de este paciente",
                    "status": 403
                }, status=status.HTTP_403_FORBIDDEN)

            # Obtener registros y optimizar con agregación si fuera necesario, 
            # pero aquí los filtramos por tratamiento para el desglose.
            registros = RegistroMedication.objects.filter(paciente=paciente)
            total_global = registros.count()
            tomados_global = registros.filter(estado='2').count()
            adherencia_global = int((tomados_global / total_global) * 100) if total_global > 0 else 0

            # Adherencia por tratamiento activo
            tratamientos_asignados = PacienteTratamiento.objects.filter(
                paciente=paciente,
                is_active=True
            ).select_related('tratamiento')

            por_tratamiento = []
            for pt in tratamientos_asignados:
                tratamiento = pt.tratamiento
                reg_tratamiento = registros.filter(tratamiento_medicamento__tratamiento=tratamiento)
                t_total = reg_tratamiento.count()
                
                if t_total > 0:
                    t_tomados = reg_tratamiento.filter(estado='2').count()
                    adh_tratamiento = int((t_tomados / t_total) * 100)
                    por_tratamiento.append({
                        "tratamiento": tratamiento.titulo,
                        "adherencia": adh_tratamiento
                    })

            return Response({
                "global": adherencia_global,
                "por_tratamiento": por_tratamiento
            }, status=status.HTTP_200_OK)

        except Paciente.DoesNotExist:
            return Response({"message": "Paciente no encontrado", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Error interno del servidor", "error": str(e), "status": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Paciente.DoesNotExist:
            return Response({
                "message": "Paciente no encontrado",
                "status": 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Error al obtener las estadísticas de adherencia",
                "error": str(e),
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Dashboard Doctor'])
class DashboardDoctorView(APIView):
    """
    Vista para el Dashboard del Doctor.
    Muestra métricas globales del médico autenticado.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Dashboard general del doctor",
        description="Retorna métricas consolidadas del doctor autenticado: pacientes únicos, tratamientos activos, medicamentos creados y adherencia promedio global.",
        responses={
            200: inline_serializer(
                name='DashboardDoctorResponse',
                fields={
                    'pacientes_totales': serializers.IntegerField(),
                    'tratamientos_activos': serializers.IntegerField(),
                    'medicamentos_creados': serializers.IntegerField(),
                    'promedio_adherencia': serializers.IntegerField()
                }
            ),
            404: OpenApiResponse(description="Doctor no encontrado"),
            500: OpenApiResponse(description="Error interno"),
        }
    )
    def get(self, request):
        try:
            from .models import Doctor
            doctor = Doctor.objects.get(user=request.user)

            # 1. Pacientes totales (pacientes únicos con tratamientos de este doctor)
            pacientes_totales = Paciente.objects.filter(
                pacientetratamiento__tratamiento__doctor=doctor
            ).distinct().count()

            # 2. Tratamientos activos
            tratamientos_activos = PacienteTratamiento.objects.filter(
                tratamiento__doctor=doctor,
                is_active=True
            ).count()

            # 3. Medicamentos creados
            medicamentos_creados = Medicamento.objects.filter(doctor=doctor).count()

            # 4. Promedio adherencia global del doctor
            registros = RegistroMedication.objects.filter(
                tratamiento_medicamento__tratamiento__doctor=doctor
            )
            stats = registros.aggregate(
                total=Count('id'),
                tomados=Count('id', filter=Q(estado='2'))
            )
            
            total_registros = stats['total']
            tomados = stats['tomados']
            promedio_adherencia = int((tomados / total_registros) * 100) if total_registros > 0 else 0

            return Response({
                "pacientes_totales": pacientes_totales,
                "tratamientos_activos": tratamientos_activos,
                "medicamentos_creados": medicamentos_creados,
                "promedio_adherencia": promedio_adherencia
            }, status=status.HTTP_200_OK)

        except Doctor.DoesNotExist:
            return Response({"message": "El usuario no tiene un perfil de doctor", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Error interno del servidor", "error": str(e), "status": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Doctor - Pacientes'])
class PacientesDoctorView(APIView):
    """
    Lista de pacientes asociados al doctor.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Lista de pacientes del doctor con resumen",
        description="Retorna los pacientes asociados al doctor, junto con un resumen de sus tratamientos activos y adherencia promedio en los mismos.",
        responses={
            200: inline_serializer(
                name='PacientesDoctorResponse',
                many=True,
                fields={
                    'id': serializers.IntegerField(),
                    'nombre': serializers.CharField(),
                    'tratamientos_activos': serializers.IntegerField(),
                    'adherencia': serializers.IntegerField()
                }
            ),
            404: OpenApiResponse(description="Doctor no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request):
        try:
            from .models import Doctor, Paciente, PacienteTratamiento, RegistroMedication
            doctor = Doctor.objects.get(user=request.user)

            # Pacientes únicos asociados al doctor
            pacientes = Paciente.objects.filter(
                pacientetratamiento__tratamiento__doctor=doctor
            ).distinct().select_related('user')

            data = []
            for paciente in pacientes:
                # Tratamientos activos con ESTE doctor
                t_activos = PacienteTratamiento.objects.filter(
                    paciente=paciente,
                    tratamiento__doctor=doctor,
                    is_active=True
                ).count()

                # Adherencia (solo registros vinculados a tratamientos del doctor)
                regs = RegistroMedication.objects.filter(
                    paciente=paciente,
                    tratamiento_medicamento__tratamiento__doctor=doctor
                ).aggregate(
                    total=Count('id'),
                    tomados=Count('id', filter=Q(estado='2'))
                )
                
                total = regs['total']
                tomados = regs['tomados']
                adherencia = int((tomados / total) * 100) if total > 0 else 0

                nombre = paciente.user.email.split('@')[0].capitalize() if paciente.user.email else "Paciente"
                
                data.append({
                    "id": paciente.id,
                    "nombre": nombre,
                    "tratamientos_activos": t_activos,
                    "adherencia": adherencia
                })

            return Response(data, status=status.HTTP_200_OK)

        except Doctor.DoesNotExist:
            return Response({"message": "El usuario no tiene un perfil de doctor", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Error interno del servidor", "error": str(e), "status": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReportePacienteDoctorView(APIView):
    """
    Reporte clínico de un paciente para el doctor.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Reporte detallado de un paciente",
        description="Devuelve el detalle de los tratamientos y últimos registros médicos de un paciente asociado al doctor.",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID del paciente", required=True),
        ],
        responses={
            200: inline_serializer(
                name='ReportePacienteDoctorResponse',
                fields={
                    'paciente': serializers.CharField(),
                    'tratamientos': serializers.ListField(
                        child=inline_serializer(
                            name='AdherenciaTratamientoReporte',
                            fields={
                                'titulo': serializers.CharField(),
                                'adherencia': serializers.IntegerField()
                            }
                        )
                    ),
                    'ultimos_registros': serializers.ListField(
                        child=inline_serializer(
                            name='UltimoRegistroMedicacion',
                            fields={
                                'medicamento': serializers.CharField(),
                                'fecha': serializers.CharField(),
                                'tomado': serializers.BooleanField()
                            }
                        )
                    )
                }
            ),
            403: OpenApiResponse(description="El paciente no está asociado a este doctor"),
            404: OpenApiResponse(description="Paciente o Doctor no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, id):
        try:
            from .models import Doctor, Paciente, PacienteTratamiento, RegistroMedication
            doctor = Doctor.objects.get(user=request.user)
            paciente = Paciente.objects.get(id=id)

            # Validar asociación
            pt_asignados = PacienteTratamiento.objects.filter(
                paciente=paciente,
                tratamiento__doctor=doctor
            ).select_related('tratamiento')

            if not pt_asignados.exists():
                return Response({"message": "El paciente no está asociado a este doctor", "status": 403}, status=status.HTTP_403_FORBIDDEN)

            # 1. Nombre
            nombre = paciente.user.email.split('@')[0].capitalize() if paciente.user.email else "Paciente"

            # 2. Tratamientos y adherencia
            tratamientos_data = []
            registros_doctor = RegistroMedication.objects.filter(
                paciente=paciente,
                tratamiento_medicamento__tratamiento__doctor=doctor
            )

            for pt in pt_asignados:
                tratamiento = pt.tratamiento
                regs = registros_doctor.filter(tratamiento_medicamento__tratamiento=tratamiento).aggregate(
                    total=Count('id'),
                    tomados=Count('id', filter=Q(estado='2'))
                )
                
                total = regs['total']
                tomados = regs['tomados']
                adherencia = int((tomados / total) * 100) if total > 0 else 0
                
                tratamientos_data.append({
                    "titulo": tratamiento.titulo,
                    "adherencia": adherencia
                })

            # 3. Últimos 5 registros
            ultimos_registros = registros_doctor.select_related('tratamiento_medicamento__medicamento').order_by('-fecha_toma', '-hora')[:5]
            
            ultimos_data = []
            for r in ultimos_registros:
                ultimos_data.append({
                    "medicamento": r.tratamiento_medicamento.medicamento.nombre_medicamento,
                    "fecha": r.fecha_toma.strftime("%Y-%m-%d"),
                    "tomado": str(r.estado) == '2'
                })

            return Response({
                "paciente": nombre,
                "tratamientos": tratamientos_data,
                "ultimos_registros": ultimos_data
            }, status=status.HTTP_200_OK)

        except Doctor.DoesNotExist:
            return Response({"message": "El usuario no es un doctor", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Paciente.DoesNotExist:
            return Response({"message": "Paciente no encontrado", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Error al obtener el reporte", "error": str(e), "status": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Doctor.DoesNotExist:
            return Response({
                "message": "El usuario no es un doctor",
                "status": 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Paciente.DoesNotExist:
            return Response({
                "message": "Paciente no encontrado",
                "status": 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Error al obtener el reporte del paciente",
                "error": str(e),
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=["Doctor - Mis tratamientos"])
class TratamientosDoctorView(APIView):
    """
    Tratamientos creados por el médico.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Tratamientos creados por el doctor",
        description="Devuelve una lista de tratamientos creados por el doctor, con el total de pacientes asignados y su adherencia promedio en cada uno.",
        responses={
            200: inline_serializer(
                name='TratamientosDoctorResponse',
                many=True,
                fields={
                    'id': serializers.CharField(),
                    'titulo': serializers.CharField(),
                    'pacientes_asignados': serializers.IntegerField(),
                    'adherencia': serializers.IntegerField()
                }
            ),
            404: OpenApiResponse(description="Doctor no encontrado"),
            500: OpenApiResponse(description="Error interno"),
        }
    )
    def get(self, request): 
        try:
            from .models import Doctor, Tratamiento, PacienteTratamiento, RegistroMedication
            doctor = Doctor.objects.get(user=request.user)
            tratamientos = Tratamiento.objects.filter(doctor=doctor)

            data = []
            for t in tratamientos:
                p_asignados = PacienteTratamiento.objects.filter(tratamiento=t, is_active=True).count()
                
                # Adherencia por tratamiento
                stats = RegistroMedication.objects.filter(tratamiento_medicamento__tratamiento=t).aggregate(
                    total=Count('id'),
                    tomados=Count('id', filter=Q(estado='2'))
                )
                
                total = stats['total']
                tomados = stats['tomados']
                adherencia = int((tomados / total) * 100) if total > 0 else 0

                data.append({
                    "id": str(t.uuid),
                    "titulo": t.titulo,
                    "pacientes_asignados": p_asignados,
                    "adherencia": adherencia
                })

            return Response(data, status=status.HTTP_200_OK)

        except Doctor.DoesNotExist:
            return Response({"message": "El usuario no tiene un perfil de doctor", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Error al obtener los tratamientos", "error": str(e), "status": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Doctor - Rendimiento por tratamientos'])
class RendimientoPorTratamientoView(APIView):
    """
    Analítica detallada por tratamiento.
    Identifica pacientes en riesgo (adherencia < 70%).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Estadísticas de un tratamiento específico",
        description="Devuelve estadísticas detalladas de un tratamiento: pacientes totales, adherencia promedio y conteo de pacientes en riesgo (< 70% adherencia).",
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.UUID, location=OpenApiParameter.PATH, description="UUID del tratamiento", required=True),
        ],
        responses={
            200: inline_serializer(
                name='RendimientoTratamientoResponse',
                fields={
                    'tratamiento': serializers.CharField(),
                    'pacientes': serializers.IntegerField(),
                    'adherencia_promedio': serializers.IntegerField(),
                    'pacientes_bajo_70': serializers.IntegerField()
                }
            ),
            404: OpenApiResponse(description="Tratamiento o Doctor no encontrado"),
            500: OpenApiResponse(description="Error interno"),
        }
    )
    def get(self, request, id): 
        try: 
            from .models import Doctor, Tratamiento, PacienteTratamiento, RegistroMedication
            doctor = Doctor.objects.get(user=request.user)
            tratamiento = Tratamiento.objects.get(uuid=id, doctor=doctor)

            asignaciones_activas = PacienteTratamiento.objects.filter(tratamiento=tratamiento, is_active=True)
            p_total = asignaciones_activas.count()

            regs_globales = RegistroMedication.objects.filter(tratamiento_medicamento__tratamiento=tratamiento)
            stats_g = regs_globales.aggregate(
                total=Count('id'),
                tomados=Count('id', filter=Q(estado='2'))
            )
            
            total_g = stats_g['total']
            tomados_g = stats_g['tomados']
            adh_promedio = int((tomados_g / total_g) * 100) if total_g > 0 else 0

            # Optimización: Obtener adherencia por paciente en una sola query
            # Filtramos por los registros del tratamiento y agrupamos por paciente
            adherencia_por_paciente = regs_globales.values('paciente').annotate(
                total_p=Count('id'),
                tomados_p=Count('id', filter=Q(estado='2'))
            )

            pacientes_en_riesgo = 0
            # Los pacientes en el tratamiento que no tienen registros aún también se consideran en riesgo o se ignoran?
            # Según lógica previa, si total_p es 0, suma 1.
            # Primero contamos los que sí tienen registros
            pacientes_con_registros = set()
            for p_stats in adherencia_por_paciente:
                total_p = p_stats['total_p']
                tomados_p = p_stats['tomados_p']
                adh_p = int((tomados_p / total_p) * 100) if total_p > 0 else 0
                if adh_p < 70:
                    pacientes_en_riesgo += 1
                pacientes_con_registros.add(p_stats['paciente'])

            # Luego sumamos los que están en el tratamiento pero no tienen registros
            # (Si p_total > len(pacientes_con_registros))
            pacientes_sin_registros = p_total - len(pacientes_con_registros)
            if pacientes_sin_registros > 0:
                pacientes_en_riesgo += pacientes_sin_registros

            return Response({
                "tratamiento": tratamiento.titulo,
                "pacientes": p_total,
                "adherencia_promedio": adh_promedio,
                "pacientes_bajo_70": pacientes_en_riesgo
            }, status=status.HTTP_200_OK)

        except Doctor.DoesNotExist:
            return Response({"message": "Perfil de doctor no encontrado", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Tratamiento.DoesNotExist:
            return Response({"message": "Tratamiento no encontrado", "status": 404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Error interno", "error": str(e), "status": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Medicación de Hoy'])
class TodayMedicationsView(APIView):
    """
    Endpoint para obtener los medicamentos programados del día actual,
    agrupados por periodo (Mañana, Tarde, Noche).
    Solo accesible por el paciente dueño del perfil o un admin.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obtener medicamentos programados para hoy",
        description=(
            "Retorna todos los medicamentos programados para el día actual del paciente, "
            "agrupados en tres periodos: Mañana (00:00-11:59), Tarde (12:00-17:59) y Noche (18:00-23:59). "
            "Cada grupo incluye un status general (Completado, Pendiente o Sin medicamentos). "
            "Solo el paciente autenticado puede consultar sus propios datos."
        ),
        parameters=[
            OpenApiParameter(
                name="patientId",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID del paciente",
                required=True
            ),
        ],
        responses={
            200: inline_serializer(
                name='TodayMedicationsResponse',
                many=True,
                fields={
                    'title': serializers.CharField(help_text="Periodo del día: Mañana, Tarde o Noche"),
                    'status': serializers.CharField(help_text="Completado, Pendiente o Sin medicamentos"),
                    'data': serializers.ListField(
                        child=inline_serializer(
                            name='MedicationItem',
                            fields={
                                'id': serializers.CharField(),
                                'title': serializers.CharField(help_text="Nombre del medicamento"),
                                'dose': serializers.CharField(help_text="Dosis asignada"),
                                'time': serializers.CharField(help_text="Hora programada (formato 12h)"),
                                'completed': serializers.BooleanField(help_text="Si el medicamento fue tomado"),
                                'doctorName': serializers.CharField(help_text="Nombre del doctor"),
                                'treatmentName': serializers.CharField(help_text="Nombre del tratamiento"),
                            }
                        )
                    ),
                }
            ),
            403: OpenApiResponse(description="No tiene permisos para ver este paciente"),
            404: OpenApiResponse(description="Paciente no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, patientId):
        try:
            paciente = Paciente.objects.select_related('user').get(id=patientId)

            # Validación de seguridad: solo el propio paciente o un admin
            if not request.user.is_staff and paciente.user != request.user:
                return Response({
                    "message": "No tiene permisos para ver los datos de este paciente",
                    "status": 403
                }, status=status.HTTP_403_FORBIDDEN)

            hoy = timezone.now().date()

            # Obtener tratamientos activos
            active_treatments = PacienteTratamiento.objects.filter(
                paciente=paciente,
                is_active=True
            ).values_list('tratamiento_id', flat=True)

            registros = RegistroMedication.objects.filter(
                paciente=paciente,
                fecha_toma=hoy,
                tratamiento_medicamento__tratamiento__in=active_treatments
            ).select_related(
                'tratamiento_medicamento__medicamento',
                'tratamiento_medicamento__tratamiento__doctor__user'
            ).order_by('hora')

            grupos = {
                "Mañana": [],
                "Tarde": [],
                "Noche": []
            }

            for registro in registros:
                tm = registro.tratamiento_medicamento
                tratamiento = tm.tratamiento

                hora_str = registro.hora.strftime("%I:%M %p")

                doctor = tratamiento.doctor
                doctor_name = doctor.user.email.split('@')[0].capitalize() if doctor.user.email else "Doctor"

                item = {
                    "id": str(registro.id),
                    "title": tm.medicamento.nombre_medicamento,
                    "dose": tm.dosis,
                    "time": hora_str,
                    "completed": str(registro.estado) == '2',
                    "doctorName": doctor_name,
                    "treatmentName": tratamiento.titulo
                }

                # Asignar al grupo según la hora
                hora = registro.hora.hour
                if 0 <= hora < 12:
                    grupos["Mañana"].append(item)
                elif 12 <= hora < 18:
                    grupos["Tarde"].append(item)
                else:
                    grupos["Noche"].append(item)

            resultado = []
            for titulo in ["Mañana", "Tarde", "Noche"]:
                datos = grupos[titulo]
                if len(datos) > 0:
                    completados = sum(1 for d in datos if d["completed"])
                    status_text = "Completado" if completados == len(datos) else "Pendiente"
                else:
                    status_text = "Sin medicamentos"

                resultado.append({
                    "title": titulo,
                    "status": status_text,
                    "data": datos
                })

            return Response(resultado, status=status.HTTP_200_OK)

        except Paciente.DoesNotExist:
            return Response({
                "message": "Paciente no encontrado",
                "status": 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Error al obtener los medicamentos de hoy",
                "error": str(e),
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Métricas de Hoy'])
class TodayMetricsView(APIView):
    """
    Endpoint para calcular las métricas diarias del paciente:
    completados, pendientes y atrasados.
    Actualiza automáticamente el estado de registros atrasados a '3'.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obtener métricas de medicamentos de hoy",
        description=(
            "Calcula en tiempo real los medicamentos completados, pendientes y atrasados "
            "del día actual. Un medicamento se considera atrasado si su hora programada "
            "ya pasó y no fue marcado como tomado. Los registros atrasados se actualizan "
            "automáticamente a estado '3' en la base de datos."
        ),
        parameters=[
            OpenApiParameter(
                name="patientId",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID del paciente",
                required=True
            ),
        ],
        responses={
            200: inline_serializer(
                name='TodayMetricsResponse',
                fields={
                    'completed': serializers.IntegerField(help_text="Medicamentos tomados"),
                    'pending': serializers.IntegerField(help_text="Medicamentos pendientes (hora no ha llegado)"),
                    'overdue': serializers.IntegerField(help_text="Medicamentos atrasados (hora ya pasó)"),
                    'total': serializers.IntegerField(help_text="Total de medicamentos del día"),
                }
            ),
            403: OpenApiResponse(description="No tiene permisos para ver este paciente"),
            404: OpenApiResponse(description="Paciente no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, patientId):
        try:
            paciente = Paciente.objects.select_related('user').get(id=patientId)

            # Validación de seguridad
            if not request.user.is_staff and paciente.user != request.user:
                return Response({
                    "message": "No tiene permisos para ver los datos de este paciente",
                    "status": 403
                }, status=status.HTTP_403_FORBIDDEN)

            ahora = timezone.now()
            fecha_actual = ahora.date()
            hora_actual = ahora.time()

            active_treatments = PacienteTratamiento.objects.filter(
                paciente=paciente,
                is_active=True
            ).values_list('tratamiento_id', flat=True)

            # Convertir a lista para evitar query extra en .count() al final
            registros_hoy = list(RegistroMedication.objects.filter(
                paciente=paciente,
                fecha_toma=fecha_actual,
                tratamiento_medicamento__tratamiento__in=active_treatments
            ))

            total = len(registros_hoy)
            completed = 0
            pending = 0
            overdue = 0

            registros_para_actualizar = []

            for registro in registros_hoy:
                if str(registro.estado) == '2':
                    completed += 1
                else:
                    if registro.hora < hora_actual:
                        overdue += 1
                        if str(registro.estado) == '1':
                            registro.estado = '3'
                            registros_para_actualizar.append(registro)
                    else:
                        pending += 1

            # Actualizar en batch los registros atrasados
            if registros_para_actualizar:
                RegistroMedication.objects.bulk_update(registros_para_actualizar, ['estado'])

            data = {
                "completed": completed,
                "pending": pending,
                "overdue": overdue,
                "total": total
            }

            return Response(data, status=status.HTTP_200_OK)

        except Paciente.DoesNotExist:
            return Response({
                "message": "Paciente no encontrado",
                "status": 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Error al obtener las métricas de hoy",
                "error": str(e),
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Cumplimiento Semanal'])
class WeeklyAdherenceView(APIView):
    """
    Endpoint para verificar la adherencia diaria del paciente
    durante la semana actual (lunes a domingo).
    Un día se considera completado si TODOS los medicamentos fueron tomados.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obtener cumplimiento semanal",
        description=(
            "Verifica la adherencia diaria durante la semana actual (lunes a domingo). "
            "Un día se marca como completado (true) si todos los medicamentos programados "
            "fueron tomados. El día actual se marca como 'current'. Los días futuros "
            "se marcan como false."
        ),
        parameters=[
            OpenApiParameter(
                name="patientId",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID del paciente",
                required=True
            ),
        ],
        responses={
            200: inline_serializer(
                name='WeeklyAdherenceResponse',
                many=True,
                fields={
                    'day': serializers.CharField(help_text="Día de la semana: LUN, MAR, MIE, JUE, VIE, SAB, DOM"),
                    'done': serializers.CharField(help_text="true si completó todo, false si no, 'current' si es hoy"),
                }
            ),
            403: OpenApiResponse(description="No tiene permisos para ver este paciente"),
            404: OpenApiResponse(description="Paciente no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, patientId):
        try:
            paciente = Paciente.objects.select_related('user').get(id=patientId)

            # Validación de seguridad
            if not request.user.is_staff and paciente.user != request.user:
                return Response({
                    "message": "No tiene permisos para ver los datos de este paciente",
                    "status": 403
                }, status=status.HTTP_403_FORBIDDEN)

            hoy = timezone.now().date()

            # Lunes de esta semana (0 = Lunes, 6 = Domingo)
            start_of_week = hoy - timedelta(days=hoy.weekday())

            active_treatments = PacienteTratamiento.objects.filter(
                paciente=paciente,
                is_active=True
            ).values_list('tratamiento_id', flat=True)

            # Convertir a lista para evitar múltiples queries al iterar por día
            registros_semana = list(RegistroMedication.objects.filter(
                paciente=paciente,
                fecha_toma__gte=start_of_week,
                fecha_toma__lt=start_of_week + timedelta(days=7),
                tratamiento_medicamento__tratamiento__in=active_treatments
            ))

            DIAS_SEMANA = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
            resultado = []

            for i in range(7):
                current_date = start_of_week + timedelta(days=i)
                day_name = DIAS_SEMANA[i]

                if current_date == hoy:
                    done_status = "current"
                elif current_date > hoy:
                    done_status = False
                else:
                    registros_dia = [r for r in registros_semana if r.fecha_toma == current_date]
                    if len(registros_dia) == 0:
                        done_status = False
                    else:
                        done_status = all(str(r.estado) == '2' for r in registros_dia)

                resultado.append({
                    "day": day_name,
                    "done": done_status
                })

            return Response(resultado, status=status.HTTP_200_OK)

        except Paciente.DoesNotExist:
            return Response({
                "message": "Paciente no encontrado",
                "status": 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Error al obtener el cumplimiento semanal",
                "error": str(e),
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Progreso Global'])
class GlobalProgressView(APIView):
    """
    Endpoint para calcular el porcentaje total de adherencia del paciente
    considerando únicamente tratamientos activos.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obtener progreso global de adherencia",
        description=(
            "Calcula el porcentaje total de adherencia del paciente considerando "
            "únicamente tratamientos activos. Divide medicamentos completados (estado '2') "
            "entre el total de registros para obtener el porcentaje."
        ),
        parameters=[
            OpenApiParameter(
                name="patientId",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID del paciente",
                required=True
            ),
        ],
        responses={
            200: inline_serializer(
                name='GlobalProgressResponse',
                fields={
                    'progress': serializers.IntegerField(help_text="Porcentaje de adherencia (0-100)"),
                    'completed': serializers.IntegerField(help_text="Total de medicamentos tomados"),
                    'total': serializers.IntegerField(help_text="Total de registros de medicación"),
                }
            ),
            403: OpenApiResponse(description="No tiene permisos para ver este paciente"),
            404: OpenApiResponse(description="Paciente no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, patientId):
        try:
            paciente = Paciente.objects.select_related('user').get(id=patientId)

            # Validación de seguridad
            if not request.user.is_staff and paciente.user != request.user:
                return Response({
                    "message": "No tiene permisos para ver los datos de este paciente",
                    "status": 403
                }, status=status.HTTP_403_FORBIDDEN)

            # Obtener solo tratamientos activos
            active_treatments = PacienteTratamiento.objects.filter(
                paciente=paciente,
                is_active=True
            ).values_list('tratamiento_id', flat=True)

            # Filtrar registros que pertenezcan a tratamientos activos
            registros = RegistroMedication.objects.filter(
                paciente=paciente,
                tratamiento_medicamento__tratamiento__in=active_treatments
            )

            total = registros.count()
            completed = registros.filter(estado='2').count()
            progress = int((completed / total) * 100) if total > 0 else 0

            data = {
                "progress": progress,
                "completed": completed,
                "total": total
            }

            return Response(data, status=status.HTTP_200_OK)

        except Paciente.DoesNotExist:
            return Response({
                "message": "Paciente no encontrado",
                "status": 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Error al obtener el progreso global",
                "error": str(e),
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Detalle de Tratamiento'])
class TreatmentDetailView(APIView):
    """
    Endpoint para obtener el detalle completo de un tratamiento
    incluyendo todos sus medicamentos asignados con dosis, horario,
    frecuencia e instrucciones.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obtener detalle completo de un tratamiento",
        description=(
            "Retorna la información del tratamiento junto con la lista completa "
            "de medicamentos asignados, incluyendo dosis, horario, frecuencia "
            "e instrucciones de cada uno."
        ),
        parameters=[
            OpenApiParameter(
                name="treatmentId",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID del tratamiento",
                required=True
            ),
        ],
        responses={
            200: inline_serializer(
                name='TreatmentDetailResponse',
                fields={
                    'treatmentId': serializers.CharField(help_text="UUID del tratamiento"),
                    'treatmentName': serializers.CharField(help_text="Nombre del tratamiento"),
                    'medications': serializers.ListField(
                        child=inline_serializer(
                            name='TreatmentMedicationDetail',
                            fields={
                                'medicationName': serializers.CharField(help_text="Nombre del medicamento"),
                                'dose': serializers.CharField(help_text="Dosis"),
                                'schedule': serializers.CharField(help_text="Horario"),
                                'frequency': serializers.CharField(help_text="Frecuencia"),
                                'instructions': serializers.CharField(help_text="Instrucciones"),
                            }
                        )
                    ),
                }
            ),
            404: OpenApiResponse(description="Tratamiento no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def get(self, request, treatmentId):
        try:
            tratamiento = Tratamiento.objects.select_related('doctor__user').get(uuid=treatmentId)

            # Obtener los medicamentos asignados a este tratamiento
            tratamiento_medicamentos = TratamientoMedicamento.objects.filter(
                tratamiento=tratamiento
            ).select_related('medicamento')

            medications = []
            for tm in tratamiento_medicamentos:
                medications.append({
                    "medicationName": tm.medicamento.nombre_medicamento,
                    "dose": tm.dosis,
                    "schedule": tm.horario,
                    "frequency": tm.frecuencia,
                    "instructions": tm.instrucciones
                })

            data = {
                "treatmentId": str(tratamiento.uuid),
                "treatmentName": tratamiento.titulo,
                "medications": medications
            }

            return Response(data, status=status.HTTP_200_OK)

        except Tratamiento.DoesNotExist:
            return Response({
                "message": "Tratamiento no encontrado",
                "status": 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Error al obtener el detalle del tratamiento",
                "error": str(e),
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Registro de Medicación'])
class MedicationRecordView(APIView):
    """
    Endpoint para registrar la toma de un medicamento.
    Soporta fotografía de evidencia y observaciones.
    Previene registros duplicados por día para el mismo medicamento.
    Valida que el tratamiento pertenezca al paciente autenticado.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Registrar completación de medicamento",
        description=(
            "Registra que un paciente tomó un medicamento. Permite adjuntar una fotografía "
            "de evidencia y observaciones opcionales. Previene duplicados verificando si ya "
            "existe un registro del mismo medicamento para el día actual. "
            "Solo el paciente autenticado puede registrar su propia medicación."
        ),
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "paciente": {"type": "integer", "description": "ID del paciente", "example": 1},
                    "tratamiento_medicamento": {"type": "integer", "description": "ID de la asignación tratamiento-medicamento", "example": 1},
                    "hora": {"type": "string", "format": "time", "description": "Hora de toma (HH:MM)", "example": "08:00"},
                    "foto": {"type": "string", "format": "binary", "description": "Fotografía de evidencia (opcional)"},
                    "observaciones": {"type": "string", "description": "Observaciones del paciente (opcional)", "example": "Tomé con el desayuno"}
                },
                "required": ["paciente", "tratamiento_medicamento", "hora"]
            }
        },
        responses={
            201: inline_serializer(
                name='MedicationRecordSuccessResponse',
                fields={
                    'success': serializers.BooleanField(),
                    'message': serializers.CharField(),
                }
            ),
            400: OpenApiResponse(description="Error de validación o registro duplicado"),
            403: OpenApiResponse(description="No tiene permisos para registrar medicación de este paciente"),
            404: OpenApiResponse(description="Paciente o tratamiento-medicamento no encontrado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def post(self, request):
        try:
            data = request.data
            paciente_id = data.get('paciente')
            tm_id = data.get('tratamiento_medicamento')
            hora = data.get('hora')

            if not paciente_id or not tm_id or not hora:
                return Response({
                    "success": False,
                    "message": "Los campos paciente, tratamiento_medicamento y hora son requeridos"
                }, status=status.HTTP_400_BAD_REQUEST)

            paciente = Paciente.objects.select_related('user').get(id=paciente_id)

            # Validación de seguridad: solo el propio paciente o un admin
            if not request.user.is_staff and paciente.user != request.user:
                return Response({
                    "success": False,
                    "message": "No tiene permisos para registrar medicación de este paciente"
                }, status=status.HTTP_403_FORBIDDEN)

            tratamiento_medicamento = TratamientoMedicamento.objects.get(id=tm_id)

            # Validar que el tratamiento pertenezca al paciente y esté activo
            tiene_tratamiento = PacienteTratamiento.objects.filter(
                paciente=paciente,
                tratamiento=tratamiento_medicamento.tratamiento,
                is_active=True
            ).exists()

            if not tiene_tratamiento:
                return Response({
                    "success": False,
                    "message": "Este medicamento no pertenece a un tratamiento activo del paciente"
                }, status=status.HTTP_400_BAD_REQUEST)

            hoy = timezone.now().date()

            # Validar duplicados: mismo paciente + mismo tratamiento_medicamento + misma fecha
            existe = RegistroMedication.objects.filter(
                paciente=paciente,
                tratamiento_medicamento=tratamiento_medicamento,
                fecha_toma=hoy
            ).exists()

            if existe:
                return Response({
                    "success": False,
                    "message": "Este medicamento ya fue registrado el día de hoy"
                }, status=status.HTTP_400_BAD_REQUEST)

            RegistroMedication.objects.create(
                paciente=paciente,
                tratamiento_medicamento=tratamiento_medicamento,
                fecha_toma=hoy,
                estado='2',  # Tomado
                hora=hora,
                foto=request.FILES.get('foto'),
                observaciones=data.get('observaciones', '')
            )

            return Response({
                "success": True,
                "message": "Medicamento registrado correctamente"
            }, status=status.HTTP_201_CREATED)

        except Paciente.DoesNotExist:
            return Response({
                "success": False,
                "message": "Paciente no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        except TratamientoMedicamento.DoesNotExist:
            return Response({
                "success": False,
                "message": "Tratamiento-medicamento no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "message": "Error al registrar el medicamento",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
