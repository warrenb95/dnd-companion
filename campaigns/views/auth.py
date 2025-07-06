from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib import messages

from ..forms import StyledAuthenticationForm


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        form = StyledAuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = StyledAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('campaigns:home')
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, self.template_name, {'form': form})