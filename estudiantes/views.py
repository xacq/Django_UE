
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, TutorForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import *
from django.contrib.auth.decorators import user_passes_test
from .forms import *
from django.utils import timezone
from openai import OpenAI
import re
from django.db.models import Q 
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import PasswordChangeView
from .forms import CustomPasswordChangeForm
from .utils import validar_cedula, validar_ruc  # Asegúrate de importar la función de validación
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def registro(request):
    if request.method == 'POST':
        nombres = request.POST['nombres']
        apellidos = request.POST['apellidos']
        cedula = request.POST['cedula']
        email = request.POST['email']
        password = request.POST['password']
        password_confirmation = request.POST['password2']
        if password_confirmation != password:   
            messages.error(request, 'Las contraseñas no coniciden!')
            return redirect('registro')
        elif not validar_cedula(cedula):
            messages.error(request, 'La cédula ingresada no es válida. Por favor, rectifíquela.')
            return redirect('registro')
        else:
            name = nombres.replace(' ','_')
            lastname = apellidos.replace(' ','_')
            username = f"{name}_{lastname}".lower()
            # Verificar si el nombre de usuario o el correo electrónico ya existen
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
                return redirect('registro')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está en uso.')
                return redirect('registro')
            else:
                # Crear el usuario si no existe
                        # Crear el usuario
                user = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password),  # Asegurar que la contraseña se guarde correctamente
                    first_name=nombres,
                    last_name=apellidos
                )
                # Asignar el rol de 'Estudiante'
                rol_estudiante, created = Rol.objects.get_or_create(nombre='Usuario')
                estado_ingreso = 'Espera'
                # Crea el perfil del usuario con la cédula
                Perfil.objects.create(user=user, rol=rol_estudiante, estado_ingreso=estado_ingreso, apellidos=apellidos, cedula=cedula, nombres=nombres)
                messages.success(request, 'Tu cuenta ha sido creada exitosamente.')
                return redirect('login')
    else:
        return render(request, 'registro.html')

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                # Obtener el perfil del usuario
                perfil = Perfil.objects.get(user=user)
                if perfil.estado_ingreso == 'Rechazado':
                    messages.error(request, 'Su perfil ha sido Rechazado.')
                else:
                    rol_nombre = perfil.rol.nombre
                    # Iniciar sesión al usuario
                    login(request, user)
                    
                    # Establecer variables de sesión
                    request.session['username'] = username
                    request.session['nombres_completos'] = perfil.nombres + ' ' +perfil.apellidos
                    request.session['cedula'] = perfil.cedula
                    request.session['email'] = user.email  # Obtener email desde el objeto User
                    request.session['rol'] = rol_nombre  
                    request.session['estado_ingreso'] = perfil.estado_ingreso 
                    request.session['estado_carta_aprobacion'] = perfil.estado_carta_aprobacion
                    request.session['estado_tutor'] = perfil.tutor_asignado_estado
                    request.session['estado_ia'] = perfil.ia_estado
                    if rol_nombre == 'Estudiante':
                        if perfil.empresa_nombre is not None:  # Comprueba si existe la empresa
                            request.session['estado_empresa'] = perfil.empresa_estado
                            request.session['empresa'] = perfil.empresa_nombre.nombre_empresa
                            request.session['supervisor'] = perfil.supervisor
                        else:
                            request.session['estado_empresa'] = 'Espera'
                            request.session['empresa'] = 'Espera'
                            request.session['supervisor'] = 'Espera'  # O un valor por defecto apropiado
                              
                        if perfil.tutor_id is not None:
                            try:
                                tutor = Tutor.objects.get(id=perfil.tutor_id)
                                request.session['tutor'] = tutor.nombre
                            except Tutor.DoesNotExist:
                                # Manejar el caso en que el tutor no existe
                                request.session['tutor'] = 'No asignado'  # O un valor por defecto
                        else:
                            # Manejar el caso en que el tutor no está asignado
                            request.session['tutor'] = 'No asignado'
                    
                    tutor_pendientes = Perfil.objects.filter(rol__nombre='Estudiante', tutor_asignado_estado='Espera')
                    tutores_epera= [
                        {
                            'username': tutor.user.username,  # Incluye el username
                            'email': tutor.user.email,
                            'estado_tutor': tutor.tutor_asignado_estado ,
                            'pk': tutor.pk
                        }
                        for tutor in tutor_pendientes
                    ]
                    
                    estudiantes_pendientes = Perfil.objects.filter(estado_ingreso='Espera', habilitado=True)
                    estudiantes= [
                        {
                            'username': estudiante.user.username,  # Incluye el username
                            'email': estudiante.user.email,
                            'estado_ingreso': estudiante.estado_ingreso,
                            'pk': estudiante.pk
                        }
                        for estudiante in estudiantes_pendientes
                    ]
                    
                    cartas_pendientes = CartaAceptacion.objects.filter(estado_carta='Espera')
                    cartas = [
                        {
                            'username': carta.estudiante_carta.username,
                            'cedula_carta': carta.cedula_carta,
                            'ano_lectivo_carta': carta.ano_lectivo_carta,
                            'estado_carta': carta.estado_carta,
                            'pk': carta.pk
                        }
                        for carta in cartas_pendientes
                    ]

                    context = {
                        'estudiantes' : estudiantes,
                        'cartas' : cartas,  
                        'tutores_epera' : tutores_epera,                  
                    }
                    return render(request, 'home.html', context)
            except Perfil.DoesNotExist:
                messages.error(request, 'No se ha encontrado un perfil asociado al usuario.')
                return redirect('login')  # O a cualquier otra página de tu elección
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('login')
    
    return render(request, 'ingreso.html')

@login_required
def aprobar_usuario(request, pk):
    perfil = get_object_or_404(Perfil, pk=pk)
    if request.method == 'POST':
        rol_id = request.POST.get('rol')
        nombre = request.POST.get('nombre')
        estado = request.POST.get('estado')
        # Obtener la instancia del rol correspondiente al rol_id
        rol = get_object_or_404(Rol, pk=rol_id)
        # Asignar la instancia del rol al perfil
        perfil.estado_ingreso = estado
        perfil.rol = rol
        # Guardar los cambios en el perfil
        perfil.save()
        if rol.nombre == 'Tutor': 
            nombre = nombre.replace('_', ' ')
            profesion = 'Sin informacion'
            experiencia = 'Sin experiencia'
            # Crear y guardar la instancia del modelo Tutor
            nuevo_tutor = Tutor(nombre=nombre, profesion=profesion, experiencia=experiencia)
            nuevo_tutor.save()
            
        messages.success(request, 'El usuario ha sido aprobado por el Administrador.')
        
        tutor_pendientes = Perfil.objects.filter(rol__nombre='Estudiante', tutor_asignado_estado='Espera')
        tutores_epera= [
            {
                'username': tutor.user.username,  # Incluye el username
                'email': tutor.user.email,
                'estado_tutor': tutor.tutor_asignado_estado ,
                'pk': tutor.pk
            }
            for tutor in tutor_pendientes
        ]
        rol = Rol.objects.get(nombre = 'Usuario')
        estudiantes_pendientes = Perfil.objects.filter(estado_ingreso='Espera',rol_id = rol)
        estudiantes= [
            {
                'username': estudiante.user.username,  # Incluye el username
                'email': estudiante.user.email,
                'estado_ingreso': estudiante.estado_ingreso,
                'pk': estudiante.pk
            }
            for estudiante in estudiantes_pendientes
        ]
        
        cartas_pendientes = CartaAceptacion.objects.filter(estado_carta='Espera')
        cartas = [
            {
                'username': carta.estudiante_carta.username,
                'cedula_carta': carta.cedula_carta,
                'ano_lectivo_carta': carta.ano_lectivo_carta,
                'estado_carta': carta.estado_carta,
                'pk': carta.pk
            }
            for carta in cartas_pendientes
        ]
   
        context = {
            'estudiantes' : estudiantes,
            'cartas' : cartas,  
            'tutores_epera' : tutores_epera                  
        }
        return render(request, 'home.html', context)
    else:
        perfil = Perfil.objects.get(pk=pk)
        form = RolForm()
        context={
            'perfil': perfil,
            'form': form
        }
        return render(request, 'aprobar_estudiante.html',context) 
    
@login_required
def rechazar_estudiante(request, pk):
    if request.method == 'POST':
        perfil = Perfil.objects.get(pk=pk)
        perfil.estado_ingreso = request.POST.get('estado_ingreso')
        perfil.save()
        messages.success(request, 'Los cambios han sido registrados por el Usuario.')
        return redirect('home')
    else:
        perfil = Perfil.objects.get(pk=pk)
        return render(request, 'rechazar_estudiante.html', {'perfil': perfil}) 
 
