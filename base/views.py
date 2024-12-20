from .models import Tarea, Archivo,GrupoDeTrabajo
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import Group
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from .forms import CustomAuthenticationForm, TareaForm
import os
from django.conf import settings
from datetime import date
from django.views.generic import TemplateView




class GruposTrabajoView(TemplateView):
    template_name = "base/grupos_trabajo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["grupos"] = GrupoDeTrabajo.objects.prefetch_related('anios').all()
        
        # Calcular la cantidad de muestras vencidas
        today = date.today()
        muestras_vencidas = Tarea.objects.filter(fecha__lte=today, completo=False, medicion_completa=False).count()
        context['muestras_vencidas'] = muestras_vencidas
        
        # Incluir las tareas vencidas en el contexto si se hizo clic en "muestras vencidas"
        if self.request.GET.get("vencidas") == "True":
            context['tareas_vencidas'] = Tarea.objects.filter(fecha__lte=today, completo=False, medicion_completa=False)
        else:
            context['tareas_vencidas'] = None
        
        return context




class Logueo(LoginView):
    template_name = "base/login.html"
    redirect_authenticated_user = True
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        return reverse_lazy("grupos_trabajo")

class analisisDeResultado(ListView):
    model = Tarea
    context_object_name = "tareas"
    template_name = "analisistemp.html"  # Cambia esto a la ruta de tu template

    def get_queryset(self):
        # Filtrar tareas excluyendo las que tienen completo o medicion_completa en False
        return Tarea.objects.filter(completo=True, medicion_completa=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        valor_buscado = self.request.GET.get("titulo", "")
        tareas = self.get_queryset()
        if valor_buscado:
            tareas = tareas.filter(titulo__icontains=valor_buscado)
        context["tareas"] = tareas
        context["valor_buscado"] = valor_buscado
        return context


class listaPendientes(ListView):
    model = Tarea
    context_object_name = "tareas"
    template_name = "base/tarea_list.html"

    def get_queryset(self):
        valor_buscado = self.request.GET.get("titulo", "")
        completo = self.request.GET.get("completo")
        medicion_completa = self.request.GET.get("medicion_completa")
        grupo_id = self.request.GET.get("grupo")
        anio = self.request.GET.get("anio")
        vencidas = self.request.GET.get("vencidas")

        # Filtramos por grupo y año si están presentes
        tareas = Tarea.objects.all()
        if grupo_id:
            tareas = tareas.filter(grupo_de_trabajo_id=grupo_id)
        if anio:
            tareas = tareas.filter(anio__anio=anio)
        if vencidas == "True":
            today = date.today()
            tareas = tareas.filter(fecha__lte=today, completo=False, medicion_completa=False)

        # Aplicamos otros filtros solo si están presentes
        if valor_buscado:
            tareas = tareas.filter(titulo__icontains=valor_buscado)
        if completo is not None and completo != "":
            tareas = tareas.filter(completo=(completo == 'True'))
        if medicion_completa is not None and medicion_completa != "":
            tareas = tareas.filter(medicion_completa=(medicion_completa == 'True'))

        return tareas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["valor_buscado"] = self.request.GET.get("titulo", "")
        context["completo"] = self.request.GET.get("completo")
        context["medicion_completa"] = self.request.GET.get("medicion_completa")
        context["grupo_id"] = self.request.GET.get("grupo")
        context["anio"] = self.request.GET.get("anio")
        context["vencidas"] = self.request.GET.get("vencidas")
        return context



class EditarTareas(UpdateView):
    model = Tarea
    form_class = TareaForm

    def form_valid(self, form):
        tarea = form.save(commit=False)
        
        # Mantener los valores originales de grupo_de_trabajo y anio
        tarea.grupo_de_trabajo = self.object.grupo_de_trabajo
        tarea.anio = self.object.anio

        if form.cleaned_data.get('medicion_completa') and not tarea.fecha_medicion:
            tarea.fecha_medicion = date.today()
        tarea.usuario = self.request.user
        tarea.save()
        if form.cleaned_data.get('medicion_gamma') and not tarea.fecha_medicion_gamma:
            tarea.fecha_medicion_gamma = date.today()
        tarea.usuario = self.request.user
        tarea.save()
        if self.request.FILES.get('archivo'):
            archivo = Archivo(tarea=tarea, archivo=self.request.FILES['archivo'])
            archivo.save()

        grupo_id = tarea.grupo_de_trabajo.id if tarea.grupo_de_trabajo else None
        anio = tarea.anio.anio if tarea.anio else None

        if grupo_id is not None and anio is not None:
            return redirect(reverse('tareas') + f'?grupo={grupo_id}&anio={anio}')
        else:
            return redirect(reverse('tareas'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_tarea'] = self.object.titulo  # Añadir el título de la tarea al contexto
        archivos = self.object.archivos.all()
        archivos_existentes = [archivo for archivo in archivos if os.path.exists(os.path.join(settings.MEDIA_ROOT, archivo.archivo.name))]
        context['archivos'] = archivos_existentes
        context['form'] = self.get_form()

        # Pasar el usuario actual y verificar los grupos de usuarios de manera segura
        context['user'] = self.request.user
        context['user_visita'] = Group.objects.filter(name='Visitantes').first().user_set.all() if Group.objects.filter(name='Visitantes').exists() else []
        context['user_muestreo'] = Group.objects.filter(name='muestreo').first().user_set.all() if Group.objects.filter(name='muestreo').exists() else []
        context['user_mediciones'] = Group.objects.filter(name='mediciones').first().user_set.all() if Group.objects.filter(name='mediciones').exists() else []
        context['user_superuser'] = Group.objects.filter(name='superuser').first().user_set.all() if Group.objects.filter(name='superuser').exists() else []
        context['user_analisis'] = Group.objects.filter(name='analisis').first().user_set.all() if Group.objects.filter(name='analisis').exists() else []
        context['user_gamma'] = Group.objects.filter(name='gamma').first().user_set.all() if Group.objects.filter(name='gamma').exists() else []
        return context



import logging

logger = logging.getLogger(__name__)

class EliminarArchivo(View):
    def post(self, request, archivo_id):
        archivo = get_object_or_404(Archivo, id=archivo_id)
        tarea_id = archivo.tarea.id
        try:
            archivo.archivo.delete()
            archivo.delete()
            logger.info(f"Archivo {archivo_id} eliminado con éxito.")
        except Exception as e:
            logger.error(f"Error al eliminar el archivo {archivo_id}: {e}")
        return redirect('editar-tarea', pk=tarea_id)
