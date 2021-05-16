from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

# Form validasi login
class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label="Password")

# Form validasi login
class DaftarAkunForm(forms.Form):
    password = forms.CharField(label="Password")
    verif_password = forms.CharField(label="Verifikasi Password")
    skin = forms.IntegerField(label="Skin")
    spawn_awal = forms.CharField(label="Spawn Pertama Kali")

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label="Password Lama")
    new_password = forms.CharField(label="Password Baru")
    confirm_password = forms.CharField(label="Konfirmasi Password Baru")

class SetupForm(forms.Form):
    # Job Sallary
    gaji_montir_listrik = forms.IntegerField(label="Gaji Montir Listrik", widget=forms.TextInput(attrs={
        'type': 'text',
        'class': 'form-control',
        'onchange': "this.parentElement.parentElement.children[2].innerHTML = '';"
    }))
    gaji_pizzaboy = forms.IntegerField(label="Gaji Pizzaboy", widget=forms.TextInput(attrs={
        'type': 'text',
        'class': 'form-control',
        'onchange': "this.parentElement.parentElement.children[2].innerHTML = '';"
    }))
    gaji_sweeper = forms.IntegerField(label="Gaji Sweeper", widget=forms.TextInput(attrs={
        'type': 'text',
        'class': 'form-control',
        'onchange': "this.parentElement.parentElement.children[2].innerHTML = '';"
    }))
    gaji_trashmaster = forms.IntegerField(label="Gaji Trashmaster", widget=forms.TextInput(attrs={
        'type': 'text',
        'class': 'form-control',
        'onchange': "this.parentElement.parentElement.children[2].innerHTML = '';"
    }))
    # Tagihan
    tagihan_denda_sewa_kendaraan = forms.IntegerField(label="Tagihan Denda Sewa Kendaraan", widget=forms.TextInput(attrs={
        'type': 'text',
        'class': 'form-control',
        'onchange': "this.parentElement.parentElement.children[2].innerHTML = '';"
    }))
    tagihan_mati_rs = forms.IntegerField(label="Tagihan Mati RS", widget=forms.TextInput(attrs={
        'type': 'text',
        'class': 'form-control',
        'onchange': "this.parentElement.parentElement.children[2].innerHTML = '';"
    }))
    tagihan_revive = forms.IntegerField(label="Tagihan Revive", widget=forms.TextInput(attrs={
        'type': 'text',
        'class': 'form-control',
        'onchange': "this.parentElement.parentElement.children[2].innerHTML = '';"
    }))

class MappingForm(forms.Form):
    mapping_name = forms.CharField(label="Nama Mapping", widget=forms.TextInput(attrs={
        'type': 'text',
        'class': 'form-control',
    }),
    validators=[validators.validate_slug])
    keterangan = forms.CharField(label="Keterangan", widget=forms.TextInput(attrs={
        'type': 'text',
        'class': 'form-control',
    }))
    objects = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
    }))