@login_required   
def aprobar_carta(request, pk):
    try:
        # Se asume que 'estudiante_carta' es una ForeignKey a User, por lo que el pk debe ser el ID del User
        carta = CartaAceptacion.objects.get(estudiante_carta_id=pk)
        carta.estado_carta = 'Aprobado'
        carta.save()
        # Se guarda el estado en el perfil correspondiente
        perfil = Perfil.objects.get(user_id=pk)
        perfil.estado_carta_aprobacion = 'Aprobado'
        perfil.save()
        messages.success(request, 'La carta ha sido aprobada por el rector.')
        return redirect('home')
    except CartaAceptacion.DoesNotExist:
        messages.error(request, 'No se encontró la carta de aceptación para este estudiante.')
        return redirect('home')
    except Perfil.DoesNotExist:
        messages.error(request, 'No se encontró el perfil asociado a este estudiante.')
        return redirect('home')
    
@login_required   
def rechazar_carta(request, pk):

    carta = CartaAceptacion.objects.get(pk=pk)
    carta.estado_carta = 'Rechazado'
    carta.save()
    
    #se guarda el estado en perfil
    usuario = Perfil.objects.get(user_id=carta.estudiante_carta)
    usuario.estado_carta_aprobacion = 'Rechazado'
    usuario.save()
    
    messages.success(request, 'La carta ha sido rechazada por el rector.')
    return redirect('home')

@login_required
def enviar_carta_aprobacion(request):
    user = request.user  # Obtener el usuario autenticado
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        ano_lectivo = request.POST.get('ano_lectivo')
        supervisor = request.POST.get('supervisor')
        empresa = request.POST.get('empresa')
        especializacion = request.POST.get ('especializacion')
        rector = request.POST.get ('rector')
        
        if not validar_cedula(cedula):
            messages.error(request, 'La cédula ingresada no es válida. Por favor, rectifíquela.')
            try:
                perfil = get_object_or_404(Perfil, user=user)
                empresa_asignado = perfil.empresa_nombre
                if empresa_asignado:
                    empresa = get_object_or_404(Empresa, id=empresa_asignado.id)
                    supervisor = empresa.supervisor
                    carta = CartaAceptacion.objects.filter(estudiante_carta=user).first()
            except CartaAceptacion.DoesNotExist:
                carta = None
            context = {
            'carta': carta,
            'supervisor': supervisor,
            'nombre': empresa_asignado,
            }      
            return render(request, 'carta_aprobacion.html', context)
        # Crear una nueva carta con estado 'Espera'
        carta = CartaAceptacion(
            estudiante_carta=user,
            cedula_carta=cedula,
            ano_lectivo_carta=ano_lectivo,
            comentarios_rector_carta='',
            estado_carta='Espera',
            empresa=empresa,
            supervisor=supervisor,
            especializacion = especializacion,
            rector = rector,
        )
        carta.save()
        # Actualizar el perfil del usuario
        usuario = get_object_or_404(Perfil, user=user)
        usuario.estado_carta_aprobacion = 'Espera'
        usuario.especializacion = especializacion
        usuario.save()
        
        request.session['estado_carta_aprobacion'] = "Espera"
        
        messages.success(request, 'La Carta ha sido enviada al Rector(a) de la Institución para su consideración.')
        return redirect('tutor_documentos')
    else:
        estado_empresa = request.session.get('estado_empresa', None)
        if estado_empresa is None:
            # Manejar el caso donde la variable no existe
            messages.error(request, 'No se ha definido el estado de la empresa en la sesión.')
            return redirect('tutor_documentos')  # O la página de tu elección
        else:
            if estado_empresa == 'Espera':
                messages.success(request, 'No existe empresa asignada')
                return redirect('tutor_documentos')
            else:   
                try:
                    rol_rector = Rol.objects.get(nombre='Rector')
                    rector = Perfil.objects.get(rol = rol_rector)
                    perfil = get_object_or_404(Perfil, user=user)
                    empresa_asignado = perfil.empresa_nombre
                    if empresa_asignado:
                        empresa = get_object_or_404(Empresa, id=empresa_asignado.id)
                        supervisor = empresa.supervisor
                    carta = CartaAceptacion.objects.filter(estudiante_carta=user).first()
                except CartaAceptacion.DoesNotExist:
                    carta = None

                context = {
                    'carta': carta,
                    'supervisor': supervisor,
                    'nombre': empresa_asignado,
                    'now': timezone.now(),
                    'rector' : rector.nombres + ' ' + rector.apellidos
                }
                return render(request, 'carta_aprobacion.html', context)
          
@login_required
def ver_carta(request, pk):
    carta = CartaAceptacion.objects.get(pk=pk)
    #estudiante = Perfil.objects.get(pk=carta.estudiante_carta_id)
    context = {'carta': carta}
    return render(request, 'ver_carta.html', context)              
                 
def index(request):
    return render(request, "index.html")

def ingreso(request):
    return render(request, "ingreso.html")

def test(request):
    return render(request, "test.html")

def varios(request):
    return render(request, "varios.html")

@login_required
def supervisor_estudiante_list(request):
    # Obtener el usuario actual (supervisor)
    user = request.user
    # Filtrar los estudiantes asignados a este supervisor
    estudiantes = Perfil.objects.filter(supervisor=user)
    # Pasar los estudiantes a la plantilla
    context = {
        'estudiantes': estudiantes
    }
    return render(request, 'supervisor_estudiante_list.html', context)

@login_required
def supervisor_aprobar_reporte(request, pk):
    perfil = Perfil.objects.get(pk=pk)
    reporte = Reporte.objects.get(perfil=perfil)
    context={
        'reporte': reporte,
        'perfil': perfil
        }
    return render(request, 'supervisor_aprobar_reporte.html', context)

@login_required
def reporte_aprobado(request):
    if request.method == 'POST':
        perfil = request.POST.get('perfil')
        usuario = Perfil.objects.get(pk=perfil)
        usuario.reporte_estado = 'Aprobado'
        usuario.save()
        messages.success(request,'Reporte aprobado por el Supervisor.')
        return redirect('supervisor_estudiante_list')
    else:
        messages.success(request,'Reporte no fue aprobado por el Supervisor.')
        return redirect('supervisor_estudiante_list')

@login_required
def LogoutPage(request):
    logout(request)
    return render(request, "index.html")

