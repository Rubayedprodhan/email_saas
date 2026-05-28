from django.urls import path

from .views import (
    ContactListAPI,
    CampaignListAPI
)

urlpatterns = [

    path(
        'contacts/',
        ContactListAPI.as_view(),
        name='api_contacts'
    ),

    path(
        'campaigns/',
        CampaignListAPI.as_view(),
        name='api_campaigns'
    ),
]