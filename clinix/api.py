
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
                    "horario": {"type": "string", "description": "Horario de toma (max 20 caracteres)", "example": "Cada 8 horas"},
                    "instrucciones": {"type": "string", "description": "Instrucciones de uso", "example": "Tomar después de cada comida con un vaso de agua"}
                },
                "required": ["tratamiento", "medicamento", "dosis", "horario", "instrucciones"]
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
                    "horario": {"type": "string", "example": "Cada 12 horas"},
                    "instrucciones": {"type": "string", "example": "Tomar en ayunas"}
                },
                "required": ["tratamiento", "medicamento", "dosis", "horario", "instrucciones"]
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

            