from django.urls import path

from mailing.apps import MailingConfig
from mailing.views import (
    BlockSubscriberView,
    CampaignCreateView,
    CampaignDeleteView,
    CampaignDetailView,
    CampaignListView,
    CampaignReportView,
    CampaignSendView,
    CampaignUpdateView,
    Contacts,
    DisableCampaignView,
    DisabledCampaignView,
    MainView,
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
    SubscriberCreateView,
    SubscriberDeleteView,
    SubscriberDetailView,
    SubscriberListView,
    SubscriberUpdateView,
)

app_name = MailingConfig.name

urlpatterns = [
    path("", MainView.as_view(), name="main"),
    path("contacts/", Contacts.as_view(), name="contacts"),
    path("subscribers/", SubscriberListView.as_view(), name="subscriber_list"),
    path("subscribers/<int:pk>/", SubscriberDetailView.as_view(), name="subscriber_detail"),
    path("subscribers/create/", SubscriberCreateView.as_view(), name="subscriber_create"),
    path("subscribers/<int:pk>/update/", SubscriberUpdateView.as_view(), name="subscriber_update"),
    path("subscribers/<int:pk>/delete/", SubscriberDeleteView.as_view(), name="subscriber_delete"),
    path("subscriber/block/<int:pk>/", BlockSubscriberView.as_view(), name="block_subscriber"),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("campaigns/", CampaignListView.as_view(), name="campaign_list"),
    path("campaigns/<int:pk>/", CampaignDetailView.as_view(), name="campaign_detail"),
    path("campaigns/create/", CampaignCreateView.as_view(), name="campaign_create"),
    path("campaigns/<int:pk>/update/", CampaignUpdateView.as_view(), name="campaign_update"),
    path("campaigns/<int:pk>/delete/", CampaignDeleteView.as_view(), name="campaign_delete"),
    path("campaign/disable/<int:pk>/", DisableCampaignView.as_view(), name="disable_campaign"),
    path("mailing_send/<int:pk>/", CampaignSendView.as_view(), name="campaign_send"),
    path("mailing_report/<int:pk>/", CampaignReportView.as_view(), name="mailing_report"),
    path("disabling_mailing/<int:pk>/", DisabledCampaignView.as_view(), name="disabling_mailing"),
]
