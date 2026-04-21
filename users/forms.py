from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import BooleanField, ModelForm

from users.models import User


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")


class ProfileEditForm(StyleFormMixin, ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "middle_name", "country", "phone_number", "avatar")
        exclude = ("email",)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()


class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="Новый пароль")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Повторите пароль")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")

        return cleaned_data
