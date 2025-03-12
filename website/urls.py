from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    #path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('record/<int:pk>', views.customer_record, name='record'),
    path('delete_record/<int:pk>', views.delete_record, name='delete_record'),
    path('add_record/', views.add_record, name='add_record'),
    path('update_record/<int:pk>', views.update_record, name='update_record'),
    path('update_user/', views.update_user, name='update_user'),
    path('ai_dashboard/', views.ai_dashboard, name='ai_dashboard'),
    path('ai_engagement/', views.ai_engagement, name='ai_engagement'),
    path('smart_workflows/', views.smart_workflows, name='smart_workflows'),
    # AI Features
    path('ai/anomaly-detection/', views.anomaly_detection, name='anomaly_detection'),
    path('ai/virtual-agent/', views.virtual_agent_chat, name='virtual_agent_chat'),
    path('ai/customer-insights/<int:customer_id>/', views.customer_insights, name='customer_insights'),
]