user_passes_test(lambda u: u.is_superuser)  # Solo permite acceso a administradores
def manage_users(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('manage_users')
    else:
        form = UserCreationForm()

    return render(request, 'manage_users.html', {'form': form})

@login_required(login_url='login')
def HomePage(request):
    tutor_pendientes = Perfil.objects.filter(rol__nombre='Estudiante', tutor_asignado_estado='Espera')
    tutores_epera= [
        {
            'username': tutor.user.username,  # Incluye el username
            'email': tutor.user.email,
            'estado_tutor': tutor.tutor_asignado_estado ,
            'pk': tutor.pk
        }
        for tutor in tutor_pendientes
    ]
    rol = Rol.objects.get(nombre = 'Usuario')
    estudiantes_pendientes = Perfil.objects.filter(estado_ingreso='Espera',rol_id = rol)
    estudiantes= [
        {
            'username': estudiante.user.username,  # Incluye el username
            'email': estudiante.user.email,
            'estado_ingreso': estudiante.estado_ingreso,
            'pk': estudiante.pk
        }
        for estudiante in estudiantes_pendientes
    ]
    
    cartas_pendientes = CartaAceptacion.objects.filter(estado_carta='Espera')
    cartas = [
        {
            'username': carta.estudiante_carta.username,
            'cedula_carta': carta.cedula_carta,
            'ano_lectivo_carta': carta.ano_lectivo_carta,
            'estado_carta': carta.estado_carta,
            'pk': carta.pk
        }
        for carta in cartas_pendientes
    ]

    context = {
        'estudiantes' : estudiantes,
        'cartas' : cartas,  
        'tutores_epera' : tutores_epera                  
    }
    return render(request, 'home.html', context)

#ACCIONES PARA EMPRESA

def empresa_eliminar(request, pk):
    if request.method == 'POST':
        user = request.user
        perfil = Perfil.objects.get(user=user)
        perfil.empresa_estado = 'Espera'
        perfil.supervisor = 'Espera1'
        perfil.empresa_nombre = None
        perfil.save()
        request.session['estado_empresa'] = 'Espera'
        request.session['empresa'] = 'Espera'
        request.session['supervisor'] = 'Espera'  # O un valor por defecto apropiado
        messages.success(request, 'La Empresa ya no esta asignada.')
        
        
        return redirect('home')
    else:
        # Si es una solicitud GET, obtener la empresa por su ID (pk)
        empresa = get_object_or_404(Empresa, id=pk)
        context = {'empresa': empresa}
        return render(request, 'empresa_eliminar.html', context)


class EmpresaListView(ListView):
    model = Empresa
    template_name = 'empresa_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(nombre_empresa__icontains=query))
        return queryset


class EmpresaDetailView(DetailView):
    model = Empresa
    template_name = 'empresa_detail.html'


class EmpresaCreateView(CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'empresa_form.html'
    success_url = reverse_lazy('empresa_list')
    def form_valid(self, form):
                # Obtener la instancia del formulario
        empresa = form.save(commit=False)
                # Validar el número de cédula (puedes modificar el campo según donde se almacene el RUC o cédula)
        if not validar_ruc(empresa.ruc):
            form.add_error('ruc', 'El número de RUC no es válido.')
            return self.form_invalid(form)
        # Guardar la instancia
        empresa.save()
        
        return super().form_valid(form)


class EmpresaUpdateView(UpdateView):
    model = Empresa
    fields = '__all__'
    template_name = 'empresa_form.html'
    success_url = reverse_lazy('empresa_list')


class EmpresaDeleteView(DeleteView):
    model = Empresa
    template_name = 'empresa_confirm_delete.html'
    success_url = reverse_lazy('empresa_list')

@login_required 
def escoger_empresa(request, pk):
    # Si es una solicitud GET, obtener la empresa por su ID (pk)
    empresa = get_object_or_404(Empresa, id=pk)
    context = {'empresa': empresa}
    return render(request, 'escoger_empresa.html', context)

@login_required
def escogiendo_empresa(request):
    user = request.user
    if request.method == 'POST':
        # Obtener los datos del formulario
        empresa_id = request.POST.get('empresa_id')
        empresa_supervisor = request.POST.get('empresa_supervisor')
        empresa_nombre = request.POST.get('empresa_nombre')
        empresa_correo = request.POST.get('empresa_correo')
        
        # Obtener la empresa usando el ID del formulario
        datos_empresa = get_object_or_404(Empresa, id=empresa_id)

        # Obtener el perfil del usuario autenticado
        perfil = get_object_or_404(Perfil, user=user)
        
        username_supervisor = empresa_supervisor.replace(" ", "_").lower()
        
        # Asignar la empresa seleccionada al perfil del usuario
        perfil.empresa_nombre_id = datos_empresa
        perfil.empresa_estado = 'Aprobado'
        perfil.supervisor = username_supervisor
        perfil.estado_ingreso = 'Aprobado'
        perfil.save()

        # Guardar el estado en la sesión
        request.session['estado_empresa'] = 'Aprobado'
        request.session['empresa'] = empresa_nombre
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username_supervisor).exists():
            # Si el usuario ya existe, no lo creamos de nuevo
            supervisor_user = User.objects.get(username=username_supervisor)
            messages.info(request, f'El supervisor {empresa_supervisor} ya existe con el usuario: {username_supervisor}.')
        else:
            # Crear el nuevo usuario para el supervisor
            supervisor_user = User.objects.create_user(username=username_supervisor, email=empresa_correo, password=username_supervisor)
            messages.success(request, f'Supervisor creado con usuario: {username_supervisor}, contraseña: {username_supervisor}')

            # Obtener o crear el rol de Supervisor
            rol_supervisor, created = Rol.objects.get_or_create(nombre='Usuario')
            estado_ingreso = 'Espera'

            # Crear el perfil del supervisor
            Perfil.objects.create(user=supervisor_user, rol=rol_supervisor, estado_ingreso=estado_ingreso)

        # Asignar un mensaje de éxito
        messages.success(request, f'Empresa asignada correctamente.')
        
        # Redirigir a la página de inicio u otra vista deseada
        return redirect('home')
    else:
        messages.error(request, 'No se pudo asignar la empresa.')
        return redirect('home')
        
#ACCIONES PARA ROLES

class RolListView(ListView):
    model = Rol
    template_name = 'rol_list.html'


class RolDetailView(DetailView):
    model = Rol
    template_name = 'rol_detail.html'


class RolCreateView(CreateView):
    model = Rol
    fields = '__all__'
    template_name = 'rol_form.html'
    success_url = reverse_lazy('rol_list')


class RolUpdateView(UpdateView):
    model = Rol
    fields = '__all__'
    template_name = 'rol_form.html'
    success_url = reverse_lazy('rol_list')


class RolDeleteView(DeleteView):
    model = Rol
    template_name = 'rol_confirm_delete.html'
    success_url = reverse_lazy('rol_list')
    
#ACCIONES PARA LOS FORMATOS

class FormatoListView(ListView):
    model = Formato
    template_name = 'formato_list.html'


class FormatoDetailView(DetailView):
    model = Formato
    template_name = 'formato_detail.html'


class FormatoCreateView(CreateView):
    model = Formato
    fields = '__all__'
    template_name = 'formato_form.html'
    success_url = reverse_lazy('formato_list')


class FormatoUpdateView(UpdateView):
    model = Formato
    fields = '__all__'
    template_name = 'empresa_form.html'
    success_url = reverse_lazy('formato_list')


class FormatoDeleteView(DeleteView):
    model = Formato
    template_name = 'formato_confirm_delete.html'
    success_url = reverse_lazy('formato_list')
    
#CRUD para Tutor    

def tutor_list(request):
    query = request.GET.get('q', '')  # Obtener el valor de búsqueda si existe
    if query:
        # Filtrar tutores cuyo nombre contenga el valor de búsqueda (insensible a mayúsculas)
        tutores = Tutor.objects.filter(Q(nombre__icontains=query))
    else:
        tutores = Tutor.objects.all()  # Si no hay búsqueda, mostrar todos los tutores

    return render(request, 'tutor_list.html', {'tutores': tutores, 'query': query})


def tutor_detail(request, pk):
    tutor = get_object_or_404(Tutor, pk=pk) 
    return render(request, 'tutor_detail.html', {'tutor': tutor})


def tutor_create(request):
    if request.method == 'POST':
        form = TutorForm(request.POST)
        if form.is_valid():
            # Obtener datos del formulario
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            rol_id = form.cleaned_data['rol'].id

            # Crear el usuario con nombre como username y email
            user = User.objects.create_user(username=nombre, email=email, password=password)
            
            # Crear el tutor asociado al usuario
            tutor = form.save(commit=False)
            tutor.user = user  # Asignar el usuario creado al tutor
            tutor.save()

            # Obtener el rol del formulario usando el ID del rol
            rol = Rol.objects.get(id=rol_id)
            
            # Crear el perfil asociado al usuario
            perfil = Perfil(
                user=user,
                rol=rol,  # Asignar el rol al perfil
                estado_ingreso='Espera',
                estado_carta_aprobacion='Espera1',
                tutor=tutor  # Asociar el tutor con el perfil
            )
            perfil.save()

            return redirect('tutor_list')
    else:
        form = TutorForm()
    return render(request, 'tutor_form.html', {'form': form})


def tutor_update(request, pk):
    tutor = get_object_or_404(Tutor, pk=pk)
    if request.method == 'POST':
        form = TutorForm(request.POST, instance=tutor)
        if form.is_valid():
            form.save()
            return redirect('tutor_list')
    else:
        form = TutorForm(instance=tutor)
    return render(request, 'tutor_form.html', {'form': form})


def tutor_delete(request, pk):
    tutor = get_object_or_404(Tutor, pk=pk)
    if request.method == 'POST':
        tutor.delete()
        return redirect('tutor_list')
    return render(request, 'tutor_confirm_delete.html', {'tutor': tutor})

@login_required
def tutor_asignar(request, pk):
    # Obtener el tutor según el ID proporcionado
    tutor = Tutor.objects.get(id=pk)
    # Filtrar los estudiantes que tienen el estado de carta de aprobación como "Aprobado"
    rol = Rol.objects.get(nombre='Estudiante')
    # y que no tienen tutor asignado (es decir, cuyo campo tutor es None)
    estudiantes_aprobados = Perfil.objects.filter(
        tutor_asignado_estado = 'Espera',
        rol = rol
    )   
    return render(request, 'tutor_asignar.html', {
        'tutor': tutor,
        'estudiantes_aprobados': estudiantes_aprobados,
    })

@login_required
def tutor_asignado(request):
    if request.method == 'POST':
        # Obtiene los IDs del estudiante y del tutor desde el formulario
        estudiante_id = request.POST.get('estudiante_id')
        tutor_id = request.POST.get('tutor_id')
        
        # Busca el estudiante y el tutor en la base de datos
        perfil = get_object_or_404(Perfil, id=estudiante_id)        
        # Asigna el tutor al estudiante
        perfil.tutor_id = tutor_id
        perfil.tutor_asignado_estado = "Aprobado"
        perfil.save()
        # Muestra un mensaje de éxito
        messages.success(request, 'Tutor asignado correctamente.')
        # Redirige a una página de confirmación o a la misma página de asignación
        return redirect('home')  # Cambia 'tutor_asignar' por la URL que corresponda
    else:
        # Si la solicitud no es POST, redirige a una página de error o a la página principal
        messages.error(request, 'Asignacion de Tutor no realizada.')
        return redirect('home')  # Cambia 'home' por la URL que corresponda

@login_required
def tutor(request):
    user = request.user  # Get the logged-in user
    # Obtener el perfil del estudiante basado en el ID proporcionado
    perfil = get_object_or_404(Perfil, user_id=user)
    
    # Obtener el tutor asignado
    tutor_asignado = perfil.tutor
    empresa_asignada = perfil.empresa_nombre
    
    # Crear el contexto para la plantilla
    context = {
        'perfil': perfil,
        'tutor_asignado': tutor_asignado,
        'empresa_asignada':empresa_asignada
    }
    
    # Renderizar la plantilla con el contexto
    return render(request, 'tutor.html', context)

@login_required
def tutor_documentos(request):
    return render(request, 'varios.html')

@login_required
def tutor_actualizar(request):
    if request.method == 'POST':
        tutor = Tutor.objects.get(nombre = request.user.first_name+' '+request.user.last_name)
        tutor.profesion = request.POST.get('profesion', None)
        tutor.experiencia = request.POST.get('experiencia', None)
        tutor.save()
        messages.success(request,'Informacion del Tutor Actualizada.')
        return redirect('home')
    else:    
        tutor = Tutor.objects.get(nombre = request.user.first_name+' '+request.user.last_name)
        profesion  = tutor.profesion
        experiencia = tutor.experiencia
        context = {'experiencia':experiencia, 'profesion':profesion }
        return render(request, 'tutor_actualizar.html', context)

#VISTAS ACADEMICAS
@login_required
def visita_academica(request, pk):
    perfil = Perfil.objects.get(pk=pk)
    if request.method == 'POST':
        # Obtén los datos del formulario
        estudiante_username = request.POST.get('estudiante')
        empresa = request.POST.get('empresa')
        receptora = request.POST.get('receptora')
        tutor = request.POST.get('tutor')
        supervisor = request.POST.get('supervisor')
        numero = request.POST.get('numero')
        dia = request.POST.get('dia')
        fecha = request.POST.get('fecha')
        tutor_receptora = request.POST.get('tutor_receptora')
        entidad2 = request.POST.get('entidad2')  # Entidad de la fila de la tabla
        observaciones = request.POST.get('observaciones')
        calificacion = request.POST.get('calificacion')
        Visita.objects.create(
                estudiante=estudiante_username,
                empresa=empresa,
                receptora=receptora,
                tutor=tutor,
                supervisor=supervisor,
                numero=numero,
                dia=dia,
                fecha=fecha,
                tutor_receptora=tutor_receptora,
                entidad2=entidad2,
                observaciones=observaciones,
                calificacion=calificacion,
            )
        perfil.visitas += 1
        perfil.save()
        messages.success(request, "Visita creada correctamente.")
        return redirect('tutor_documentos')
    else:
        if perfil.reporte_numero > 0:
            supervisor = perfil.supervisor
            supervisor = supervisor.replace('_',' ')
            visitas = perfil.visitas + 1
            # Filtrar estudiantes que tienen el rol de 'Estudiante' y el tutor asignado al usuario actual
            context = {
                'perfil': perfil,
                'supervisor': supervisor,
                'visitas': visitas
                }
            return render(request, 'visita_academica.html', context)
        else:
            messages.success(request, "El estudiante no empieza todavia sus practicas.")
            return redirect('tutor_estudiantes')
        
@login_required
def visita_lista(request):
    query = request.GET.get('q', '')  # Obtener el valor de búsqueda
    visitas = Visita.objects.values('estudiante').annotate(cantidad=models.Count('estudiante'))

    if query:
        # Filtrar por estudiante que contenga la palabra ingresada en el campo de búsqueda
        visitas = visitas.filter(Q(estudiante__icontains=query))

    context = {
        'visitas': visitas,
        'query': query,  # Pasar el valor de búsqueda al contexto
    }
    return render(request, 'visita_lista.html', context)

@login_required
def ver_visita (request, estudiante, numero_visita):
    try:
        # Intenta obtener la visita con el estudiante y el número de visita
        visita = Visita.objects.get(estudiante=estudiante, numero=numero_visita)
    except Visita.DoesNotExist:
        # Si la visita no existe, puedes mostrar un mensaje de error o redirigir al usuario
        messages.error(request, f"La visita número {numero_visita} del estudiante {estudiante} no existe.")
        return redirect('visita_lista')  # Redirige a la lista de visitas o a otra vista relevante
    # Si la visita existe, renderiza la página normalmente
    context = {
        'visita': visita
    }
    return render(request, 'ver_visita.html', context)
       
#EVALUACIONES 
@login_required
def aprobar_evaluacion (request, pk):
    evaluacion = Evaluacion.objects.get(pk=pk)
    evaluacion.estado = 'Aprobado'
    evaluacion.save()
    messages.success(request,'La evaluacion ha sido Aprobada')
    return redirect('home')
    
@login_required
def evaluacion_actividades(request, pk):
    perfil = Perfil.objects.get(pk=pk)
    # Filtrar estudiantes que tienen el rol de 'Estudiante' y el tutor asignado al usuario actual
    supervisor = perfil.supervisor
    supervisor = supervisor.replace('_', ' ')
    nombre = perfil.nombres + ' ' + perfil.apellidos
    try:
        evaluacion = Evaluacion.objects.get(estudiante=nombre)
        # Si la evaluación existe, redirigir con un mensaje de error
        messages.error(request, 'Ya se ha realizado la evaluación.')
        return redirect('tutor_estudiantes')
    except Evaluacion.DoesNotExist:
        # Si la evaluación no existe, continuar con la lógica
        if perfil.reporte_numero == 4:
            context = {
                'perfil': perfil,
                'supervisor': supervisor,
            }
            return render(request, 'evaluacion_actividades.html', context)
        else:
            messages.error(request, 'Todavía no se han cumplido todas las prácticas por el estudiante')
            return redirect('tutor_estudiantes')


@login_required    
def evaluacion_actividades_tutor(request):
    if request.method == 'POST':
        # Obtiene los datos del formulario
        estudiante = request.POST.get('estudiante')
        entidad = request.POST.get('entidad')
        receptora = request.POST.get('receptora')
        area = request.POST.get('area')
        perfil = request.POST.get('perfil')

        # Obtiene las evaluaciones (recuerda que hay muchos campos)
        evaluacion_1_1 = request.POST.get('evaluacion_1_1')
        evaluacion_1_2 = request.POST.get('evaluacion_1_2')
        evaluacion_1_3 = request.POST.get('evaluacion_1_3')
        evaluacion_1_4 = request.POST.get('evaluacion_1_4')
        evaluacion_1_5 = request.POST.get('evaluacion_1_5')
        evaluacion_2_1 = request.POST.get('evaluacion_2_1')
        evaluacion_2_2 = request.POST.get('evaluacion_2_2')
        evaluacion_2_3 = request.POST.get('evaluacion_2_3')
        evaluacion_2_4 = request.POST.get('evaluacion_2_4')
        evaluacion_2_5 = request.POST.get('evaluacion_2_5')
        evaluacion_3_1 = request.POST.get('evaluacion_3_1')
        evaluacion_3_2 = request.POST.get('evaluacion_3_2')
        evaluacion_3_3 = request.POST.get('evaluacion_3_3')
        evaluacion_3_4 = request.POST.get('evaluacion_3_4')
        evaluacion_3_5 = request.POST.get('evaluacion_3_5')
        evaluacion_4_1 = request.POST.get('evaluacion_4_1')
        evaluacion_4_2 = request.POST.get('evaluacion_4_2')
        evaluacion_4_3 = request.POST.get('evaluacion_4_3')
        evaluacion_4_4 = request.POST.get('evaluacion_4_4')
        evaluacion_4_5 = request.POST.get('evaluacion_4_5')
        evaluacion_5_1 = request.POST.get('evaluacion_5_1')
        evaluacion_5_2 = request.POST.get('evaluacion_5_2')
        evaluacion_5_3 = request.POST.get('evaluacion_5_3')
        evaluacion_5_4 = request.POST.get('evaluacion_5_4')
        evaluacion_5_5 = request.POST.get('evaluacion_5_5')
        evaluacion_6_1 = request.POST.get('evaluacion_6_1')
        evaluacion_6_2 = request.POST.get('evaluacion_6_2')
        evaluacion_6_3 = request.POST.get('evaluacion_6_3')
        evaluacion_6_4 = request.POST.get('evaluacion_6_4')
        evaluacion_6_5 = request.POST.get('evaluacion_6_5')
        evaluacion_7_1 = request.POST.get('evaluacion_7_1')
        evaluacion_7_2 = request.POST.get('evaluacion_7_2')
        evaluacion_7_3 = request.POST.get('evaluacion_7_3')
        evaluacion_7_4 = request.POST.get('evaluacion_7_4')
        evaluacion_7_5 = request.POST.get('evaluacion_7_5')
        evaluacion_8_1 = request.POST.get('evaluacion_8_1')
        evaluacion_8_2 = request.POST.get('evaluacion_8_2')
        evaluacion_8_3 = request.POST.get('evaluacion_8_3')
        evaluacion_8_4 = request.POST.get('evaluacion_8_4')
        evaluacion_8_5 = request.POST.get('evaluacion_8_5')
        evaluacion_9_1 = request.POST.get('evaluacion_9_1')
        evaluacion_9_2 = request.POST.get('evaluacion_9_2')
        evaluacion_9_3 = request.POST.get('evaluacion_9_3')
        evaluacion_9_4 = request.POST.get('evaluacion_9_4')
        evaluacion_9_5 = request.POST.get('evaluacion_9_5')
        evaluacion_10_1 = request.POST.get('evaluacion_10_1')
        evaluacion_10_2 = request.POST.get('evaluacion_10_2')
        evaluacion_10_3 = request.POST.get('evaluacion_10_3')
        evaluacion_10_4 = request.POST.get('evaluacion_10_4')
        evaluacion_10_5 = request.POST.get('evaluacion_10_5')
        evaluacion_11_1 = request.POST.get('evaluacion_11_1')
        evaluacion_11_2 = request.POST.get('evaluacion_11_2')
        evaluacion_11_3 = request.POST.get('evaluacion_11_3')
        evaluacion_11_4 = request.POST.get('evaluacion_11_4')
        evaluacion_11_5 = request.POST.get('evaluacion_11_5')
        evaluacion_12_1 = request.POST.get('evaluacion_12_1')
        evaluacion_12_2 = request.POST.get('evaluacion_12_2')
        evaluacion_12_3 = request.POST.get('evaluacion_12_3')
        evaluacion_12_4 = request.POST.get('evaluacion_12_4')
        evaluacion_12_5 = request.POST.get('evaluacion_12_5')

        # Crea un nuevo Evaluacion
        evaluacion = Evaluacion(
            estudiante=estudiante,
            entidad=entidad,
            receptora=receptora,
            area=area,
            perfil = perfil,
            evaluacion_1_1=evaluacion_1_1,
            evaluacion_1_2=evaluacion_1_2,
            evaluacion_1_3=evaluacion_1_3,
            evaluacion_1_4=evaluacion_1_4,
            evaluacion_1_5=evaluacion_1_5,
            evaluacion_2_1=evaluacion_2_1,
            evaluacion_2_2=evaluacion_2_2,
            evaluacion_2_3=evaluacion_2_3,
            evaluacion_2_4=evaluacion_2_4,
            evaluacion_2_5=evaluacion_2_5,
            evaluacion_3_1=evaluacion_3_1,
            evaluacion_3_2=evaluacion_3_2,
            evaluacion_3_3=evaluacion_3_3,
            evaluacion_3_4=evaluacion_3_4,
            evaluacion_3_5=evaluacion_3_5,
            evaluacion_4_1=evaluacion_4_1,
            evaluacion_4_2=evaluacion_4_2,
            evaluacion_4_3=evaluacion_4_3,
            evaluacion_4_4=evaluacion_4_4,
            evaluacion_4_5=evaluacion_4_5,
            evaluacion_5_1=evaluacion_5_1,
            evaluacion_5_2=evaluacion_5_2,
            evaluacion_5_3=evaluacion_5_3,
            evaluacion_5_4=evaluacion_5_4,
            evaluacion_5_5=evaluacion_5_5,
            evaluacion_6_1=evaluacion_6_1,
            evaluacion_6_2=evaluacion_6_2,
            evaluacion_6_3=evaluacion_6_3,
            evaluacion_6_4=evaluacion_6_4,
            evaluacion_6_5=evaluacion_6_5,
            evaluacion_7_1=evaluacion_7_1,
            evaluacion_7_2=evaluacion_7_2,
            evaluacion_7_3=evaluacion_7_3,
            evaluacion_7_4=evaluacion_7_4,
            evaluacion_7_5=evaluacion_7_5,
            evaluacion_8_1=evaluacion_8_1,
            evaluacion_8_2=evaluacion_8_2,
            evaluacion_8_3=evaluacion_8_3,
            evaluacion_8_4=evaluacion_8_4,
            evaluacion_8_5=evaluacion_8_5,
            evaluacion_9_1=evaluacion_9_1,
            evaluacion_9_2=evaluacion_9_2,
            evaluacion_9_3=evaluacion_9_3,
            evaluacion_9_4=evaluacion_9_4,
            evaluacion_9_5=evaluacion_9_5,
            evaluacion_10_1=evaluacion_10_1,
            evaluacion_10_2=evaluacion_10_2,
            evaluacion_10_3=evaluacion_10_3,
            evaluacion_10_4=evaluacion_10_4,
            evaluacion_10_5=evaluacion_10_5,
            evaluacion_11_1=evaluacion_11_1,
            evaluacion_11_2=evaluacion_11_2,
            evaluacion_11_3=evaluacion_11_3,
            evaluacion_11_4=evaluacion_11_4,
            evaluacion_11_5=evaluacion_11_5,
            evaluacion_12_1=evaluacion_12_1,
            evaluacion_12_2=evaluacion_12_2,
            evaluacion_12_3=evaluacion_12_3,
            evaluacion_12_4=evaluacion_12_4,
            evaluacion_12_5=evaluacion_12_5,
        )
        evaluacion.save()
        messages.success(request, "La evaluación se ha registrado correctamente.")
        return redirect('tutor_documentos')  # Puedes redirigir a la misma vista o a otra
    else:
        messages.success(request, "La evaluación no se ha registrado correctamente.")
        return redirect('tutor_documentos')  # Puedes redirigir a la misma vista o a otra

#REGISTRO SEMANAL
@login_required
def registro_semanal(request):
    user = request.user
    perfil = Perfil.objects.get(user = user)
    if request.method == 'POST':
        # Obtener los datos del formulario
        fecha_inicio_str = request.POST.get('fecha_inicio')
        fecha_final_str = request.POST.get('fecha_final')

        # Convertir las fechas de string a objetos datetime
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_final = datetime.strptime(fecha_final_str, '%Y-%m-%d').date()

        # Validar que la diferencia de días sea de 4 días (5 días incluyendo inicio y final)
        if (fecha_final - fecha_inicio).days != 4:
            messages.error(request, "Las fechas deben cubrir exactamente cinco días.")
            return render(request, 'registro_semanal.html')

        # Validar que la fecha de inicio sea lunes (0) y la fecha final sea viernes (4)
        if fecha_inicio.weekday() != 0 or fecha_final.weekday() != 4:
            messages.error(request, "La fecha de inicio debe ser un lunes y la fecha final debe ser un viernes.")
            return render(request, 'registro_semanal.html')

        # Si las validaciones pasan, procede a guardar el informe
        entidad = request.POST.get('entidad')
        receptora = request.POST.get('receptora')
        nombre_estudiante = request.POST.get('nombre-estudiante')
        nombre_docente = request.POST.get('nombre-docente')
        area_trabajo = request.POST.get('area-trabajo')
        
        # Datos de la tabla
        lunes_actividad = request.POST.get('lunes_actividad')
        lunes_dificultad = request.POST.get('lunes_dificultad')
        lunes_apoyo = request.POST.get('lunes_apoyo')
        lunes_observaciones = request.POST.get('lunes_observaciones')
        martes_actividad = request.POST.get('martes_actividad')
        martes_dificultad = request.POST.get('martes_dificultad')
        martes_apoyo = request.POST.get('martes_apoyo')
        martes_observaciones = request.POST.get('martes_observaciones')
        miercoles_actividad = request.POST.get('miercoles_actividad')
        miercoles_dificultad = request.POST.get('miercoles_dificultad')
        miercoles_apoyo = request.POST.get('miercoles_apoyo')
        miercoles_observaciones = request.POST.get('miercoles_observaciones')
        jueves_actividad = request.POST.get('jueves_actividad')
        jueves_dificultad = request.POST.get('jueves_dificultad')
        jueves_apoyo = request.POST.get('jueves_apoyo')
        jueves_observaciones = request.POST.get('jueves_observaciones')
        viernes_actividad = request.POST.get('viernes_actividad')
        viernes_dificultad = request.POST.get('viernes_dificultad')
        viernes_apoyo = request.POST.get('viernes_apoyo')
        viernes_observaciones = request.POST.get('viernes_observaciones')
        
        # Crear el informe y guardar en la base de datos
        informe = InformeDiario(
            entidad=entidad,
            receptora=receptora,
            nombre_estudiante=nombre_estudiante,
            nombre_docente=nombre_docente,
            area_trabajo=area_trabajo,
            fecha_inicio=fecha_inicio,
            fecha_final=fecha_final,
            lunes_actividad=lunes_actividad,
            lunes_dificultad=lunes_dificultad,
            lunes_apoyo=lunes_apoyo,
            lunes_observaciones=lunes_observaciones,
            martes_actividad=martes_actividad,
            martes_dificultad=martes_dificultad,
            martes_apoyo=martes_apoyo,
            martes_observaciones=martes_observaciones,
            miercoles_actividad=miercoles_actividad,
            miercoles_dificultad=miercoles_dificultad,
            miercoles_apoyo=miercoles_apoyo,
            miercoles_observaciones=miercoles_observaciones,
            jueves_actividad=jueves_actividad,
            jueves_dificultad=jueves_dificultad,
            jueves_apoyo=jueves_apoyo,
            jueves_observaciones=jueves_observaciones,
            viernes_actividad=viernes_actividad,
            viernes_dificultad=viernes_dificultad,
            viernes_apoyo=viernes_apoyo,
            viernes_observaciones=viernes_observaciones,
        )
        informe.save()
        if perfil.reporte_numero == 0: #SOLO GUARDARA LA SEMANA EN LA QUE INICIA
            perfil.reporte_fecha_inicio = fecha_inicio_str
            perfil.reporte_fecha_final = fecha_final_str
        else:
            perfil.reporte_fecha_final = fecha_final_str    
        perfil.reporte_numero += 1
        perfil.save()
        messages.success(request, "El informe semanal se ha registrado correctamente.")
        return redirect('registro_semanal_lista')  
    elif perfil.reporte_numero == 4:
        messages.success(request,'Ya se han generado 4 Registros de Actividades')
        return redirect('tutor_documentos') 
    else:    
        return render(request, 'registro_semanal.html')

@login_required
def registro_semanal_lista(request):
    user = request.user
    rol = request.session.get('rol', None)
    # Obtener la palabra clave de búsqueda desde el formulario
    query = request.GET.get('q')
    # Filtrar informes según el rol
    if rol == 'Tutor':
        informes = InformeDiario.objects.all().order_by('nombre_estudiante')
    elif rol == 'Estudiante':
        informes = InformeDiario.objects.filter(nombre_estudiante=user.first_name + ' ' + user.last_name)
    else:
        informes = InformeDiario.objects.none()
    # Aplicar el filtro de búsqueda si se ingresa una palabra clave
    if query:
        informes = informes.filter(
            Q(nombre_estudiante__icontains=query) |
            Q(entidad__icontains=query) |
            Q(area_trabajo__icontains=query)
        )
    # Verificar si la lista de informes está vacía
    if not informes.exists():
        mensaje = "No hay informes disponibles."
    else:
        mensaje = None
    context = {
        'informes': informes,
        'mensaje': mensaje,
        'query': query,  # Pasar la consulta de búsqueda al contexto
    }
    return render(request, 'registro_semanal_lista.html', context)

@login_required
def registro_semanal_ver (request, pk):
    registro = InformeDiario.objects.get(pk=pk)
    context={
        'registro': registro
    }
    return render(request, 'registro_semanal_ver.html', context)

@login_required
def registro_semanal_eliminar (request, pk):
    registro = InformeDiario.objects.get(pk=pk)
    registro.delete()
    user = request.user
    perfil = Perfil.objects.get(user=user)
    perfil.reporte_numero -=1
    perfil.save()
    messages.success(request,'Registro de Actividad Semanal eliminado correctamente')
    return redirect('registro_semanal_lista')

#EVALUACIONES
@login_required
def evaluacion_aprobada_lista(request):
    query = request.GET.get('q', '')  # Captura el valor de búsqueda
    evaluaciones = Evaluacion.objects.filter(estado='Aprobado').order_by('-fecha_hora_registro')
    
    if query:
        # Filtrar por el nombre del estudiante en las evaluaciones aprobadas
        evaluaciones = evaluaciones.filter(Q(estudiante__icontains=query))

    context = {
        'evaluaciones': evaluaciones,
        'query': query,  # Pasar el valor de búsqueda al contexto
    }
    return render(request, 'evaluacion_aprobadalista.html', context)    

@login_required
def evaluacion_lista(request):
    query = request.GET.get('q', '')  # Captura el valor de búsqueda
    evaluaciones = Evaluacion.objects.all().order_by('-fecha_hora_registro')
    
    if query:
        # Filtrar por estudiante que contenga la palabra ingresada en el campo de búsqueda
        evaluaciones = evaluaciones.filter(Q(estudiante__icontains=query))

    context = {
        'evaluaciones': evaluaciones,
        'query': query,  # Pasar el valor de búsqueda al contexto
    }
    return render(request, 'evaluacion_lista.html', context)

@login_required    
def ver_evaluacion(request, pk):
    evaluacion = Evaluacion.objects.get(pk=pk)
    context = { 'evaluacion': evaluacion}
    return render(request, 'ver_evaluacion.html', context)

@login_required
def tutor_estudiantes(request):
    # Verifica que el usuario tiene el rol 'Tutor'
    user = request.user
    tutor = Tutor.objects.get(nombre=user.first_name + ' ' + user.last_name)
    if tutor:
        # Obtener la palabra clave de búsqueda
        query = request.GET.get('q')
        # Obtiene los perfiles que tienen asignado al tutor logueado
        perfiles_asignados = Perfil.objects.filter(tutor_id=tutor.id)
        # Filtrar si hay una búsqueda
        if query:
            perfiles_asignados = perfiles_asignados.filter(
                Q(user__username__icontains=query) | 
                Q(user__email__icontains=query) | 
                Q(tutor_asignado_estado__icontains=query)
            )
        
        context = {
            'estudiantes_asignados': perfiles_asignados
        }
        
        return render(request, 'tutor_estudiantes.html', context)
    else:
        # Muestra un mensaje si no hay tutor asignado
        messages.success(request, 'No tiene estudiantes asignados.')
        return redirect('home')

#INTELIGENCIA ARTIFICIAL
@login_required 
def formulario_ia(request):
    if request.method == 'POST':
        p1 = request.POST.get('p1')
        p2 = request.POST.get('p2')
        p3 = request.POST.get('p3')
        p4 = request.POST.get('p4')
        p5 = request.POST.get('p5')
        p6 = request.POST.get('p6')
        p7 = request.POST.get('p7')
        p8 = request.POST.get('p8')
        p9 = request.POST.get('p9')
        p10 = request.POST.get('p10')
        p11 = request.POST.get('p11')   
        p12 = request.POST.get('p12')
        p13 = request.POST.get('p13')
        p14 = request.POST.get('p14')
        p15 = request.POST.get('p15')
        p16 = request.POST.get('p16')
        p17 = request.POST.get('p17')
        p18 = request.POST.get('p18')
        p19 = request.POST.get('p19')
        p20 = request.POST.get('p20')
        p21 = request.POST.get('p21')
        p22 = request.POST.get('p22')
        p23 = request.POST.get('p23')
        p24 = request.POST.get('p24')
        p25 = request.POST.get('p25')
        p26 = request.POST.get('p26')
        p27 = request.POST.get('p27')
        
        preguntas_respuestas = [
            "¿Qué actividades disfrutas hacer en tu tiempo libre? " + p1 +
            "¿Hay alguna materia en la escuela que te guste más que las demás? ¿Cuál y por qué? " + p2 + 
            "¿Participas en algún club, grupo o equipo dentro o fuera de la escuela? ¿Cuál es tu rol en ese grupo? " + p3 + 
            "¿Hay algún pasatiempo o actividad extracurricular que te apasione? " + p4 + 
            "¿Qué especialidad estudias? " + p5 + 
            "¿Hay alguna actividad o tarea que encuentres fácil de realizar y que otras personas consideren difícil? " + p6 + 
            "¿Prefieres trabajar solo o en equipo? ¿Por qué? " + p7 + 
            "¿Te sientes cómodo(a) utilizando tecnología? Si es así, ¿qué tipo de tecnología disfrutas usar más? " + p8 + 
            "¿Qué es lo más importante para ti en un trabajo o carrera? " + p9 + 
            "¿Te sientes más motivado(a) cuando estás trabajando en un proyecto creativo o en una tarea analítica? " + p10 + 
            "¿Te gusta enfrentar nuevos desafíos o prefieres tareas más predecibles y estructuradas? " + p11 + 
            "¿Has tenido alguna experiencia laboral o de voluntariado? ¿Cómo fue esa experiencia? " + p12 + 
            "¿Hay algún trabajo o actividad que hayas realizado en el pasado que no te haya gustado? ¿Por qué? " + p13 + 
            "¿Has tenido alguna asignatura o proyecto escolar que te haya resultado especialmente interesante o satisfactorio? " + p14 + 
            "¿Tienes alguna idea sobre qué carrera o profesión te gustaría seguir en el futuro? " + p15 + 
            "¿Qué tipo de empresa o sector te llama más la atención? " + p16 + 
            "¿Dónde te ves a ti mismo(a) en cinco años? ¿Y en diez años? " + p17 + 
            "¿Qué aspectos de una empresa consideras importantes para tu desarrollo profesional? " + p18 + 
            "¿Prefieres un ambiente de trabajo dinámico y cambiante o uno más estable y rutinario? " + p19 + 
            "¿Te sientes más productivo(a) en un entorno estructurado o en uno más flexible y creativo? " + p20 + 
            "¿Te interesa más trabajar en una gran empresa o en una pequeña empresa/startup? ¿Por qué? " + p21 + 
            "¿Qué es lo que más te gustaría aprender durante tus prácticas preprofesionales? " + p22 + 
            "¿Hay alguna habilidad específica que te gustaría desarrollar? " + p23 + 
            "¿Qué crees que podrías aportar a una empresa durante tus prácticas? " + p24 + 
            "¿Qué tipo de apoyo o guía te gustaría recibir durante tus prácticas? " + p25 + 
            "Si pudieras diseñar tu trabajo ideal, ¿cómo sería? " + p26 + 
            "¿Qué tipo de impacto te gustaría tener en tu comunidad o en el mundo a través de tu trabajo? " + p27
        ]
        
        request.session['preguntas_respuestas'] = preguntas_respuestas

        # Guardar cada pregunta en una variable
        pregunta1 = "¿Qué actividades disfrutas hacer en tu tiempo libre? "
        pregunta2 = "¿Hay alguna materia en la escuela que te guste más que las demás? ¿Cuál y por qué? "
        pregunta3 = "¿Participas en algún club, grupo o equipo dentro o fuera de la escuela? ¿Cuál es tu rol en ese grupo? "
        pregunta4 = "¿Hay algún pasatiempo o actividad extracurricular que te apasione? "
        pregunta5 = "¿Qué especialidad estudias? "
        pregunta6 = "¿Hay alguna actividad o tarea que encuentres fácil de realizar y que otras personas consideren difícil? "
        pregunta7 = "¿Prefieres trabajar solo o en equipo? ¿Por qué? "
        pregunta8 = "¿Te sientes cómodo(a) utilizando tecnología? Si es así, ¿qué tipo de tecnología disfrutas usar más? "
        pregunta9 = "¿Qué es lo más importante para ti en un trabajo o carrera? "
        pregunta10 = "¿Te sientes más motivado(a) cuando estás trabajando en un proyecto creativo o en una tarea analítica? "
        pregunta11 = "¿Te gusta enfrentar nuevos desafíos o prefieres tareas más predecibles y estructuradas? "
        pregunta12 = "¿Has tenido alguna experiencia laboral o de voluntariado? ¿Cómo fue esa experiencia? "
        pregunta13 = "¿Hay algún trabajo o actividad que hayas realizado en el pasado que no te haya gustado? ¿Por qué? "
        pregunta14 = "¿Has tenido alguna asignatura o proyecto escolar que te haya resultado especialmente interesante o satisfactorio? "
        pregunta15 = "¿Tienes alguna idea sobre qué carrera o profesión te gustaría seguir en el futuro? "
        pregunta16 = "¿Qué tipo de empresa o sector te llama más la atención? "
        pregunta17 = "¿Dónde te ves a ti mismo(a) en cinco años? ¿Y en diez años? "
        pregunta18 = "¿Qué aspectos de una empresa consideras importantes para tu desarrollo profesional? "
        pregunta19 = "¿Prefieres un ambiente de trabajo dinámico y cambiante o uno más estable y rutinario? "
        pregunta20 = "¿Te sientes más productivo(a) en un entorno estructurado o en uno más flexible y creativo? "
        pregunta21 = "¿Te interesa más trabajar en una gran empresa o en una pequeña empresa/startup? ¿Por qué? "
        pregunta22 = "¿Qué es lo que más te gustaría aprender durante tus prácticas preprofesionales? "
        pregunta23 = "¿Hay alguna habilidad específica que te gustaría desarrollar? "
        pregunta24 = "¿Qué crees que podrías aportar a una empresa durante tus prácticas? "
        pregunta25 = "¿Qué tipo de apoyo o guía te gustaría recibir durante tus prácticas? "
        pregunta26 = "Si pudieras diseñar tu trabajo ideal, ¿cómo sería? "
        pregunta27 = "¿Qué tipo de impacto te gustaría tener en tu comunidad o en el mundo a través de tu trabajo? "
        
        context ={
            'pregunta1': pregunta1,
            'respuesta1': p1,
            'pregunta2': pregunta2,
            'respuesta2': p2,
            'pregunta3': pregunta3,
            'respuesta3': p3,
            'pregunta4': pregunta4,
            'respuesta4': p4,
            'pregunta5': pregunta5,
            'respuesta5': p5,
            'pregunta6': pregunta6,
            'respuesta6': p6,
            'pregunta7': pregunta7,
            'respuesta7': p7,
            'pregunta8': pregunta8,
            'respuesta8': p8,
            'pregunta9': pregunta9,
            'respuesta9': p9,
            'pregunta10': pregunta10,
            'respuesta10': p10,
            'pregunta11': pregunta11,
            'respuesta11': p11,
            'pregunta12': pregunta12,
            'respuesta12': p12,
            'pregunta13': pregunta13,
            'respuesta13': p13,
            'pregunta14': pregunta14,
            'respuesta14': p14,
            'pregunta15': pregunta15,
            'respuesta15': p15,
            'pregunta16': pregunta16,
            'respuesta16': p16,
            'pregunta17': pregunta17,
            'respuesta17': p17,
            'pregunta18': pregunta18,
            'respuesta18': p18,
            'pregunta19': pregunta19,
            'respuesta19': p19,
            'pregunta20': pregunta20,
            'respuesta20': p20,
            'pregunta21': pregunta21,
            'respuesta21': p21,
            'pregunta22': pregunta22,
            'respuesta22': p22,
            'pregunta23': pregunta23,
            'respuesta23': p23,
            'pregunta24': pregunta24,
            'respuesta24': p24,
            'pregunta25': pregunta25,
            'respuesta25': p25,
            'pregunta26': pregunta26,
            'respuesta26': p26,
            'pregunta27': pregunta27,
            'respuesta27': p27,
        }

    return render(request, 'preguntas_respuestas.html', context)

def formatear_respuesta_a_html(respuesta):
    # Reemplazar saltos de línea por etiquetas <br> y otros formatos
    respuesta_html = respuesta
    
    # Convertir **negrita** a <strong>
    respuesta_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', respuesta_html)
    
    # Convertir - ítem de lista a <li>
    respuesta_html = re.sub(r'(?m)^- (.*)$', r'<li>\1</li>', respuesta_html)
    
    # Convertir títulos con ### a <h2>
    respuesta_html = re.sub(r'(?m)^# (.*)$', r'<h4>\1</h4>', respuesta_html)
    
    # Convertir títulos con #### a <h3>
    respuesta_html = re.sub(r'(?m)^## (.*)$', r'<h4>\1</h4>', respuesta_html)
    
        # Convertir títulos con #### a <h3>
    respuesta_html = re.sub(r'(?m)^### (.*)$', r'<h4 style="color: green">\1</h4>', respuesta_html)
    
    # Convertir números de sección (e.g., 1., 2.) a <h3>
    respuesta_html = re.sub(r'(?m)^(\d+)\. (.*)$', r'<h3>\2</h3>', respuesta_html)
    
    # Convertir párrafos a <p>
    respuesta_html = re.sub(r'(?m)^([^\d#-].*)$', r'<p>\1</p>', respuesta_html)
    
    # Envolver todo en un <div>
    respuesta_html = f'<div>{respuesta_html}</div>'
    
    return respuesta_html

@login_required
def analisis_ia(request):
        # Verificar si hay respuestas en la sesión
    preguntas_respuestas = request.session.get('preguntas_respuestas', [])
    user = request.user  # Obtener el usuario autenticado

    # Verificar si el usuario tiene un perfil válido
    perfil = get_object_or_404(Perfil, user=user)
    if preguntas_respuestas:
        user = request.user
        perfil = Perfil.objects.get(user=user)  # Cambié .filter() a .get() para obtener un solo objeto

        client = OpenAI(api_key="sk-ag9xrx4D-a3SBglAZkLdHrLLDm8iKggBaWtIiB41phT3BlbkFJd-sW3qNse7s_Gs_wNSfG-fJk-5HLAkW_-i0fm4xToA")
        
        prompt = f"""
        Actúa como un psicólogo escolar que analiza las respuestas de un estudiante para determinar su perfil profesional y recomendar un tipo de empresa adecuada para sus prácticas preprofesionales. Necesito que al final concretes la clase de empresa que debera buscar el estudiante y si es posible le des opciones dentro del ambioto Ecuatoriano, especificamente Guayaquil. Las respuestas del estudiante son las siguientes:
        {request.session.get('preguntas_respuestas')}
        Por favor, organiza la respuesta en secciones con los siguientes encabezados:
        1. Análisis general del Perfil
        2. Recomendaciones de Empresas para Prácticas Preprofesionales
        3. Conclusión

        Cada sección debe estar claramente separada y utilizar formato de lista si es necesario. 
        Asegúrate de que la respuesta sea clara y fácil de leer, 
        usando # para los encabezados, ## para subtitulos y un * para listas numeradas o no numeradas para recomendaciones y pasos.
        """
        
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un psicólogo escolar que trabaja como orientador vocacional en un Colegio de Guayaquil."},
                {"role": "user", "content": prompt }
            ],
            max_tokens=1000
        )
        
        respuesta = respuesta = completion.choices[0].message.content
        respuesta_html = formatear_respuesta_a_html(respuesta)
        
        perfil.ia_estado = 'Aprobado'
        perfil.ia_respuesta = respuesta
        perfil.save()

        request.session['estado_ia'] = 'Aprobado'
        context = {'respuesta_html': respuesta_html}
        
        return render(request, 'ia_respuesta.html', context)
    else: 
        # Si no hay respuestas en la sesión, mostrar la respuesta almacenada en el perfil
        respuesta = perfil.ia_respuesta
        respuesta_html = formatear_respuesta_a_html(respuesta)
        context = {'respuesta_html': respuesta_html}
        return render(request, 'ia_respuesta.html', context)

