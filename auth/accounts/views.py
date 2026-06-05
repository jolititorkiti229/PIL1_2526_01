from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, RegisterForm, UserUpdateForm
from .models import Profile


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte cree avec succes.")
            return redirect("profile")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    Profile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html")


@login_required
def edit_profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile,
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profil mis a jour avec succes.")
            return redirect("profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )

