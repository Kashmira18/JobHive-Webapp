from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('inbox/', views.inbox_view, name='inbox'),
    path('start/<int:application_id>/', views.start_chat_view, name='start_chat'),
    path('room/<int:thread_id>/', views.chat_room_view, name='chat_room'),
]
