
from django.urls import path, include
from my_app import views
from valid_entry import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('contact', views.contact, name='home'),
    path('events', views.events, name='events'),
    path('events/<int:event_id>', views.event_info, name='events_info'),
    path('events/<int:event_id>/register/<int:form_id>', views.register_event, name='register_event'),
    path('sucess', views.sucess, name='sucess'),
    path('ticket/download/<str:ticket_id>/', views.download_ticket, name='download_ticket'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
