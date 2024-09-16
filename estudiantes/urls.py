from django.urls import path
from . import views  # Importa el módulo views
from django.contrib.auth import views as auth_views
from .views import *


urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.LoginPage, name="login"),  # login
    path('home/', views.HomePage, name="home"),  # home
    
    path('logout/', views.LogoutPage, name='logout'),  # SALIR
    path('ingreso/', views.ingreso, name='ingreso'),  # ingreso
    path('registro/', views.registro, name='registro'),  # registro
    path('manage-users/', views.manage_users, name='manage_users'),
    
    path('test/', views.test, name='test'),
    path('varios/', views.varios, name='varios'),
    
    path('aprobar_usuario/<int:pk>/', views.aprobar_usuario, name='aprobar_usuario'),
    path('rechazar_estudiante/<int:pk>/', views.rechazar_estudiante, name='rechazar_estudiante'),
    
    path('aprobar_carta/<int:pk>/', views.aprobar_carta, name='aprobar_carta'),
    path('rechazar_carta/<int:pk>/', views.rechazar_carta, name='rechazar_carta'),
    path('enviar_carta_aprobacion/', views.enviar_carta_aprobacion, name='enviar_carta_aprobacion'),
    path('ver_carta/<int:pk>/', views.ver_carta, name='ver_carta'),
    
    
    path('empresa/', views.EmpresaListView.as_view(), name='empresa_list'),  # Ahora importa la clase desde views.py
    path('empresa/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresa/create/', views.EmpresaCreateView.as_view(), name='empresa_create'),
    path('empresa/<int:pk>/update/', views.EmpresaUpdateView.as_view(), name='empresa_update'),
    path('empresa/<int:pk>/delete/', views.EmpresaDeleteView.as_view(), name='empresa_delete'),
    path('empresa_eliminar/<int:pk>', views.empresa_eliminar, name='empresa_eliminar'),
    
    path('escoger_empresa/<int:pk>/', views.escoger_empresa, name='escoger_empresa'),
    path('escogiendo_empresa/', views.escogiendo_empresa, name='escogiendo_empresa'),
    
    path('empresas/', views.empresas, name='empresas'),
    path('empresa_asignado/', views.empresa_asignado, name='empresa_asignado'),
    path('empresas_estudiante/<int:pk>/', views.empresas_estudiante, name='empresas_estudiante'), 
    
    path('rol/', views.RolListView.as_view(), name='rol_list'),
    path('rol/<int:pk>/', views.RolDetailView.as_view(), name='rol_detail'),
    path('rol/create/', views.RolCreateView.as_view(), name='rol_create'),
    path('rol/<int:pk>/update/', views.RolUpdateView.as_view(), name='rol_update'),
    path('rol/<int:pk>/delete/', views.RolDeleteView.as_view(), name='rol_delete'),
    
    path('formato/', views.FormatoListView.as_view(), name='formato_list'),
    path('formato/<int:pk>/', views.FormatoDetailView.as_view(), name='formato_detail'),
    path('formato/create/', views.FormatoCreateView.as_view(), name='formato_create'),
    path('formato/<int:pk>/update/', views.FormatoUpdateView.as_view(), name='formato_update'),
    path('formato/<int:pk>/delete/', views.FormatoDeleteView.as_view(), name='formato_delete'),
    
    path('tutores/', views.tutor_list, name='tutor_list'),
    path('tutores/<int:pk>/', views.tutor_detail, name='tutor_detail'),
    path('tutores/nuevo/', views.tutor_create, name='tutor_create'),
    path('tutores/<int:pk>/editar/', views.tutor_update, name='tutor_update'),
    path('tutores/<int:pk>/eliminar/', views.tutor_delete, name='tutor_delete'),
    
    path('tutor_asignar/<int:pk>/', views.tutor_asignar, name='tutor_asignar'),
    path('tutor_asignado/', views.tutor_asignado, name='tutor_asignado'),
    path('tutor/', views.tutor, name='tutor'),
    path('tutor_documentos/', views.tutor_documentos, name='tutor_documentos'),
    path('tutor_estudiantes/', views.tutor_estudiantes, name='tutor_estudiantes'),
    path('tutor_actualizar/', views.tutor_actualizar, name='tutor_actualizar'),
    
    path('visita_lista/', views.visita_lista, name='visita_lista'),
    path('visita_academica/<int:pk>/', views.visita_academica, name='visita_academica'),
    path('ver_visita/<str:estudiante>/<int:numero_visita>/', views.ver_visita, name='ver_visita'),
    
    path('evaluacion_actividades_tutor/', views.evaluacion_actividades_tutor, name='evaluacion_actividades_tutor'),
    path('evaluacion_actividades/<int:pk>/', views.evaluacion_actividades, name='evaluacion_actividades'),
    path('evaluacion_lista/', views.evaluacion_lista, name='evaluacion_lista'),
    path('ver_evaluacion/<int:pk>/', views.ver_evaluacion, name='ver_evaluacion'),
    path('aprobar_evaluacion/<int:pk>/', views.aprobar_evaluacion, name='aprobar_evaluacion'),
    
    path('registro_semanal/', views.registro_semanal, name='registro_semanal'),
    path('registro_semanal_lista/', views.registro_semanal_lista, name='registro_semanal_lista'),
    path('registro_semanal_ver/<int:pk>/', views.registro_semanal_ver, name='registro_semanal_ver'),
    path('registro_semanal_eliminar/<int:pk>/', views.registro_semanal_eliminar, name='registro_semanal_eliminar'),
    
    path('formulario_ia/', views.formulario_ia, name='formulario_ia'),
    path('analisis_ia/', views.analisis_ia, name='analisis_ia'),
    
    path('cambiar-contrasena/', CustomPasswordChangeView, name='password_change'),
    path('cambiar-contrasena-exito/', auth_views.PasswordChangeDoneView.as_view(template_name='cambiar_contrasena_exito.html'), name='password_change_done'),

    path('supervisor_estudiante_list/', views.supervisor_estudiante_list, name='supervisor_estudiante_list'),
    path('supervisor_aprobar_reporte/<int:pk>/', views.supervisor_aprobar_reporte, name='supervisor_aprobar_reporte'),
    
    path('evaluacion_aprobada_lista/', views.evaluacion_aprobada_lista, name='evaluacion_aprobada_lista'),
    
    path('generar_reporte/<int:pk>/', views.generar_reporte, name='generar_reporte'),
    path('reporte_aprobado/', views.reporte_aprobado, name='reporte_aprobado'),
    path('generar-pdf/<int:pk>/', generar_pdf, name='generar_pdf'),
    path('reporte_estudiante/', views.reporte_estudiante, name='reporte_estudiante'),
    
    
    path('usuarios-no-estudiantes/', listar_usuarios_no_estudiantes, name='listar_usuarios_no_estudiantes'),
    path('cambiar-rol/<int:pk>/', cambiar_rol, name='cambiar_rol'),
    
    path('listar_usuarios/', views.listar_usuarios, name='listar_usuarios'),
    
    path('eliminar-usuario/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('habilitar_usuario/<int:pk>/', views.habilitar_usuario, name='habilitar_usuario'),
    
]