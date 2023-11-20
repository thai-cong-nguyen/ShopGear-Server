from django.shortcuts import render
from .models import Category
# Create your views here.


def index(request):
    obj = Category.objects.all()
    context = {
        'obj': obj
    }
    return render(request, 'index.html', context)
