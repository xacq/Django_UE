# estudiantes/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.forms import PasswordChangeForm


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            perfil = Perfil.objects.create(user=user, rol=self.cleaned_data['rol'])
            perfil.save()
        return user
    

class TutorForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), required=True, label="Rol")

    class Meta:
        model = Tutor
        fields = ['nombre', 'profesion', 'experiencia', 'email', 'password', 'rol']


class RolForm(forms.Form):
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), label="Selecciona un rol")
    

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=(
            'Tu contraseña no puede ser demasiado similar a tu otra información personal. '
            'Tu contraseña debe contener al menos 8 caracteres. '
            'Tu contraseña no puede ser una contraseña comúnmente usada. '
            'Tu contraseña no puede ser completamente numérica.'
        )
    )
    new_password2 = forms.CharField(
        label='Confirmación de nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre_empresa', 'direccion', 'telefono', 'correo_electronico', 'representante', 'supervisor', 'ruc']
        