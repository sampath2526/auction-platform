from django.urls import path
from .views import conversation_list, chat_view, delete_conversation


urlpatterns = [
    path('conversations/', conversation_list, name='conversation_list'),
    path('chat/<int:conversation_id>/', chat_view, name='chat_view'),
    path('conversations/delete/<int:conversation_id>/', delete_conversation, name='delete_conversation'),
 
]
