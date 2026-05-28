from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
import pandas as pd
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from .models import Contact
from .forms import CSVUploadForm
from .models import Contact
from .forms import ContactForm


class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = 'contacts/list.html'

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/create.html'
    success_url = reverse_lazy('contact_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/update.html'
    success_url = reverse_lazy('contact_list')

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


class ContactDeleteView(LoginRequiredMixin, DeleteView):
    model = Contact
    template_name = 'contacts/delete.html'
    success_url = reverse_lazy('contact_list')

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)




class CSVUploadView(LoginRequiredMixin, View):

    template_name = 'contacts/upload.html'

    def get(self, request):
        form = CSVUploadForm()

        return render(request,self.template_name,{'form': form})

    def post(self, request):

        form = CSVUploadForm(request.POST,request.FILES)

        if form.is_valid():

            csv_file = request.FILES['file']

            df = pd.read_csv(csv_file)

            for _, row in df.iterrows():

                email = row['email']

                name = row.get('name', '')

                exists = Contact.objects.filter(
                    user=request.user,
                    email=email
                ).exists()

                if not exists:
                    Contact.objects.create(
                        user=request.user,
                        name=name,
                        email=email
                    )

            return redirect('contact_list')

        return render(
            request,
            self.template_name,
            {'form': form}
        )
    
def unsubscribe_contact(
    request,
    contact_id
):

    contact = get_object_or_404(
        Contact,
        id=contact_id
    )

    contact.is_subscribed = False

    contact.save()

    return render(
        request,
        'contacts/unsubscribed.html'
    )