from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "filiere", "niveau", "role", "updated_at")
    search_fields = ("user__username", "user__email", "filiere", "competences")
    list_filter = ("role", "filiere", "niveau")

