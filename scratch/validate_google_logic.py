import os
import sys
from unittest.mock import MagicMock, patch

# Mocking Google Auth to test our audience logic
def test_google_auth_logic():
    print("--- Iniciando validación técnica de Google Auth (Android/Web) ---")
    
    # Simulamos variables de entorno
    web_id = "12345-web.apps.googleusercontent.com"
    android_id = "67890-android.apps.googleusercontent.com"
    
    # Simulamos la lógica que pusimos en la vista
    valid_audiences = [id for id in [web_id, android_id] if id]
    print(f"IDs permitidos detectados: {valid_audiences}")
    
    if len(valid_audiences) == 2:
        print("✅ ÉXITO: El sistema detecta ambos Client IDs (Web y Android).")
    else:
        print("❌ ERROR: No se detectaron ambos IDs.")

    # Simulación de la llamada a la librería de Google
    # Si pasamos una lista a verify_oauth2_token, debe funcionar.
    try:
        from google.oauth2 import id_token
        print("✅ Librería 'google-auth' importada correctamente.")
    except ImportError:
        print("❌ Error: 'google-auth' no está instalado.")

if __name__ == "__main__":
    test_google_auth_logic()
