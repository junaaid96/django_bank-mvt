from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.views.generic import FormView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class UserRegistration(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    # reverse_lazy is used to delay the reverse lookup until the view is called.
    # reverse_lazy is used in class based views and object, reverse is used in function based views and string.
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        customer = form.save()
        messages.success(self.request, 'Account Created Successfully!')
        login(self.request, customer)
        # here we use super() to call the parent class method form_valid() and pass the form as an argument. that means form_valid calls itself recursively.
        return super().form_valid(form)


class UserLogin(LoginView):
    template_name = 'accounts/user_login.html'

    def get_success_url(self):
        return reverse_lazy('home')


class UserLogout(LogoutView):
    template_name = ''

    def get_success_url(self):
        logout(self.request)
        return reverse_lazy('login')


@method_decorator(login_required, name='dispatch')
class UserBankAccountUpdate(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account Updated Successfully!')
            return redirect('profile')
        else:
            print(form.errors)
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class UserPasswordChange(PasswordChangeView):
    template_name = 'accounts/change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.success(self.request, 'Password Changed Successfully!')

        # send email to user
        user = self.request.user
        email = self.request.user.email
        mail_subject = 'Password Changed Successfully!'
        html_template = 'email/change_password_email.html'

        message = render_to_string(html_template, {
            'user': user,
        })
        send_email = EmailMultiAlternatives(
            mail_subject, message, to=[email]
        )
        send_email.attach_alternative(message, "text/html")
        send_email.send()

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Password Change Failed!')
        return super().form_invalid(form)
