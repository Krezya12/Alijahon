from django.db.models import Q
from apps.models import *

class SearchMixin:

    def get_queryset(self):
        queryset = super().get_queryset()

        # Забираем поисковый запрос
        query = self.request.GET.get('q', '').strip()

        if query:
            # Логируем в историю поиска для авторизованных
            if self.request.user.is_authenticated:
                History.objects.get_or_create(
                    user=self.request.user,
                    request=query
                )

            if hasattr(queryset.model, 'title'):
                queryset = queryset.filter(
                    Q(title__icontains=query) | Q(description__icontains=query)
                ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Прокидываем query и категории, чтобы base.html всегда их видел
        context['search_query'] = self.request.GET.get('q', '').strip()
        context['categories'] = Category.objects.all()
        return context