from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def home(request):
    return render(request, 'core/base.html')
@login_required
def profile(request):
    return render(request, 'core/base.html')

def login_view(request):
    return render(request, 'core/base.html')

def register_view(request):
    return render(request, 'core/base.html')

def logout_view(request):
    return render(request, 'core/base.html')

def about(request):
    return render(request, 'core/base.html')

def contact(request):
    return render(request, 'core/base.html')
