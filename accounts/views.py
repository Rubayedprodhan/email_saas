from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView


from django.contrib.auth.mixins import (
    LoginRequiredMixin
)

from django.views.generic import (
    UpdateView
)

from .models import SMTPSetting
from django.contrib import messages

from django.core.mail import send_mail

from django.core.mail.backends.smtp import (
    EmailBackend
)

from django.shortcuts import redirect
from .forms import SMTPSettingForm
from .forms import RegisterForm

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'


class UserLogoutView(LogoutView):
    next_page = 'login'




class SMTPSettingUpdateView(
    LoginRequiredMixin,
    UpdateView
):

    model = SMTPSetting

    form_class = SMTPSettingForm

    template_name = (
        'accounts/smtp_settings.html'
    )

    success_url = reverse_lazy(
        'smtp_settings'
    )

    def get_object(self):

        smtp_setting, created = (
            SMTPSetting.objects.get_or_create(
                user=self.request.user
            )
        )

        return smtp_setting


def test_smtp(request):

    smtp = SMTPSetting.objects.get(
        user=request.user
    )

    try:

        backend = EmailBackend(

            host=smtp.smtp_host,

            port=smtp.smtp_port,

            username=smtp.smtp_username,

            password=smtp.smtp_password,

            use_tls=smtp.use_tls
        )

        send_mail(

            'SMTP Test Email',

            'SMTP Working Successfully',

            smtp.from_email,

            [request.user.email],

            connection=backend
        )

        messages.success(

            request,

            'SMTP Working Successfully'
        )

    except Exception as e:

        messages.error(

            request,

            str(e)
        )

    return redirect(
        'smtp_settings'
    )