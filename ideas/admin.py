# ideas/admin.py - Здесь я настраиваю, как мои модели будут выглядеть в админке Django

from django.contrib import admin
from .models import Category, Idea, UserProfile, TeamRequest, Conversation, Message

class CategoryAdmin(admin.ModelAdmin):
    """Мои настройки для отображения Категорий в админ-панели."""
    # В списке категорий хочу видеть только название
    list_display = ('name',)
    # И хочу, чтобы можно было искать категорию по имени
    search_fields = ('name',)


class IdeaAdmin(admin.ModelAdmin):
    """Мои настройки для отображения Идей в админ-панели."""

    # Какие колонки показывать в списке всех идей
    list_display = (
        'title',            # Название идеи
        'author',           # Кто автор
        'display_categories', # Поле категорий (использую свой метод для красивого вывода)
        'status',           # Текущий статус (модерация, одобрена, отклонена)
        'created_at',       # Когда создана
    )
    # По каким полям можно будет фильтровать идеи в админке
    list_filter = (
        'status',       # По статусу
        'categories',   # По связанным категориям (использую новое поле ManyToMany)
        'created_at',   # По дате создания
    )
    # По каким полям будет работать поиск
    search_fields = (
        'title',            # По названию
        'description',      # По описанию
        'author__username', # Можно искать даже по имени пользователя автора (через связь ForeignKey)
    )
    # Поля, которые нельзя будет редактировать на странице изменения идеи
    # Даты ставятся автоматом, автора назначаем при создании
    readonly_fields = ('created_at', 'updated_at', 'author')

    # Добавляю свои действия для массовой обработки идей
    actions = ['make_approved', 'make_rejected']

    # Виджет с двумя колонками для удобного выбора нескольких категорий
    # (работает для полей ManyToManyField)
    filter_horizontal = ('categories',) # Можно использовать 'filter_vertical', если больше нравится вертикальный вид

    # Группирую поля на странице редактирования идеи для порядка
    fieldsets = (
        # Первая секция - основное (без заголовка)
        (None, {
            'fields': ('title', 'description', 'categories') # Использую новое поле 'categories'
        }),
        # Вторая секция - про статус и даты (сделаю её сворачиваемой)
        ('Метаданные', {
            'fields': ('status', 'created_at', 'updated_at'),
            'classes': ('collapse',) # Добавляет возможность скрыть/показать секцию
        }),
        # Отдельно покажу автора (он readonly)
        ('Автор (не редактируется)', {
            'fields': ('author',),
        }),
        # Секция про команду и контакты
        ('Детали для команды', {
            'fields': ('required_people_tags', 'contact_info')
        }),
    )

    # Мой метод, чтобы красиво показать категории в списке идей (в list_display)
    @admin.display(description='Категории') # Заголовок колонки
    def display_categories(self, obj):
        """Отображает категории идеи через запятую."""
        return ", ".join([cat.name for cat in obj.categories.all()[:3]])

    # Моё действие для одобрения идей
    @admin.action(description='Одобрить выбранные идеи') # Название действия в выпадающем списке
    def make_approved(self, request, queryset):
        """Устанавливает статус 'Одобрена' для выбранных идей (queryset)."""
        # queryset - это набор объектов Idea, которые я выбрал галочками
        queryset.update(status=Idea.Status.APPROVED) # Меняю статус у всех разом
        # Показываю сообщение админу об успехе
        self.message_user(request, "Выбранные идеи были одобрены.")

    # Моё действие для отклонения идей
    @admin.action(description='Отклонить выбранные идеи')
    def make_rejected(self, request, queryset):
        """Устанавливает статус 'Отклонена' для выбранных идей."""
        queryset.update(status=Idea.Status.REJECTED)
        # Сюда можно будет добавить отправку email авторам об отклонении
        self.message_user(request, "Выбранные идеи были отклонены.")

    # Переопределяю стандартный метод сохранения модели в админке
    def save_model(self, request, obj, form, change):
        # Если объект новый (т.е. создается через админку, а не редактируется)
        if not obj.pk:
            # Назначаю текущего пользователя админки автором идеи
            obj.author = request.user
        # Вызываю стандартный метод сохранения родительского класса
        super().save_model(request, obj, form, change)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Idea, IdeaAdmin)
admin.site.register(UserProfile)
