from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Usuario
from .serializers import UsuarioSerializer
from clinix.models import Doctor, Paciente;



class RegisterDoctorView(APIView): 

    @extend_schema(
        summary="Registrar un nuevo doctor",
        description="Registra un nuevo doctor en la base de datos y devuelve sus tokens de acceso y refresco.",
        request=UsuarioSerializer,
        responses={
            201: OpenApiResponse(description="Doctor creado exitosamente"),
            400: OpenApiResponse(description="Errores de validación"),
        }
    )
    def post(self, request): 

        data = request.data; 

        try: 
            with transaction.atomic(): 

                user = Usuario.objects.create_user(
                    email = data['email'], 
                    password = data['password'],
                    is_doctor = True,
                    is_paciente = False,
                ); 

                doctor = Doctor.objects.create(
                    user = user, 
                    especialidad = data['especialidad'],
                    colegiado = data['colegiado'],
                )

                refresh = RefreshToken.for_user(user);

                return Response({
                    'message': 'Doctor creado exitosamente',
                    'user_id': user.id,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED);

        except Exception as e: 
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR);

class RegisterPacienteView(APIView): 

    @extend_schema(
        summary="Registrar un nuevo paciente",
        description="Registra un nuevo paciente en la base de datos y devuelve sus tokens de acceso y refresco.",
        request=UsuarioSerializer,
        responses={
            201: OpenApiResponse(description="Paciente creado exitosamente"),
            400: OpenApiResponse(description="Errores de validación"),
        }
    )

    def post(self, request): 

        data = request.data; 
        
        try: 

            with transaction.atomic():

                user = Usuario.objects.create_user(
                    email = data['email'], 
                    password = data['password'],
                    is_doctor = False,
                    is_paciente = True,
                ); 

                paciente = Paciente.objects.create(
                    user = user, 
                    fecha_nac = data['fecha_nac'],
                    descripcion = data['descripcion'],
                    telefono = data['telefono'],
                )

                refresh = RefreshToken.for_user(user);

                return Response({
                    'message': 'Paciente creado exitosamente',
                    'user_id': user.id,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED);

        except Exception as e: 
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR);


class RegisterView(APIView):

    #permite que cualquera acceda a este endpoint sin estar logeado (por el momento)

    permission_classes = [AllowAny]; 

    @extend_schema(
        summary="Registrar un nuevo usuario",
        description="Registra un nuevo usuario en la base de datos y devuelve sus tokens de acceso y refresco.",
        request=UsuarioSerializer,
        responses={
            201: OpenApiResponse(description="Usuario creado exitosamente"),
            400: OpenApiResponse(description="Errores de validación"),
        }
    )

    def post(self, request) : 
        serializer = UsuarioSerializer(data=request.data); 

        if(serializer.is_valid()):
            user = serializer.save(); 

            refresh = RefreshToken.for_user(user); 

            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView): 
    
    permission_classes = [AllowAny]; 

    @extend_schema(
        summary="Iniciar sesión",
        description="Inicia sesión usando email y contraseña, o mediante google_id.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string"},
                    "google_id": {"type": "string"},
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Inicio de sesión exitoso"),
            400: OpenApiResponse(description="Petición incorrecta o datos faltantes"),
            401: OpenApiResponse(description="Credenciales inválidas"),
            404: OpenApiResponse(description="Usuario no encontrado"),
        }
    )
    def post(self, request): 
        email = request.data.get('email'); 
        password = request.data.get('password'); 
        google_id = request.data.get('google_id'); 

        user = None; 

        if google_id: 
            try: 
                user = Usuario.objects.get(google_id=google_id);
            except Usuario.DoesNotExist:
                return Response({
                    'error': 'Usuario no encontrado',
                }, status=status.HTTP_404_NOT_FOUND)
        elif email and password: 
            user = authenticate(request, email=email, password=password); 
            if not user: 
                return Response({
                    'error': 'Credenciales inválidas',
                }, status=status.HTTP_401_UNAUTHORIZED);
        
        else: 
            return Response({
                'error': 'Debes proveer email/password o google_id',
            }, status=status.HTTP_400_BAD_REQUEST);
        
        if user: 
            refresh = RefreshToken.for_user(user); 
            serializer = UsuarioSerializer(user);
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

            

class LogoutView(APIView): 
    permission_classes = [IsAuthenticated]; 

    @extend_schema(
        summary="Cerrar sesión",
        description="Cierra la sesión del usuario invalidando el token de refresco (blacklist). Requiere autenticación con JWT.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "description": "Token de refresco a invalidar"}
                },
                "required": ["refresh"]
            }
        },
        responses={
            200: OpenApiResponse(description="Logout exitoso"),
            400: OpenApiResponse(description="Token de refresco no proveído"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def post(self, request): 
        try: 
            refresh_token = request.data.get('refresh');
            if not refresh_token: 
                return Response({
                    'error': 'Token no proveido',
                }, status=status.HTTP_400_BAD_REQUEST);
            
            token = RefreshToken(refresh_token)
            token.blacklist();
            return Response({'message': 'Logout exitoso'}, status=status.HTTP_200_OK)
        except Exception as e: 
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR);