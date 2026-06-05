from django import forms
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    email = forms.EmailField(label="Adresse email", required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        labels = {
            "username": "Nom d'utilisateur",
            "email": "Adresse email",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est deja utilisee.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Profile.objects.create(user=user)
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        labels = {
            "username": "Nom d'utilisateur",
            "email": "Adresse email",
        }


class PasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].help_text = ""
        self.fields["new_password2"].help_text = ""

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Cette adresse email est deja utilisee.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "filiere",
            "niveau",
            "role",
            "competences",
            "centres_interet",
            "disponibilites",
            "bio",
            "photo",
        ]
        widgets = {
            "competences": forms.Textarea(attrs={"rows": 3}),
            "centres_interet": forms.Textarea(attrs={"rows": 3}),
            "disponibilites": forms.Textarea(attrs={"rows": 3}),
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "first_name": "Prenom",
            "last_name": "Nom",
            "filiere": "Filiere",
            "niveau": "Niveau",
            "role": "Role",
            "competences": "Competences",
            "centres_interet": "Centres d'interet",
            "disponibilites": "Disponibilites",
            "bio": "Biographie",
            "photo": "Photo de profil",
        }
