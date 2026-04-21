from django import forms

from mailing.models import Campaign, Message, Subscriber


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class SubscriberForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = "__all__"
        exclude = ("blocking_client", "disabling_mailings", "owner")


class MessageForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = "__all__"
        exclude = ("blocking_sms", "disabling_mailings", "owner")


class CampaignForm(StyleFormMixin, forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=Subscriber.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Получатели",
    )

    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}), label="Дата и время начала отправки"
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}), label="Дата и время окончания отправки"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # получаем пользователя
        super().__init__(*args, **kwargs)

        if self.user:
            # фильтруем получателей только по текущему пользователю
            self.fields["recipients"].queryset = Subscriber.objects.filter(owner=self.user)
        else:
            # если пользователь не передан, очищаем queryset
            self.fields["recipients"].queryset = Subscriber.objects.none()

    class Meta:
        model = Campaign
        fields = ["start_time", "end_time", "status", "is_active", "message", "recipients"]
        exclude = ["owner"]


class SubscriberModeratorForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = "__all__"
        exclude = ["blocking_client", "disabling_mailings"]


class MessageModeratorForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = "__all__"
        exclude = ["blocking_message", "disabling_mailings"]


class CampaignModeratorForm(StyleFormMixin, forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}), label="Дата и время начала отправки"
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}), label="Дата и время окончания отправки"
    )

    recipients = forms.ModelMultipleChoiceField(
        queryset=Subscriber.objects.none(), widget=forms.CheckboxSelectMultiple, required=False, label="Получатели"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["recipients"].queryset = Subscriber.objects.filter(owner=self.user)

    class Meta:
        model = Campaign
        fields = "__all__"
        exclude = []
