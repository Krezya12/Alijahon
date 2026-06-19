from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.views import *

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('', ProductListView.as_view(), name='home'),
    path('product-detail/<int:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('register', UserCreateView.as_view(), name='register'),
    path('login', LoginFormView.as_view(), name='login'),
    path('category', CategoryListView.as_view(), name='category'),
    path('category/sort-by', ListByCategoryView.as_view(), name='product_by_category'),
    path('admin-page', AdminListView.as_view(), name='admin-page'),
    path('admin-page/operator-page', OperatorListView.as_view(), name='operator-page'),
    path('admin-page/operator-page/order/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('admin-page/operator-page/order/update/<int:pk>', OrderUpdateView.as_view(), name='order-update'),
    path('admin-page/operator-page/order/create', OrderCreateView.as_view(), name='order-create'),
    path('profile/wishlist', WishListView.as_view(), name='wishlist'),
    path('profile/wishlist/fav-del/<int:pk>', FavDelView.as_view(), name='fav-del'),
    path('profile/wishlist/sort-by', FavByCategoryView.as_view(), name='fav-by-ctg'),
    path('admin-page/market/add_fav', FavCreateView.as_view(), name='fav-create'),
    path('admin-page/market', MarketListView.as_view(), name='market'),
    path('admin-page/market/flow-create', CreateFlowView.as_view(), name='flow-create'),
    path('admin-page/market/sort-by', MarketByCategoryView.as_view(), name='market-by-category'),
    path('admin-page/requests', RequestListView.as_view(), name='requests'),
    path('admin-page/urls', UrlListView.as_view(), name='urls'),
    path('admin-page/urls/del/<int:pk>', FlowDeleteView.as_view(), name='flow-del'),
    path('admin-page/competition', CompetitionListView.as_view(), name='competition'),
    path('admin-page/withdraw', WithdrawListView.as_view(), name='withdraw'),
    path('admin-page/withdraw/transaction', TransactionCreateView.as_view(), name='transaction'),
    path('admin-page/stats', StatsListView.as_view(), name='statistic'),
    path('profile/referral', ReferralListView.as_view(), name='referral'),
    path('profile/settings/update/<int:pk>', SettingsUpdateView.as_view(), name='profile-update'),
    path('profile/settings', SettingsListView.as_view(), name='settings'),
    path('profile/logout', LogoutView.as_view(next_page='home'), name='logout'),
    path('ajax/get-districts/', get_districts_by_region, name='get_districts'),

]
