from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

urlpatterns = [
    path('add/', views.add_data, name='add_default'),
    path('company/', views.iu_detais.as_view(), name='company'),
    path('register/', views.RegisterApi.as_view(), name='register'),
    path('login/', views.LoginApi.as_view(), name='login'),
    path('details/', views.UserDetailsApi.as_view(), name='user_details'),
    path('block/', views.BlockDetailsApi.as_view(), name='blok_details'),
    path('task/', views.TaskManagementApi.as_view(), name='task_management'),
    path('', views.sentry_page, name='sentry'),
    path('sentry/<type>/', views.sentry_operations.as_view(), name='sentry'),
    path('sentry/exc/<type>/', views.sentry_operations.as_view(), name='sentry_exc'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task_ddashboard/', views.task_details_dashboard, name='task_ddashboard')

    # path('token/', views.CustomTokenObtainPairView.as_view(), name='token'),
    # path('restjwt/', obtain_jwt_token, name='rest_jwt'),

]
