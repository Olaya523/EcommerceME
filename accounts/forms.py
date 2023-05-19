from django import forms 
from .models import Account 

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Ingrese Contraseña',
        'class' :'form-control'
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Confirmar Contraseña',
        'class' : 'form-control', 
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number','email','password']


    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args ,**kwargs  )
        self.fields['first_name'].widget.attrs['placeholder'] = 'ingrese nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'ingrese apellido'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'ingrese numero celular'
        self.fields['email'].widget.attrs['placeholder'] = 'ingrese email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "La contraseña no coincide "
            )
