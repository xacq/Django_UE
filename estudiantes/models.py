# models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Empresa(models.Model):
    nombre_empresa = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    correo_electronico = models.CharField(max_length=100)
    representante = models.CharField(max_length=100)
    supervisor = models.CharField(max_length=100)
    ruc = models.CharField(max_length=13, default="")
    def __str__(self):
        return self.nombre_empresa

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class Tutor (models.Model):
    nombre = models.CharField(max_length=100)
    profesion = models.CharField(max_length=100)
    experiencia = models.TextField(max_length=500)
    def __str__(self):
        return self.nombre

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=10, default='0000000000')
    nombres = models.CharField(max_length=100, default='')
    apellidos=models.CharField(max_length=100, default='')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    estado_ingreso = models.CharField(max_length=20, default='Espera')
    estado_carta_aprobacion = models.CharField(max_length=20, default='Espera1')
    tutor = models.ForeignKey(Tutor, on_delete=models.SET_NULL, null=True, blank=True, related_name='perfiles')
    tutor_asignado_estado = models.CharField(max_length=20, default='Espera')
    supervisor= models.CharField(max_length=20, default='Espera1')
    ia_respuesta = models.CharField(max_length=500, default='Sin Respuesta')
    ia_estado = models.CharField(max_length=20, default='Espera')
    empresa_nombre = models.ForeignKey(Empresa, null=True, blank=True, on_delete=models.SET_NULL)
    empresa_estado = models.CharField(max_length=20, default='Espera')
    reporte_estado = models.CharField(max_length=20, default='Espera1')
    habilitado = models.BooleanField(default=True)
    reporte_numero = models.IntegerField(default=0)
    reporte_fecha_inicio = models.DateField(default=date.today)
    reporte_fecha_final = models.DateField(default=date.today)
    especializacion = models.CharField(max_length=50, default='Especializacion')
    visitas = models.IntegerField(default=0)     

    def __str__(self):
        return f'{self.user.username} - {self.rol.nombre if self.rol else "Sin rol"}'

class Formato(models.Model):
    nombre_formato = models.CharField(max_length=100)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=50)
    archivo_formato = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre
    
class CartaAceptacion(models.Model):
    estudiante_carta = models.ForeignKey(User, on_delete=models.CASCADE)
    cedula_carta = models.CharField(max_length=20)
    ano_lectivo_carta = models.CharField(max_length=10)
    fecha_subida_carta = models.DateField(auto_now_add=True)
    comentarios_rector_carta = models.TextField()
    estado_carta = models.TextField(default='Espera1')
    empresa = models.CharField(max_length=100, default='Espera')
    supervisor = models.CharField(max_length=100, default='Espera') 
    especializacion = models.CharField(max_length=50, default='Especializacion')       
    rector = models.CharField(max_length=100, default='Rector') 

    def __str__(self):
        return f"{self.estudiante_carta.username} - {self.ano_lectivo_carta}"
    
class InformeDiario(models.Model):
    entidad = models.CharField(max_length=255, blank=True)
    receptora = models.CharField(max_length=255)
    nombre_estudiante = models.CharField(max_length=255, blank=True)
    nombre_docente = models.CharField(max_length=255, blank=True)
    area_trabajo = models.CharField(max_length=255)
    fecha_inicio = models.DateField(default=date.today)
    fecha_final = models.DateField(default=date.today)
    fecha_hora_registro = models.DateTimeField(auto_now_add=True)  # Nuevo campo

    # Campos para la descripción de cada día
    lunes_actividad = models.TextField()
    lunes_dificultad = models.TextField()
    lunes_apoyo = models.TextField()
    lunes_observaciones = models.TextField()
    martes_actividad = models.TextField()
    martes_dificultad = models.TextField()
    martes_apoyo = models.TextField()
    martes_observaciones = models.TextField()
    miercoles_actividad = models.TextField()
    miercoles_dificultad = models.TextField()
    miercoles_apoyo = models.TextField()
    miercoles_observaciones = models.TextField()
    jueves_actividad = models.TextField()
    jueves_dificultad = models.TextField()
    jueves_apoyo = models.TextField()
    jueves_observaciones = models.TextField()
    viernes_actividad = models.TextField()
    viernes_dificultad = models.TextField()
    viernes_apoyo = models.TextField()
    viernes_observaciones = models.TextField()

    def __str__(self):
        return f"Informe Diario de {self.nombre_estudiante} - {self.fecha_hora_registro}"
      
class Evaluacion(models.Model):
    estudiante = models.CharField(max_length=255)
    entidad = models.CharField(max_length=255)
    receptora = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, default='Espera')
    fecha_hora_registro = models.DateTimeField(auto_now_add=True)
    perfil = models.IntegerField(default=0)

    # Campos para la evaluación cualitativa (sin choices)
    evaluacion_1_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_1_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_1_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_1_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_1_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_2_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_2_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_2_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_2_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_2_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_3_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_3_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_3_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_3_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_3_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_4_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_4_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_4_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_4_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_4_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_5_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_5_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_5_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_5_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_5_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_6_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_6_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_6_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_6_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_6_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_7_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_7_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_7_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_7_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_7_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_8_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_8_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_8_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_8_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_8_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_9_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_9_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_9_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_9_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_9_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_10_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_10_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_10_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_10_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_10_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_11_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_11_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_11_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_11_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_11_5 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_12_1 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_12_2 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_12_3 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_12_4 = models.CharField(max_length=1, blank=True, null=True)
    evaluacion_12_5 = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        return f"Evaluación de {self.estudiante} - {self.fecha_hora_registro}"
    
class Visita(models.Model):
    estudiante = models.CharField(max_length=255)
    empresa = models.CharField(max_length=255)
    receptora = models.CharField(max_length=255)
    tutor = models.CharField(max_length=255)  # Tutor asignado
    supervisor = models.CharField(max_length=255) 
    numero = models.CharField(max_length=50)  # Visita No.
    dia = models.CharField(max_length=10)
    fecha = models.DateField()
    tutor_receptora = models.CharField(max_length=255)  # Tutor Receptora
    entidad2 = models.CharField(max_length=255)  # Entidad (para la fila de la tabla)
    observaciones = models.TextField()
    calificacion = models.CharField(max_length=255, blank=True)
    fecha_hora_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visita de {self.estudiante } a {self.empresa}"
      
class Reporte(models.Model):
    evaluacion = models.ForeignKey('Evaluacion', on_delete=models.CASCADE)
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE)
    conclusiones = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    rector = models.CharField(max_length=100,default='rector')   
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte de {self.perfil.user.username}"