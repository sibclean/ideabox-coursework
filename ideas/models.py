# ideas/models.py - Структура данных (модели) для приложения 'ideas'

from django.db import models 
from django.contrib.auth.models import User 
from django.utils.translation import gettext_lazy as _ 
from PIL import Image


class Category(models.Model):
    """Модель для категорий идей."""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Название категории"))

    class Meta:
        verbose_name = _("Категория") 
        verbose_name_plural = _("Категории") 
        ordering = ['name'] 

    def __str__(self):
        return self.name


class Idea(models.Model):
    """Основная модель для хранения информации об идеях."""
    class Status(models.TextChoices):
        MODERATION = 'MOD', _('На модерации') 
        APPROVED = 'APP', _('Одобрена')     
        REJECTED = 'REJ', _('Отклонена')    

    title = models.CharField(max_length=200, verbose_name=_("Название идеи")) 
    description = models.TextField(verbose_name=_("Подробное описание")) 
    categories = models.ManyToManyField(
        Category, 
        related_name='ideas', 
        verbose_name=_("Категории"), 
        blank=False 
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ideas', 
        verbose_name=_("Автор")
    )
    status = models.CharField(
        max_length=3, 
        choices=Status.choices, 
        default=Status.MODERATION, 
        verbose_name=_("Статус")
    )
    required_people_tags = models.TextField(
        blank=True, 
        verbose_name=_("Кто нужен в команду (теги или текст)"),
        help_text=_("Укажите требуемые роли, навыки или просто текстом") 
    )
    contact_info = models.TextField(verbose_name=_("Контактная информация для связи"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        verbose_name = _("Идея") 
        verbose_name_plural = _("Идеи") 
        ordering = ['-created_at'] 

    def get_roles_list(self):
        if self.required_people_tags:
            return [role.strip() for role in self.required_people_tags.split(',')]
        return []

    def __str__(self):
        return self.title
    cover_image = models.ImageField(upload_to='idea_covers/', null=True, blank=True, verbose_name="Обложка проекта")
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.cover_image:
            img = Image.open(self.cover_image.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.cover_image.path, quality=85)


class UserProfile(models.Model):
    """Модель Профиля пользователя с расширенной ролевой моделью."""
    class Role(models.TextChoices):
        STUDENT = 'STU', _('Студент')
        TEACHER = 'TCH', _('Преподаватель')

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE, 
        related_name='profile', 
        primary_key=True, 
        verbose_name=_("Пользователь")
    )
    role = models.CharField(
        max_length=3,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_("Роль в системе")
    )
    first_name = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name=_("Имя")
    )
    last_name = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name=_("Фамилия")
    )
    university = models.CharField(
        max_length=255,
        blank=True, 
        verbose_name=_("Университет")
    )
    course_year = models.PositiveSmallIntegerField(
        blank=True, 
        null=True,  
        verbose_name=_("Курс")
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True, 
        verbose_name=_("Аватарка")
    )

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.last_name} {self.first_name} ({self.user.username}) — {self.get_role_display()}"
        return f"Профиль {self.user.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            img = Image.open(self.avatar.path)
            # Если фотка больше 500x500, сжимаем ее
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
                img.save(self.avatar.path, quality=85)    


class TeamRequest(models.Model):
    """Модель заявки на вступление в команду проекта."""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    ]
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField("Роль", max_length=100)
    contact_info = models.CharField("Contacts", max_length=255)
    message = models.TextField("О себе / Сообщение")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.idea.title}"


class Conversation(models.Model):
    """Чат: может быть личным (по заявке) или групповым (по проекту)."""
    
    # Сделали null=True, blank=True, потому что у группового чата заявки нет
    request = models.OneToOneField(
        'TeamRequest', 
        on_delete=models.CASCADE, 
        related_name='conversation', 
        verbose_name=_("Заявка (Личный чат)"),
        null=True, 
        blank=True
    )
    
    # Новые поля для группового чата
    idea = models.OneToOneField(
        'Idea', 
        on_delete=models.CASCADE, 
        related_name='group_chat', 
        verbose_name=_("Идея (Групповой чат)"),
        null=True, 
        blank=True
    )
    participants = models.ManyToManyField(
        User, 
        related_name='group_conversations', 
        verbose_name=_("Участники чата"),
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    class Meta:
        verbose_name = _("Чат")
        verbose_name_plural = _("Чаты")

    def __str__(self):
        if self.idea:
            return f"Групповой чат проекта: {self.idea.title}"
        elif self.request:
            return f"Личный чат по заявке #{self.request.id}"
        return f"Чат #{self.id}"

class Message(models.Model):
    """Сообщение в чате."""
    conversation = models.ForeignKey(
        'Conversation', 
        on_delete=models.CASCADE, 
        related_name='messages', 
        verbose_name=_("Чат")
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages', 
        verbose_name=_("Отправитель")
    )
    text = models.TextField(verbose_name=_("Текст сообщения"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Отправлено"))
    is_read = models.BooleanField(default=False, verbose_name=_("Прочитано"))

    class Meta:
        verbose_name = _("Сообщение")
        verbose_name_plural = _("Сообщения")
        ordering = ['created_at']

    def __str__(self):
        return f"От {self.sender.username} в {self.created_at.strftime('%H:%M')}"
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)