#EMPRESAS
@login_required
def empresas(request):
    # Obtener la palabra clave de búsqueda desde el formulario
    query = request.GET.get('q')
    # Obtener todas las empresas del modelo Empresa
    if query:
        empresas = Empresa.objects.filter(
            Q(nombre_empresa__icontains=query) |
            Q(ruc__icontains=query) |
            Q(direccion__icontains=query)
        )
    else:
        empresas = Empresa.objects.all()
    # Pasar las empresas al contexto
    context = {
        'empresas': empresas,
        'query': query,  # Pasar la consulta de búsqueda al contexto
    }
    return render(request, 'empresas.html', context)

@login_required
def empresas_estudiante(request, pk):
    # Obtener la empresa según el ID proporcionado
    empresa = Empresa.objects.get(id=pk)
    # Filtrar los estudiantes que tienen el estado de carta de aprobación como "Aprobado"
    # y que no tienen tutor asignado (es decir, cuyo campo tutor es None)
    estudiantes_aprobados = Perfil.objects.filter(
        ia_estado='Aprobado',
        tutor_asignado_estado = 'Aprobado'
    )   
    return render(request, 'empresa_asignar.html', {
        'empresa': empresa,
        'estudiantes_aprobados': estudiantes_aprobados,
    })

@login_required
def empresa_asignado(request):
    if request.method == 'POST':
        # Obtiene los IDs del estudiante y del tutor desde el formulario
        estudiante_id = request.POST.get('estudiante_id')
        empresa_id = request.POST.get('empresa_id')
        
        # Busca el estudiante y el tutor en la base de datos
        perfil = get_object_or_404(Perfil, id=estudiante_id)        
        # Asigna el tutor al estudiante
        perfil.empresa_nombre_id= empresa_id
        perfil.empresa_estado = "Aprobado"
        perfil.save()
        # Muestra un mensaje de éxito
        messages.success(request, 'Empresa asignada correctamente.')
        # Redirige a una página de confirmación o a la misma página de asignación
        return redirect('home')  # Cambia 'tutor_asignar' por la URL que corresponda
    else:
        # Si la solicitud no es POST, redirige a una página de error o a la página principal
        messages.error(request, 'Asignacion de Empresa no realizada.')
        return redirect('home')  # Cambia 'home' por la URL que corresponda

