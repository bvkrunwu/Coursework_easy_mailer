import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import CreateView, DetailView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import PasswordResetConfirmForm, PasswordResetRequestForm, ProfileEditForm, UserRegisterForm
from users.models import User


@method_decorator(login_required, name="dispatch")
class UserDetailView(DetailView):
    model = User
    template_name = "users/profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator(login_required, name="dispatch")
class UserUpdateView(UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = "users/edit_profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлён!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return super().form_invalid(form)


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Добро пожаловать в наш сервис!",
            message=f"""Здравствуйте!
Спасибо, что зарегистрировались в нашем сервисе.
Перейдите по ссылке для подтверждения почты {url}
После проверки почты вы сможете войти в свой аккаунт и начать пользоваться всеми возможностями.
С уважением,
Команда нашего сервиса""",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = get_object_or_404(User, email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            reset_url = request.build_absolute_uri(
                reverse("users:password_reset_confirm", kwargs={"uid64": uid, "token": token})
            )

            send_mail(
                subject="Восстановление пароля",
                message=f"Пожалуйста, перейдите по ссылке {reset_url} для сброса пароля",
                from_email=EMAIL_HOST_USER,
                recipient_list=[email],
            )

            return redirect("users:password_reset_done")

    else:
        form = PasswordResetRequestForm()

    return render(request, "users/password_reset_form.html", {"form": form})


def password_reset_confirm(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data["new_password"])
                user.save()

                return redirect("users:password_reset_complete")

        else:
            form = PasswordResetConfirmForm()

        return render(request, "users/password_reset_confirm.html", {"form": form})
    else:
        return redirect("users:password_reset_invalid.html")


def password_reset_complete(request):
    return render(request, "users/password_reset_complete.html")


def password_reset_invalid(request):
    return render(request, "users/password_reset_invalid.html")


def password_reset_done(request):
    return render(request, "users/password_reset_done.html")
