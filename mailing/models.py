from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from users.models import User


class Subscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="Ф.И.О.")
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Статус активности")
    owner = models.ForeignKey(
        User,
        verbose_name="Ответственный",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="owner_subscriber",
    )

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылок"
        ordering = ["full_name"]
        permissions = [
            ("can_block_client", "Can block client"),
        ]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Содержимое письма")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Отправитель", related_name="message_author"
    )

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["subject"]
        permissions = [
            ("can_block_message", "Can block message"),
        ]


class Campaign(models.Model):
    STATUS_CREATED = "created"
    STATUS_STARTED = "started"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_STARTED, "Запущена"),
        (STATUS_COMPLETED, "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_CREATED, verbose_name="Статус рассылки"
    )
    is_active = models.BooleanField(default=True, verbose_name="Рассылка активна")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Subscriber, verbose_name="Получатели")
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name="owner_mailing_campaign"
    )

    def __str__(self):
        return f"Рассылка #{self.id} — {self.message.subject}"

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Дата начала должна быть раньше даты окончания.")
            if self.start_time < timezone.now():
                raise ValidationError("Дата начала не может быть в прошлом.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def update_status(self):
        now = timezone.now()
        if now < self.start_time:
            new_status = self.STATUS_CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.STATUS_STARTED
        else:
            new_status = self.STATUS_COMPLETED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-start_time"]
        permissions = [
            ("set_is_active", "Set is active"),
        ]
        indexes = [
            models.Index(fields=["start_time"]),
        ]


class DeliveryAttempt(models.Model):
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAILED, "Не успешно"),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    delivery_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_SUCCESS, verbose_name="Статус попытки рассылки"
    )
    server_response = models.TextField(verbose_name="Ответ почтового сервера")
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, verbose_name="Рассылка", related_name="delivery_attempts"
    )

    def __str__(self):
        return self.delivery_status

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = [
            "-attempt_time",
        ]
