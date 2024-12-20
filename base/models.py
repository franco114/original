from django.db import models
from django.contrib.auth.models import User

class GrupoDeTrabajo(models.Model):
    titulo = models.CharField(max_length=250, unique=True)  # Título único

    def __str__(self):
        return self.titulo

class Anio(models.Model):
    grupo = models.ForeignKey(GrupoDeTrabajo, related_name='anios', on_delete=models.CASCADE)
    anio = models.IntegerField()

    def __str__(self):
        return f"{self.grupo.titulo} - {self.anio}"

class Tarea(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    titulo = models.CharField(max_length=250)
    integrantes = models.TextField(null=True, blank=True)
    completo = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
    fecha = models.DateField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    fecha_medicion = models.DateField(null=True, blank=True)
    medicion_completa = models.BooleanField(default=False)
    medicion_gamma = models.BooleanField(default=False)
    justificacion = models.TextField(null=True, blank=True)
    grupo_de_trabajo = models.ForeignKey(GrupoDeTrabajo, on_delete=models.CASCADE, null=True, blank=True)
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, null=True, blank=True)
    fecha_medicion_gamma = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ["completo"]

class Archivo(models.Model):
    tarea = models.ForeignKey(Tarea, related_name="archivos", on_delete=models.CASCADE)
    archivo = models.FileField(upload_to="protocolos/")

    def __str__(self):
        return self.archivo.name
