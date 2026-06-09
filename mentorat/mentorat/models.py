from django.db import models
from django.conf import settings


class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom


class Mentorat(models.Model):
    TYPE_CHOICES = [
        ('offre', 'Offre'),
        ('demande', 'Demande'),
    ]
    FORMAT_CHOICES = [
        ('online', 'En ligne'),
        ('presentiel', 'Présentiel'),
        ('les_deux', 'Les deux'),
    ]
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('fermé', 'Fermé'),
        ('en_cours', 'En cours'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentorats'
    )
    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.SET_NULL,
        null=True
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    format = models.CharField(max_length=15, choices=FORMAT_CHOICES)
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='actif'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.user} - {self.matiere}"


class Matching(models.Model):
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matchings_mentor'
    )
    mentore = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matchings_mentore'
    )
    score = models.FloatField(default=0.0)
    competence_score = models.FloatField(default=0.0)
    disponibilite_score = models.FloatField(default=0.0)
    filiere_score = models.FloatField(default=0.0)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match {self.mentor} → {self.mentore} ({self.score})"


from django.db import models

# Create your models here.