@login_required
def reporte_estudiante(request):
    user = request.user
    perfil = Perfil.objects.get(user=user)
    try:
        reporte = Reporte.objects.get(perfil=perfil)
        context = {
            'perfil': perfil,
            'now': timezone.now(),   
            'reporte': reporte
        }
        return render(request, 'reporte.html', context)
    except Reporte.DoesNotExist:
        messages.error(request, 'No se ha realizado el Reporte.')
        return redirect('home')
                    
@login_required
def generar_reporte(request, pk):
    if request.method == 'POST':
        # Actualizar los campos del reporte si se envía un formulario
        conclusiones = request.POST.get('conclusiones')
        observaciones = request.POST.get('observaciones')
        estudiante = request.POST.get('estudiante')
        evaluacion = request.POST.get('evaluacion')
        rector = request.POST.get('rector')
        # Obtener los objetos relacionados
        evaluacion = Evaluacion.objects.get(pk=evaluacion)
        perfil = Perfil.objects.get(pk=estudiante)
        # Crea una nueva instancia de Reporte
        reporte = Reporte(
            evaluacion=evaluacion,
            perfil=perfil,
            conclusiones=conclusiones,
            observaciones=observaciones,
            rector = rector,
        )
        reporte.save() # Guarda la instancia en la base de datos
        perfil.reporte_estado = 'Espera'
        perfil.save() # Guarda la instancia en la db

        # Agregar un mensaje de éxito o redirigir si es necesario
        messages.success(request, 'Reporte generado exitosamente.')
        return redirect('evaluacion_aprobada_lista')  # Redirigir a otra vista si es necesario
    else:
    # Pasar los datos al contexto para renderizar en la plantilla
        # Obtener la evaluación usando el pk proporcionado
        evaluacion = get_object_or_404(Evaluacion, pk=pk)
        # Obtener el perfil del estudiante asociado a la evaluación
        perfil = Perfil.objects.get(pk = evaluacion.perfil)
        if perfil.reporte_numero == 4 and perfil.reporte_estado == 'Espera1':
            # Obtener o crear un reporte relacionado a la evaluación, perfil y empresa
            rol = Rol.objects.get(nombre = 'Rector')
            perfil_rector = Perfil.objects.get(rol = rol.pk)
            context = {
                'evaluacion': evaluacion,
                'perfil': perfil,
                'now': timezone.now(),   
                'perfil_rector': perfil_rector
                }
            return render(request, 'generar_reporte.html', context)
        elif perfil.reporte_numero == 4 and perfil.reporte_estado == 'Aprobado':
            # Obtener o crear un reporte relacionado a la evaluación, perfil y empresa
            rol = Rol.objects.get(nombre = 'Rector')
            perfil_rector = Perfil.objects.get(rol = rol.pk)
            reporte = Reporte.objects.get(perfil = perfil)
            context = {
                'evaluacion': evaluacion,
                'perfil': perfil,
                'now': timezone.now(),   
                'perfil_rector': perfil_rector,
                'reporte': reporte
                }
            return render(request, 'reporte.html', context)
        else :
            messages.error(request,'No se puede realizar el Reporte Final debido a que faltan actividades.')
            return redirect('evaluacion_aprobada_lista')

