from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from apps.forms import *
from apps.models import *
from datetime import timedelta
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView, DeleteView


class BaseListView(ListView):
    queryset = Category.objects.all()
    template_name = 'base/base.html'


class ListByCategoryView(ListView):
    queryset = Category.objects.all()
    template_name = 'category.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.request.GET.get('pk')

        context['products'] = Product.objects.filter(category=pk)

        return context


class HomeListView(ListView):
    queryset = Product.objects.all()
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        three_days_ago = timezone.now() - timedelta(days=3)
        context['new_products'] = Product.objects.filter(created_at__gte=three_days_ago).order_by('-created_at')
        context['categories'] = Category.objects.all()
        context['products'] = Product.objects.all()

        return context


class CategoryListView(ListView):
    queryset = Product.objects.all()
    template_name = 'category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()
        context['products'] = Product.objects.all()

        return context


class AdminListView(ListView):
    queryset = Product.objects.all()
    template_name = 'admin_page.html'


class MarketListView(ListView):
    queryset = Product.objects.all()
    template_name = 'market.html'

    def get_context_data(self, *, object_list=..., **kwargs):
        context = super().get_context_data(**kwargs)

        context['products'] = Product.objects.all()
        context['categories'] = Category.objects.all()
        context['fav_ids'] = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)

        return context


class RequestListView(ListView):
    queryset = Product.objects.all()
    template_name = 'requests.html'


class UrlListView(ListView):
    queryset = Flow.objects.all()
    template_name = 'urls.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['flows'] = Flow.objects.all()

        return context


class StatsListView(ListView):
    queryset = Product.objects.all()
    template_name = 'statistic.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        today = timezone.now().date()
        orders = Order.objects.filter(flow__user=user)
        new = timezone.now() - timedelta(days=3)

        context['flows'] = Flow.objects.filter(user=user)
        context['visits'] = Flow.objects.filter(user=user).aggregate(total=Sum('visits'))['total']

        context['today'] = orders.filter(status=Order.StatusType.DELIVERING, delivery_date=today).count()
        context['after'] = orders.filter(status=Order.StatusType.DELIVERING, delivery_date__gt=today).count()
        context['new'] = Flow.objects.filter(created_at__gte=new).count()

        context['packing'] = orders.filter(status=Order.StatusType.PACKING).count()
        context['delivering'] = orders.filter(status=Order.StatusType.DELIVERING).count()
        context['delivered'] = orders.filter(status=Order.StatusType.DELIVERED).count()
        context['postponed'] = orders.filter(status=Order.StatusType.POSTPONED).count()
        context['returned'] = orders.filter(status=Order.StatusType.RETURNED).count()
        context['cancelled'] = orders.filter(status=Order.StatusType.CANCELLED).count()
        context['hold'] = orders.filter(status=Order.StatusType.HOLD).count()
        context['archive'] = orders.filter(status=Order.StatusType.ARCHIVE).count()

        context['products'] = Product.objects.filter(flows__user=user).distinct().annotate(
            visits=Sum('flows__visits', filter=Q(flows__user=user)),

            packing=Count('flows__orders', filter=Q(flows__user=user, flows__orders__status=Order.StatusType.PACKING)),
            delivering=Count('flows__orders',
                             filter=Q(flows__user=user, flows__orders__status=Order.StatusType.DELIVERING)),
            delivered=Count('flows__orders',
                            filter=Q(flows__user=user, flows__orders__status=Order.StatusType.DELIVERED)),
            postponed=Count('flows__orders',
                            filter=Q(flows__user=user, flows__orders__status=Order.StatusType.POSTPONED)),
            returned=Count('flows__orders',
                           filter=Q(flows__user=user, flows__orders__status=Order.StatusType.RETURNED)),
            cancelled=Count('flows__orders',
                            filter=Q(flows__user=user, flows__orders__status=Order.StatusType.CANCELLED)),
            hold=Count('flows__orders', filter=Q(flows__user=user, flows__orders__status=Order.StatusType.HOLD)),
            archive=Count('flows__orders', filter=Q(flows__user=user, flows__orders__status=Order.StatusType.ARCHIVE)),

            today=Count('flows__orders', filter=Q(
                flows__user=user,
                flows__orders__status=Order.StatusType.DELIVERING,
                flows__orders__delivery_date=today
            )),
            after=Count('flows__orders', filter=Q(
                flows__user=user,
                flows__orders__status=Order.StatusType.DELIVERING,
                flows__orders__delivery_date__gt=today
            )),
        )

        return context


class CompetitionListView(ListView):
    queryset = Product.objects.all()
    template_name = 'competition.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['users'] = User.objects.all().annotate(
            sales=Count('flows__orders', filter=Q(flows__orders__status=Order.StatusType.DELIVERED)))

        return context


class WithdrawListView(ListView):
    queryset = Product.objects.all()
    template_name = 'withdraw.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        context['transactions_count'] = Transaction.objects.filter(user=user).count()

        context['balance'] = user.balance

        context['transactions'] = Transaction.objects.filter(user=user).order_by('-created_at')

        return context


