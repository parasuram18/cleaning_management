from django.urls import path
from practice import views



urlpatterns = [
    path('', views.sentry_page, name='sentry'),
    path('sentry/<type>/', views.sentry_operations.as_view(), name='sentry'),
    path('sentry/exc/<type>/', views.sentry_operations.as_view(), name='sentry_exc'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task_ddashboard/', views.task_details_dashboard, name='task_ddashboard'),
    path('file_upload/',views.file_upload_view, name='upload_file_view')
]
