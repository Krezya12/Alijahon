import logging

from apps.models import User

logger = logging.getLogger(__name__)

class UserActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Код, который выполняется ДО того, как пользователь получит страницу
        first_name = request.user.first_name if request.user.is_authenticated else "Аноним"
        path = request.path

        # Записываем действие в лог
        logger.info(f"Пользователь [{first_name}] перешел на страницу: {path}")

        response = self.get_response(request)
        return response
