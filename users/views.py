from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("signup")
    template_name = "signup.html"


def user_contact(request):

    form = ContactForm()

    contact = Contact.objects.get(pk=3)
    form = ContactForm(instance=contact)
    return render(request, 'contact.html', {'form': form})
