
from django.urls import path, include
from .views import RegisterView, LoginView, LogoutView, RegisterDoctorView, RegisterPacienteView
urlpatterns = [ 
    path('register/', RegisterView.as_view(), name='register'),
    path('register-doctor/', RegisterDoctorView.as_view(), name='register-doctor'),
    path('register-paciente/', RegisterPacienteView.as_view(), name='register-paciente'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]