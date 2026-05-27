from django.urls import path

from .views import (
    CampaignListView,
    CampaignCreateView
)

urlpatterns = [
    path(
        '',
        CampaignListView.as_view(),
        name='campaign_list'
    ),

    path(
        'create/',
        CampaignCreateView.as_view(),
        name='campaign_create'
    ),
]