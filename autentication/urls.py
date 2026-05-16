
from django.urls import path, include
from .views import RegisterView, LoginView, LogoutView, RegisterDoctorView, RegisterPacienteView, GoogleAuthView, TokenRefreshView, MockLoginView
urlpatterns = [ 
    path('register/', RegisterView.as_view(), name='register'),
    path('register-doctor/', RegisterDoctorView.as_view(), name='register-doctor'),
    path('register-paciente/', RegisterPacienteView.as_view(), name='register-paciente'),
    path('login/', LoginView.as_view(), name='login'),
    path('auth/mock/', MockLoginView.as_view(), name='mock-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]