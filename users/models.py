from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserCustomManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Поле электронной почты должно быть заполнено.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        # Устанавливаем обязательные поля для суперпользователя
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields["is_staff"]:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")

        if not extra_fields["is_superuser"]:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=50, verbose_name="Имя", blank=True, null=True)
    last_name = models.CharField(max_length=50, verbose_name="Фамилия", blank=True, null=True)
    middle_name = models.CharField(max_length=50, verbose_name="Отчество", blank=True, null=True)
    country = models.CharField(
        max_length=100, verbose_name="Страна", blank=True, null=True, help_text="Введите страну"
    )
    phone_number = models.CharField(
        max_length=35, verbose_name="Номер телефона", blank=True, null=True, help_text="Введите номер телефона"
    )
    avatar = models.ImageField(
        upload_to="users/avatars/", verbose_name="Аватар", blank=True, null=True, help_text="Загрузите свой аватар"
    )

    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
