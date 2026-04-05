from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.views.generic.edit import View

from config.settings import EMAIL_HOST_USER
from mailing.forms import (
    CampaignForm,
    CampaignModeratorForm,
    MessageForm,
    MessageModeratorForm,
    SubscriberForm,
    SubscriberModeratorForm,
)
from mailing.models import Campaign, Message, Subscriber


def base(request):
    return render(request, "mailing/base.html")


class Contacts(TemplateView):
    template_name = "mailing/contacts.html"

    def post(self, request):
        name = request.POST.get("name")
        message = request.POST.get("message")
        return HttpResponse(f"Спасибо, {name}! {message} Сообщение получено.")


class MainView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()

        if user.has_perm("mailing.can_view_all_campaigns"):
            context["mail_count"] = Campaign.objects.count()
            context["active_count"] = Campaign.objects.filter(
                status="started", start_time__lte=now, end_time__gte=now
            ).count()
            context["unique_email"] = Subscriber.objects.count()
        else:
            context["mail_count"] = Campaign.objects.filter(owner=user).count()
            context["active_count"] = Campaign.objects.filter(
                owner=user, status="started", start_time__lte=now, end_time__gte=now
            ).count()
            context["unique_email"] = Subscriber.objects.filter(owner=user).count()

        return context


class BlockSubscriberView(PermissionRequiredMixin, View):
    permission_required = "mailing.can_block_subscriber"
    raise_exception = True

    def post(self, request, pk):
        subscriber = get_object_or_404(Subscriber, pk=pk)
        subscriber.is_active = not subscriber.is_active
        subscriber.save()
        return JsonResponse({"status": "ok"})


class SubscriberListView(LoginRequiredMixin, ListView):
    model = Subscriber
    template_name = "mailing/subscriber_list.html"
    context_object_name = "subscribers"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_subscribers"):
            return Subscriber.objects.all()
        else:
            return Subscriber.objects.filter(owner=user)


class SubscriberDetailView(LoginRequiredMixin, DetailView):
    model = Subscriber
    template_name = "mailing/subscriber_detail.html"
    context_object_name = "subscriber"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user.has_perm("mailing.can_view_all_subscribers") or self.request.user == obj.owner:
            return obj
        raise PermissionDenied


class SubscriberCreateView(LoginRequiredMixin, CreateView):
    model = Subscriber
    form_class = SubscriberForm
    success_url = reverse_lazy("mailing:subscriber_list")

    def form_valid(self, form):
        subscriber = form.save(commit=False)
        subscriber.owner = self.request.user
        subscriber.save()
        return super().form_valid(form)


class SubscriberUpdateView(LoginRequiredMixin, UpdateView):
    model = Subscriber
    form_class = SubscriberForm
    success_url = reverse_lazy("mailing:subscriber_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user == obj.owner:
            return obj
        raise PermissionDenied

    def get_form_class(self):
        user = self.request.user
        if user.has_perm("mailing.can_block_subscriber"):  # Исправлено на корректное разрешение
            return SubscriberModeratorForm
        return SubscriberForm

    def form_valid(self, form):
        subscriber = form.save(commit=False)
        subscriber.save()
        form.save_m2m()
        return super().form_valid(form)


class SubscriberDeleteView(LoginRequiredMixin, DeleteView):
    model = Subscriber
    success_url = reverse_lazy("mailing:subscriber_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user == obj.owner:
            return obj
        raise PermissionDenied


class MessageListView(ListView):
    model = Message


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user == obj.owner:
            return obj
        raise PermissionDenied


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        message = form.save(commit=False)
        message.owner = self.request.user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user == obj.owner:
            return obj
        raise PermissionDenied

    def get_form_class(self):
        user = self.request.user
        if user.has_perm("message.can_unblocking_message") and user.has_perm("message.can_disabling_mailings"):
            return MessageModeratorForm
        return MessageForm


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy("mailing:message_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user == obj.owner:
            return obj
        raise PermissionDenied


class DisableCampaignView(PermissionRequiredMixin, View):
    permission_required = "mailing.can_disable_campaigns"
    raise_exception = True

    def post(self, request, pk):
        campaign = get_object_or_404(Campaign, pk=pk)
        campaign.is_active = False
        campaign.save()
        return JsonResponse({"status": "ok"})


class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = "mailing/campaign_list.html"
    context_object_name = "campaigns"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_campaigns"):  # Для менеджеров
            return Campaign.objects.all()
        else:  # Для обычных пользователей
            return Campaign.objects.filter(owner=user)


class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = "mailing/campaign_detail.html"
    context_object_name = "campaign"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user.has_perm("mailing.can_view_all_campaigns") or self.request.user == obj.owner:
            return obj
        raise PermissionDenied


class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    success_url = reverse_lazy("mailing:campaign_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        campaign = form.save(commit=False)
        campaign.owner = self.request.user
        campaign.save()
        form.save_m2m()
        return super().form_valid(form)


class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    success_url = reverse_lazy("mailing:campaign_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user == obj.owner:
            return obj
        raise PermissionDenied

    def get_form_kwargs(self):
        """Передаём текущего пользователя в форму для фильтрации получателей"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_form_class(self):
        user = self.request.user
        if user.has_perm("mailing.can_unblocking_mailing") and user.has_perm("mailing.can_disabling_mailings"):
            return CampaignModeratorForm
        return CampaignForm

    def form_valid(self, form):
        campaign = form.save(commit=False)
        campaign.owner = self.request.user
        campaign.save()
        form.save_m2m()
        return super().form_valid(form)


class CampaignDeleteView(LoginRequiredMixin, DeleteView):
    model = Campaign
    success_url = reverse_lazy("mailing:campaign_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user == obj.owner:
            return obj
        raise PermissionDenied


class CampaignSendView(LoginRequiredMixin, View):

    def get(self, request, pk, *args, **kwargs):
        mailing = get_object_or_404(Campaign, pk=pk)

        return render(request, "mailing/campaign_send.html", {"mailing": mailing})

    def post(self, request, pk, *args, **kwargs):
        mailing = get_object_or_404(Campaign, pk=pk)

        if mailing and mailing.status == "created" or mailing.status == "launched":
            recipients = mailing.recipients.all()

            for recipient in recipients:
                try:
                    send_mail(mailing.message.subject, mailing.message.body, EMAIL_HOST_USER, [recipient.email])

                    DisabledCampaignView.objects.create(
                        mailing=mailing, status="success", response="Сообщение отправлено успешно"
                    )

                except Exception as e:
                    DisabledCampaignView.objects.create(mailing=mailing, status="not_success", response=str(e))

        mailing.status = "started"
        mailing.save()

        return redirect("mailing:campaign_list")


class CampaignReportView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = "mailing/campaign_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["STATUS_SUCCESS"] = self.object.attempts.filter(status="success").count()
        context["STATUS_SUCCESS"] = self.object.attempts.filter(status="not_success").count()
        context["total_attempts"] = self.object.attempts.count()

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super().get(request, *args, **kwargs)


class DisabledCampaignView(LoginRequiredMixin, View):

    def post(self, request, pk):
        mailing = get_object_or_404(Campaign, id=pk)

        if not request.user.has_perm("mailing.can_disable_campaigns"):
            return HttpResponseForbidden("У вас недостаточно прав для отключения рассылки")

        mailing.status = "completed"
        mailing.save()

        return redirect("mailing:mailing", pk=mailing.id)
