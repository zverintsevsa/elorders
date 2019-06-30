from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django.urls import path, reverse

from . import views


app_name = 'tcsystem'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='tcsystem:your-orders')),
    path('your-orders/', views.YourOrderListView.as_view(), name='your-orders'),
    path('for-you-orders/', views.ForYouOrderListView.as_view(), name='for-you-orders'),
    path('for-signing-orders/', views.ForSigningOrderListView.as_view(), name='for-signing-orders'),

    path('order-create/', views.OrderCreateView.as_view(), name='order-create'),
    path('order-detail/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('order-detail/<int:pk>/comment-create/', views.CommentCreateView.as_view(), name='comment-create'),
    path('order-detail/<int:pk>/sign/', views.OrderSignView.as_view(), name='order-sign'),
    path('order-detail/<int:pk>/hash/', views.GetOrderHashView.as_view(), name='get-hash'),
    
    path('user-list/', views.UserListView.as_view(), name='user-list'),
    path('user-detail/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('group-list/', views.GroupListView.as_view(), name='group-list'),
    path('group-detail/<int:pk>/', views.GroupDetailView.as_view(), name='group-detail'),
    path('personal-group-detail/<int:pk>/', views.PersonalGroupDetailView.as_view(), name='personal-group-detail'),
    path('personal-group-create/', views.PersonalGroupCreateView.as_view(), name='personal-group-create'),

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/passwordchange/<int:pk>/', auth_views.PasswordChangeView.as_view(), name='passwordchange'),
    
    path('chat/<int:pk>/', views.ChatView.as_view(), name='chat'),
    path('chat-list/', views.ChatListView.as_view(), name='chat-list'),
    path('open-chat/<int:pk>/', views.OpenChatView.as_view(), name='open-chat'),
]