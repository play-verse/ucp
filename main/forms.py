from django import forms

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
