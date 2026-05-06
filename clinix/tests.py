from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from .models import Medicamento, Tratamiento, PacienteTratamiento, TratamientoMedicamento
from .serializers import MedicamentoSerializer, TratamientoSerializer, PacienteTratamientoSerializer, TratamientoMedicamentoSerializer

class MedicamentoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.medicamento1 = Medicamento.objects.create(nombre_medicamento="Paracetamol", descripcion="Analgésico y antipirético")
        self.medicamento2 = Medicamento.objects.create(nombre_medicamento="Amoxicilina", descripcion="Antibiótico")

    def test_medicamento_creation(self):
        """Test para crear un medicamento"""
        data = {
            "nombre_medicamento": "Ibuprofeno",
            "descripcion": "Antiinflamatorio"
        }
        response = self.client.post(reverse('medicamento-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Medicamento.objects.count(), 3)

    def test_medicamento_list(self):
        """Test para obtener la lista de medicamentos"""
        response = self.client.get(reverse('medicamento-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_medicamento_detail(self):
        """Test para obtener un medicamento por ID"""
        response = self.client.get(reverse('medicamento-detail', args=[self.medicamento1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre_medicamento'], 'Paracetamol')

    def test_medicamento_update(self):
        """Test para actualizar un medicamento"""
        data = {
            "nombre_medicamento": "Paracetamol 500mg",
            "descripcion": "Analgésico y antipirético"
        }
        response = self.client.put(reverse('medicamento-detail', args=[self.medicamento1.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Medicamento.objects.get(id=self.medicamento1.id).nombre_medicamento, 'Paracetamol 500mg')

    def test_medicamento_delete(self):
        """Test para eliminar un medicamento"""
        response = self.client.delete(reverse('medicamento-detail', args=[self.medicamento1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Medicamento.objects.count(), 1)

class TratamientoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.tratamiento1 = Tratamiento.objects.create(titulo="Tratamiento A", descripcion="Descripción A", doctor="Dr. Smith")
        self.tratamiento2 = Tratamiento.objects.create(titulo="Tratamiento B", descripcion="Descripción B", doctor="Dr. Jones")

    def test_tratamiento_creation(self):
        """Test para crear un tratamiento"""
        data = {
            "titulo": "Tratamiento C",
            "descripcion": "Descripción C",
            "doctor": "Dr. Brown"
        }
        response = self.client.post(reverse('tratamiento-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tratamiento.objects.count(), 3)

    def test_tratamiento_list(self):
        """Test para obtener la lista de tratamientos"""
        response = self.client.get(reverse('tratamiento-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_tratamiento_detail(self):
        """Test para obtener un tratamiento por ID"""
        response = self.client.get(reverse('tratamiento-detail', args=[self.tratamiento1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], 'Tratamiento A')

    def test_tratamiento_update(self):
        """Test para actualizar un tratamiento"""
        data = {
            "titulo": "Tratamiento A Actualizado",
            "descripcion": "Descripción A",
            "doctor": "Dr. Smith"
        }
        response = self.client.put(reverse('tratamiento-detail', args=[self.tratamiento1.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Tratamiento.objects.get(id=self.tratamiento1.id).titulo, 'Tratamiento A Actualizado')

    def test_tratamiento_delete(self):
        """Test para eliminar un tratamiento"""
        response = self.client.delete(reverse('tratamiento-detail', args=[self.tratamiento1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tratamiento.objects.count(), 1)

class PacienteTratamientoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.tratamiento1 = Tratamiento.objects.create(titulo="Tratamiento A", descripcion="Descripción A", doctor="Dr. Smith")
        self.paciente_tratamiento1 = PacienteTratamiento.objects.create(paciente="Paciente 1", tratamiento=self.tratamiento1)
        self.paciente_tratamiento2 = PacienteTratamiento.objects.create(paciente="Paciente 2", tratamiento=self.tratamiento1)

    def test_paciente_tratamiento_creation(self):
        """Test para crear un registro de paciente-tratamiento"""
        data = {
            "paciente": "Paciente 3",
            "tratamiento": self.tratamiento1.id
        }
        response = self.client.post(reverse('paciente-tratamiento-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PacienteTratamiento.objects.count(), 3)

    def test_paciente_tratamiento_list(self):
        """Test para obtener la lista de registros de paciente-tratamiento"""
        response = self.client.get(reverse('paciente-tratamiento-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_paciente_tratamiento_detail(self):
        """Test para obtener un registro de paciente-tratamiento por ID"""
        response = self.client.get(reverse('paciente-tratamiento-detail', args=[self.paciente_tratamiento1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['paciente'], 'Paciente 1')

    def test_paciente_tratamiento_update(self):
        """Test para actualizar un registro de paciente-tratamiento"""
        data = {
            "paciente": "Paciente 1 Actualizado",
            "tratamiento": self.tratamiento1.id
        }
        response = self.client.put(reverse('paciente-tratamiento-detail', args=[self.paciente_tratamiento1.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PacienteTratamiento.objects.get(id=self.paciente_tratamiento1.id).paciente, 'Paciente 1 Actualizado')

    def test_paciente_tratamiento_delete(self):
        """Test para eliminar un registro de paciente-tratamiento"""
        response = self.client.delete(reverse('paciente-tratamiento-detail', args=[self.paciente_tratamiento1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PacienteTratamiento.objects.count(), 1)

class TratamientoMedicamentoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.tratamiento1 = Tratamiento.objects.create(titulo="Tratamiento A", descripcion="Descripción A", doctor="Dr. Smith")
        self.medicamento1 = Medicamento.objects.create(nombre_medicamento="Paracetamol", descripcion="Analgésico y antipirético")
        self.tratamiento_medicamento1 = TratamientoMedicamento.objects.create(
            tratamiento=self.tratamiento1, 
            medicamento=self.medicamento1, 
            dosis="500mg", 
            frecuencia="Cada 8 horas", 
            duracion="10 días"
        )
        self.tratamiento_medicamento2 = TratamientoMedicamento.objects.create(
            tratamiento=self.tratamiento1, 
            medicamento=self.medicamento1, 
            dosis="1000mg", 
            frecuencia="Cada 12 horas", 
            duracion="7 días"
        )

    def test_tratamiento_medicamento_creation(self):
        """Test para crear un registro de tratamiento-medicamento"""
        data = {
            "tratamiento": self.tratamiento1.id,
            "medicamento": self.medicamento1.id,
            "dosis": "250mg",
            "frecuencia": "Cada 6 horas",
            "duracion": "14 días"
        }
        response = self.client.post(reverse('tratamiento-medicamento-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TratamientoMedicamento.objects.count(), 3)

    def test_tratamiento_medicamento_list(self):
        """Test para obtener la lista de registros de tratamiento-medicamento"""
        response = self.client.get(reverse('tratamiento-medicamento-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_tratamiento_medicamento_detail(self):
        """Test para obtener un registro de tratamiento-medicamento por ID"""
        response = self.client.get(reverse('tratamiento-medicamento-detail', args=[self.tratamiento_medicamento1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['dosis'], '500mg')

    def test_tratamiento_medicamento_update(self):
        """Test para actualizar un registro de tratamiento-medicamento"""
        data = {
            "tratamiento": self.tratamiento1.id,
            "medicamento": self.medicamento1.id,
            "dosis": "500mg",
            "frecuencia": "Cada 8 horas",
            "duracion": "12 días"
        }
        response = self.client.put(reverse('tratamiento-medicamento-detail', args=[self.tratamiento_medicamento1.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TratamientoMedicamento.objects.get(id=self.tratamiento_medicamento1.id).duracion, '12 días')

    def test_tratamiento_medicamento_delete(self):
        """Test para eliminar un registro de tratamiento-medicamento"""
        response = self.client.delete(reverse('tratamiento-medicamento-detail', args=[self.tratamiento_medicamento1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TratamientoMedicamento.objects.count(), 1)

class SerializerValidationTests(TestCase):
    def test_medicamento_serializer_validations(self):
        """Test de validaciones en el serializador de medicamentos"""
        # Prueba con nombre vacío
        data = {"nombre_medicamento": "", "descripcion": "Descripción válida"}
        serializer = MedicamentoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('nombre_medicamento', serializer.errors)
        
        # Prueba con descripción vacía
        data = {"nombre_medicamento": "Medicamento válido", "descripcion": ""}
        serializer = MedicamentoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('descripcion', serializer.errors)

    def test_tratamiento_serializer_validations(self):
        """Test de validaciones en el serializador de tratamientos"""
        # Prueba con título vacío
        data = {"titulo": "", "descripcion": "Descripción válida", "doctor": "Dr. Smith"}
        serializer = TratamientoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('titulo', serializer.errors)
        
        # Prueba con descripción vacía
        data = {"titulo": "Título válido", "descripcion": "", "doctor": "Dr. Smith"}
        serializer = TratamientoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('descripcion', serializer.errors)

    def test_paciente_tratamiento_serializer_validations(self):
        """Test de validaciones en el serializador de paciente-tratamiento"""
        # Prueba con paciente vacío
        data = {"paciente": "", "tratamiento": None}
        serializer = PacienteTratamientoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('paciente', serializer.errors)
        
        # Prueba con tratamiento vacío
        data = {"paciente": "Paciente válido", "tratamiento": None}
        serializer = PacienteTratamientoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tratamiento', serializer.errors)

    def test_tratamiento_medicamento_serializer_validations(self):
        """Test de validaciones en el serializador de tratamiento-medicamento"""
        # Prueba con dosis vacía
        data = {
            "tratamiento": None, 
            "medicamento": None, 
            "dosis": "", 
            "frecuencia": "Cada 8 horas", 
            "duracion": "10 días"
        }
        serializer = TratamientoMedicamentoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('dosis', serializer.errors)
        
        # Prueba con frecuencia vacía
        data = {
            "tratamiento": None, 
            "medicamento": None, 
            "dosis": "500mg", 
            "frecuencia": "", 
            "duracion": "10 días"
        }
        serializer = TratamientoMedicamentoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('frecuencia', serializer.errors)
        
        # Prueba con duracion vacía
        data = {
            "tratamiento": None, 
            "medicamento": None, 
            "dosis": "500mg", 
            "frecuencia": "Cada 8 horas", 
            "duracion": ""
        }
        serializer = TratamientoMedicamentoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('duracion', serializer.errors)