@login_required
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'cambiar_contrasena.html'
    success_url = '/cambiar-contrasena-exito/'

@login_required
def listar_usuarios_no_estudiantes(request):
    admin = get_object_or_404(Rol, nombre="Administrador")
    # Obtener la palabra clave de la búsqueda
    query = request.GET.get('q')    
    # Filtrar perfiles que no son administradores
    perfiles = Perfil.objects.exclude(rol=admin)
    
    if query:
        perfiles = perfiles.filter(
            Q(user__username__icontains=query) | Q(rol__nombre__icontains=query)
        )
    # Obtener todos los roles para el cambio de rol
    roles = Rol.objects.all()
    context = {
        'perfiles': perfiles,
        'roles': roles,
    }
    return render(request, 'listar_usuarios_no_estudiantes.html', context)

@login_required
@require_POST
def cambiar_rol(request, pk):
    perfil = get_object_or_404(Perfil, pk=pk)
    nuevo_rol_id = request.POST.get('nuevo_rol')
    if nuevo_rol_id:
        nuevo_rol = get_object_or_404(Rol, pk=nuevo_rol_id)
        perfil.rol = nuevo_rol
        perfil.save()
        messages.success(request, f'Rol actualizado a {nuevo_rol.nombre} para el usuario {perfil.user.username}.')
    else:
        messages.error(request, 'Debe seleccionar un rol válido.')
    
    return redirect('listar_usuarios_no_estudiantes')

