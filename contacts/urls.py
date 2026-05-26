from django.urls import path
from .views import CSVUploadView
from .views import (
    ContactListView,
    ContactCreateView,
    ContactUpdateView,
    ContactDeleteView
)

urlpatterns = [
    path('', ContactListView.as_view(), name='contact_list'),

    path('create/',
         ContactCreateView.as_view(),
         name='contact_create'),

    path('<int:pk>/update/',
         ContactUpdateView.as_view(),
         name='contact_update'),

    path('<int:pk>/delete/',
         ContactDeleteView.as_view(),
         name='contact_delete'),
    path(
    'upload/',
    CSVUploadView.as_view(),
    name='contact_upload'
),
]