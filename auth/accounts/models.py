from django.conf import settings
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [
        ("mentor", "Mentor"),
        ("mentore", "Mentore"),
        ("both", "Mentor et mentore"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    first_name = models.CharField("Prenom", max_length=100, blank=True)
    last_name = models.CharField("Nom", max_length=100, blank=True)
    filiere = models.CharField(max_length=100, blank=True)
    niveau = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="mentore")
    competences = models.TextField(blank=True)
    centres_interet = models.TextField("Centres d'interet", blank=True)
    disponibilites = models.TextField(blank=True)
    bio = models.TextField("Biographie", blank=True)
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

