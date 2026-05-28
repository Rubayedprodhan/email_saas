from django.urls import path
from .views import click_tracking
from .views import (
    CampaignListView,
    CampaignCreateView
)
#from .views import email_open_tracking
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
    path(
    'click/<int:track_id>/',
    click_tracking,
    name='click_tracking'
),
   # path('track/<int:track_id>/',email_open_tracking,name='email_tracking'),
]