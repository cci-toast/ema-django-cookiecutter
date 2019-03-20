from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name="homepage.html"), name="home"),
    path('health/', include('health_check.urls')),
    path('admin/', admin.site.urls),
]
