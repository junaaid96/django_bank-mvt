from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import UserRegistrationForm
from django.contrib.auth import login



class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    # reverse_lazy is used to delay the reverse lookup until the view is called.
    # reverse_lazy is used in class based views and object, reverse is used in function based views and string.
    success_url = reverse_lazy('register')

    def form_valid(self, form):
        customer = form.save()
        login(self.request, customer)
        # here we use super() to call the parent class method form_valid() and pass the form as an argument. that means form_valid calls itself recursively.
        return super().form_valid(form)
