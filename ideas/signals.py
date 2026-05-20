from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile, Idea, TeamRequest, Conversation


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(pre_save, sender=Idea)
def check_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_idea = Idea.objects.get(pk=instance.pk)
    except Idea.DoesNotExist:
        return

    if old_idea.status != instance.status:
        send_status_email(instance)

def send_status_email(idea):
    subject = f"Изменение статуса вашей идеи: {idea.title}"
    status_display = idea.get_status_display()
    
    message = f"""
    Здравствуйте, {idea.author.username}!
    
    Статус вашего проекта "{idea.title}" был изменен.
    
    Новый статус: {status_display}
    
    С уважением, Администрация.
    """
    
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [idea.author.email], fail_silently=False)
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")

@receiver(post_save, sender=TeamRequest)
def handle_team_request_changes(sender, instance, created, **kwargs):
    # 1. При создании новой заявки — создаем личный чат "1-на-1"
    if created:
        Conversation.objects.get_or_create(request=instance)
    
    if instance.status == 'accepted':
        # Ищем или создаем групповой чат для этой идеи
        group_chat, _ = Conversation.objects.get_or_create(idea=instance.idea)
        
        # Добавляем автора идеи (если его там еще нет)
        group_chat.participants.add(instance.idea.author)
        # Добавляем принятого кандидата
        group_chat.participants.add(instance.user)

@receiver(post_save, sender=TeamRequest)
def create_conversation_for_request(sender, instance, created, **kwargs):
    if created:
        # ЗАМЕНИЛИ .create НА .get_or_create
        Conversation.objects.get_or_create(request=instance)



