from django.urls import path
from .views import RegisterView, UserLoginView, UserLogoutView, test_smtp
from .views import SMTPSettingUpdateView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('smtp-settings/',SMTPSettingUpdateView.as_view(),name='smtp_settings'),
    path('test-smtp/',test_smtp,name='test_smtp'),

]