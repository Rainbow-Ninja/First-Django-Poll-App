from django.http import HttpResponse

def index(request):
  return  HttpResponse("Hello Twitter! :P")

# Create your views here.