class ReferralListView(ListView):
    queryset = Product.objects.all()
    template_name = 'referral.html'


class SettingsListView(ListView):
    queryset = User.objects.all()
    template_name = 'settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['regions'] = Region.objects.all()
        context['cities'] = City.objects.all()

        return context


class SettingsUpdateView(UpdateView):
    queryset = User.objects.all()
    template_name = 'settings.html'

    success_url = reverse_lazy('admin-page')
    form_class = UserUpdateForm
    pk_url_kwarg = 'pk'


class UserCreateView(CreateView):
    queryset = User.objects.all()
    form_class = UserModelForm
    template_name = 'home.html'
    success_url = reverse_lazy('home')

    def form_invalid(self, form):
        for error_message in form.errors.values():
            messages.error(self.request, error_message)
        return super().form_invalid(form)


class ProductDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = 'product_detail.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        id = self.request.GET.get('id')

        if id:
            context['flow'] = Flow.objects.filter(id=id).first()
            Flow.objects.filter(pk=id, product=self.object).update(visits=F('visits') + 1)


        return context


class LoginFormView(FormView):
    template_name = 'home.html'
    form_class = LoginModelForm
    success_url = reverse_lazy('admin-page')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_invalid(self, form):
        for error_message in form.errors.values():
            messages.error(self.request, error_message)
        return super().form_invalid(form)


class MarketByCategoryView(ListView):
    queryset = Category.objects.all()
    template_name = 'market.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.request.GET.get('pk')

        context['products'] = Product.objects.filter(category=pk)

        return context


class CreateFlowView(CreateView):
    queryset = Flow.objects.all()
    template_name = 'market.html'
    form_class = FlowModelForm
    success_url = reverse_lazy('urls')


class TransactionCreateView(CreateView):
    queryset = Transaction.objects.all()
    template_name = 'withdraw.html'
    form_class = TransactionModelForm
    success_url = reverse_lazy('withdraw')


class WishListView(ListView):
    queryset = Favorite.objects.all()
    template_name = 'wishlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['favorites'] = Favorite.objects.filter(user=self.request.user).order_by('-created_at')
        context['categories'] = Category.objects.all()

        return context


class FavByCategoryView(ListView):
    queryset = Favorite.objects.all()
    template_name = 'wishlist.html'
    context_object_name = 'favorites'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.request.GET.get('pk')

        context['favorites'] = Favorite.objects.filter(user=self.request.user).filter(product__category=pk).order_by('-created_at')
        context['categories'] = Category.objects.all()

        return context


class FavCreateView(CreateView):
    queryset = Favorite.objects.all()
    template_name = 'market.html'
    form_class = FavModelForm
    success_url = reverse_lazy('market')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, *, object_list=..., **kwargs):
        context = super().get_context_data(**kwargs)

        context['products'] = Product.objects.all().order_by('-created_at')
        context['categories'] = Category.objects.all()
        context['fav_ids'] = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)

        return context


class FavDelView(DeleteView):
    queryset = Favorite.objects.all()
    template_name = 'wishlist.html'
    context_object_name = 'favorite'
    success_url = reverse_lazy('wishlist')
    pk_url_kwarg = 'pk'


class FlowDeleteView(DeleteView):
    queryset = Flow.objects.all()
    template_name = 'urls.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('urls')


class OrderDetailView(DetailView):
    queryset = Order.objects.all()
    template_name = 'order-change.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get(self.pk_url_kwarg)

        order = Order.objects.filter(id=pk).first()

        if order.product:
            context['total'] = order.quantity * order.product.price
        elif order.flow:
            context['total'] = order.quantity * order.flow.discount

        context['regions'] = Region.objects.all()

        return context


class OrderUpdateView(UpdateView):
    queryset = Order.objects.all()
    form_class = OrderModelForm
    template_name = 'order-change.html'
    success_url = reverse_lazy('operator-page')
    pk_url_kwarg = 'pk'



class OperatorListView(ListView):
    queryset = Order.objects.all()
    template_name = 'operator-page.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = Order.objects.all()

        status = self.request.GET.get('status')
        category_id = self.request.GET.get('category_id')
        region_id = self.request.GET.get('region_id')
        district_id = self.request.GET.get('district_id')

        if status:
            queryset = queryset.filter(status=status)

        if category_id:
            queryset = queryset.filter(flow__product__category_id=category_id)

        if region_id:
            queryset = queryset.filter(flow__user__city__region_id=region_id)

        if district_id:
            queryset = queryset.filter(flow__user__city_id=district_id)

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['regions'] = Region.objects.all()
        context['cities'] = City.objects.all()
        context['categories'] = Category.objects.all()

        return context


class OrderCreateView(CreateView):
    queryset = Order.objects.all()
    template_name = 'product_detail.html'
    form_class = OrderModelForm
    success_url = reverse_lazy('market')


def get_districts_by_region(request):
    region_id = request.GET.get('region_id')
    city = City.objects.filter(region_id=region_id).values('id', 'title')
    return JsonResponse(list(city), safe=False)




