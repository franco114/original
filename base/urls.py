from django.urls import path
from .views import GruposTrabajoView, listaPendientes, Logueo, EditarTareas, EliminarArchivo
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("tareas/", login_required(listaPendientes.as_view()), name="tareas"),
    path("", Logueo.as_view(), name="login"),
    path("logout/", login_required(LogoutView.as_view(next_page="login")), name="logout"),
    path("editar-tarea/<int:pk>", login_required(EditarTareas.as_view()), name="editar-tarea"),
    path("eliminar-archivo/<int:archivo_id>/", login_required(EliminarArchivo.as_view()), name="eliminar-archivo"),
    path("grupos-trabajo/", login_required(GruposTrabajoView.as_view()), name="grupos_trabajo"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
