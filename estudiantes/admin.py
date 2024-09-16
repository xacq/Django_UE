from django.contrib import admin
from .models import Empresa, Rol, Tutor, Perfil, Formato, CartaAceptacion, InformeDiario, Evaluacion, Visita, Reporte

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'direccion', 'telefono', 'correo_electronico', 'ruc')
    search_fields = ('nombre_empresa', 'ruc')
    list_filter = ('nombre_empresa',)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'profesion', 'experiencia')
    search_fields = ('nombre', 'profesion')
    list_filter = ('profesion',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'cedula', 'nombres', 'apellidos', 'rol', 'empresa_nombre', 'estado_ingreso', 'tutor_asignado_estado')
    search_fields = ('user__username', 'nombres', 'apellidos', 'cedula', 'empresa_nombre__nombre_empresa')
    list_filter = ('rol', 'empresa_nombre', 'estado_ingreso', 'tutor_asignado_estado')
    readonly_fields = ('user', 'rol')

@admin.register(Formato)
class FormatoAdmin(admin.ModelAdmin):
    list_display = ('nombre_formato', 'descripcion', 'prioridad', 'archivo_formato')
    search_fields = ('nombre_formato',)
    list_filter = ('prioridad',)

@admin.register(CartaAceptacion)
class CartaAceptacionAdmin(admin.ModelAdmin):
    list_display = ('estudiante_carta', 'cedula_carta', 'ano_lectivo_carta', 'estado_carta', 'empresa', 'supervisor')
    search_fields = ('estudiante_carta__username', 'cedula_carta', 'empresa')
    list_filter = ('estado_carta',)

@admin.register(InformeDiario)
class InformeDiarioAdmin(admin.ModelAdmin):
    list_display = ('nombre_estudiante', 'entidad', 'area_trabajo', 'fecha_inicio', 'fecha_final')
    search_fields = ('nombre_estudiante', 'entidad')
    list_filter = ('fecha_inicio', 'fecha_final')

@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'entidad', 'area', 'estado', 'fecha_hora_registro')
    search_fields = ('estudiante', 'entidad', 'area')
    list_filter = ('estado', 'fecha_hora_registro')

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'empresa', 'receptora', 'tutor', 'supervisor', 'numero', 'fecha')
    search_fields = ('estudiante', 'empresa', 'tutor')
    list_filter = ('numero', 'fecha')

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'evaluacion', 'fecha_generacion', 'rector')
    search_fields = ('perfil__user__username', 'rector')
    list_filter = ('fecha_generacion',)
    readonly_fields = ('fecha_generacion',)
