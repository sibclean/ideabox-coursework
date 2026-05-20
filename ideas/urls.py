from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

# Импортируем views целиком, чтобы не перечислять каждую функцию
from . import views 

urlpatterns = [
    path('rprxjqflsyafjeqvmzykxfpvsgxbqgxfnftrfznufxknl/', admin.site.urls),
    path('teacher-manager/', views.teacher_manager, name='teacher_manager'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('', views.idea_list, name='idea_list'), # Главная страница
    
    path('add/', views.idea_create, name='idea_add'), # Создание
    
    path('idea/<int:pk>/', views.idea_detail, name='idea_detail'), 
    
    path('idea/<int:pk>/edit/', views.idea_edit, name='idea_update'), # Редактирование
    path('idea/<int:pk>/delete/', views.idea_delete, name='idea_delete'), # Удаление
    
    path('idea/<int:pk>/join/', views.join_team, name='join_team'), # Присоединиться (Новая форма)

    path('profile/', views.profile_edit, name='profile_edit'),
    path('my-ideas/', views.my_ideas_list, name='my_ideas_list'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_use, name='terms_of_use'),
    path('my-ideas/requests/', views.manage_requests, name='manage_requests'),
    path('respond-request/<int:req_id>/<str:action>/', views.respond_to_request, name='respond_to_request'),
    path('messages/', views.chat_list_view, name='chat_list'), # Список всех диалогов
    path('chat/<int:conversation_id>/', views.chat_room, name='chat_room'), # Это маршрут самой комнаты чата (если еще не добавил)
    path('moderation/', views.moderation_panel, name='moderation_panel'),
    path('moderation/<int:pk>/<str:action>/', views.moderate_idea, name='moderate_idea'),
    path('chat/<int:conversation_id>/delete/', views.delete_chat, name='delete_chat'),
    path('moderation/chat/<int:idea_id>/', views.start_moderation_chat, name='start_moderation_chat'),
    path('chat/<int:conversation_id>/upload/', views.upload_chat_file, name='upload_chat_file'),
    path('user/<str:username>/', views.public_profile, name='public_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