@login_required
def listar_usuarios(request):
    # Obtener todos los usuarios excepto el superusuario o algunos usuarios que desees proteger
    rol_admin = Rol.objects.get(nombre='Administrador')
    usuarios = Perfil.objects.exclude(rol=rol_admin.pk)
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'listar_usuarios.html', context)

@login_required
@require_POST
def eliminar_usuario(request, pk):
    # Obtener el usuario por su clave primaria
    usuario = get_object_or_404(Perfil, pk=pk)
    # Asegurarse de que el usuario no está intentando eliminar su propia cuenta
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect('listar_usuarios')
    # Eliminar el usuario
    usuario.habilitado = False
    usuario.estado_ingreso = 'Espera'
    usuario.save()
    messages.success(request, f'El usuario ha sido Deshabilitado.')
    return redirect('listar_usuarios')

@login_required
@require_POST
def habilitar_usuario(request, pk):
    # Obtener el usuario por su clave primaria
    usuario = get_object_or_404(Perfil, pk=pk)
    # Asegurarse de que el usuario no está intentando eliminar su propia cuenta
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect('listar_usuarios')
    # Eliminar el usuario
    usuario.habilitado = True
    usuario.estado_ingreso = 'Aprobado'
    usuario.save()
    messages.success(request, f'El usuario ha sido Habilitado.')
    return redirect('listar_usuarios')

@login_required
def generar_pdf(request, pk):
    reporte = get_object_or_404(Reporte, pk=pk)
    perfil = reporte.perfil
    perfil_rector = reporte.rector

    # Renderiza el HTML a una cadena
    html_string = render_to_string('reportePDF.html', {
        'reporte': reporte,
        'perfil': perfil,
    })

    # Crear una respuesta como PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_final.pdf"'

    # Convertir HTML a PDF usando xhtml2pdf
    pisa_status = pisa.CreatePDF(html_string, dest=response)

    # Verificar si hubo errores
    if pisa_status.err:
        return HttpResponse('Hubo un error al generar el PDF', status=500)
    
    return response
    
    
    
    
