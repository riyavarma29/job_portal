from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('profile_view/', views.profile_view, name='profile'),
    path('apply/<int:job_id>/', views.apply_to_job, name='apply_to_job'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('post/', views.post_job, name='post_job'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('jobs/delete/<int:job_id>/', views.delete_job, name='delete_job'),
    path('save_job/<int:job_id>/', views.save_job, name='save_job'),
    path('my_jobs/', views.my_jobs, name='my_jobs'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('message/<int:job_id>/<int:developer_id>/', views.message_exchange, name='message_exchange'),
    path('job/<int:job_id>/applicants/', views.view_applicants, name='view_applicants'),
    path('finalize/<int:app_id>/<str:status>/', views.finalize_job, name='finalize_job'),
    path('job/<int:job_id>/remove_saved/', views.remove_saved_job, name='remove_saved_job'),
    path('job/<int:job_id>/discard_application/', views.discard_application, name='discard_application'),
    path('chat/<int:user_id>/', views.start_chat, name='start_chat'),

]
