import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import ProfileEditForm, UserRegisterForm
from users.models import User


@method_decorator(login_required, name="dispatch")
class UserDetailView(DetailView):
    model = User
    template_name = "profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator(login_required, name="dispatch")
class UserUpdateView(UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = "edit_profile.html"
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
