from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SMTPServerViewSet, EmailQueueViewSet

router = DefaultRouter()
router.register('smtp', SMTPServerViewSet, basename='smtp')
router.register('queue', EmailQueueViewSet, basename='queue')

urlpatterns = [
    path('', include(router.urls)),
]