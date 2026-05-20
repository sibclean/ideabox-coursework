# ideas/apps.py - Конфигурация моего приложения 'ideas'

from django.apps import AppConfig

# Определяю класс конфигурации для приложения 'ideas'
# Имя класса 'IdeasConfig' я указал в settings.py в INSTALLED_APPS
class IdeasConfig(AppConfig):
    # Устанавливаю тип поля для автоматического первичного ключа 
    default_auto_field = 'django.db.models.BigAutoField'
    # Имя моего приложения
    name = 'ideas'

    # --- Подключение сигналов ---
    # Этот метод 'ready' Django вызывает, когда приложение полностью загружено
    def ready(self):
        # Здесь я импортирую модуль signals.py из моего приложения.Это стандартный способ зарегистрировать обработчики сигналов,которые я определил в signals.py (например, для создания профиля пользователя).
        # Важно делать импорт именно внутри ready(), чтобы избежать проблем при запуске.
        import ideas.signals

