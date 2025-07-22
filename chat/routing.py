from django.urls import re_path
from chat.consumers import memberschat, TaskDashboard, LiveDataDashboard




websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<sender_id>\d+)/(?P<receiver_id>\d+)/$', memberschat),
    re_path(r'^ws/dashboard/(?P<dashboard_name>\w+)/$', TaskDashboard),
    re_path(r'^ws/dashboard/$', LiveDataDashboard)
]