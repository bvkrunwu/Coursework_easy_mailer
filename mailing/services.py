from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from .models import Campaign, DeliveryAttempt, Subscriber


def run_mail(request, pk):
    mailing = Campaign.objects.get(pk=pk)
    current_time = timezone.now()

    # Проверка владельца рассылки
    if mailing.owner != request.user:
        messages.error(request, "Вы не имеете прав на запуск этой рассылки.")
        return HttpResponseRedirect(reverse("mailing:campaign_list"))

    if mailing.start_time <= current_time <= mailing.end_time:
        mailing.update_status()

        for recipient in mailing.recipients.filter(is_active=True):
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )

                DeliveryAttempt.objects.create(
                    campaign=mailing,
                    delivery_status=DeliveryAttempt.STATUS_SUCCESS,
                    server_response="Email sent successfully",
                )

            except SMTPException as smtp_err:
                DeliveryAttempt.objects.create(
                    campaign=mailing,
                    delivery_status=DeliveryAttempt.STATUS_FAILED,
                    server_response=f"SMTP Error: {smtp_err}",
                )

            except Exception as general_err:
                print(f"General error occurred while processing {recipient.email}: {general_err}")

        messages.success(request, "Рассылка успешно запущена!")
        return HttpResponseRedirect(reverse("mailing:campaign_list"))
    else:
        messages.error(request, "Рассылка не может быть запущена в данный момент.")
        return HttpResponseRedirect(reverse("mailing:campaign_list"))


def get_clients_from_cache():
    if not settings.CACHE_ENABLED:
        return Subscriber.objects.all()

    key = "client_list"
    cached_data = cache.get(key)

    if cached_data is not None:
        return cached_data

    subscribers = Subscriber.objects.all()
    cache.set(key, subscribers)

    return subscribers
