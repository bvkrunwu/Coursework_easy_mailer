from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone_number", "is_staff", "is_active", "user_groups", "date_joined")
    list_editable = ("is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "groups")
    search_fields = ("email",)
    ordering = ("email",)
    exclude = ("password",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("groups")

    def user_groups(self, obj):
        groups = obj.groups.all()
        if not groups:
            return "Нет групп"
        group_names = [group.name for group in groups]
        if len(group_names) > 3:
            return f"{', '.join(group_names[:3])} и др."
        return ", ".join(group_names)

    user_groups.short_description = "Группы"
