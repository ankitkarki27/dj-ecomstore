from django.contrib import admin
from django.urls import path,include
from . import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def healthz(request):
    return HttpResponse("OK")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz', healthz),
   
    path('', include('store.urls')),    
    
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
# media url kind of last code for profile like things