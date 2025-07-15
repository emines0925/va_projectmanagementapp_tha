from django.urls import path
from .views import (
    ManageProjectUsersView, signup_view, UserLoginView, UserLogoutView, 
    ProjectListView, ProjectDetailView, ProjectCreateView, 
    ProjectUpdateView, ProjectDeleteView
)

app_name = 'projects'

urlpatterns = [ 
    path('signup/', signup_view, name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('', ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/update/', ProjectUpdateView.as_view(), name='project-update'),
    path('projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project-delete'),
    path('projects/<int:pk>/manage/', ManageProjectUsersView.as_view(), name='project-manage-users'),
    path('create/', ProjectCreateView.as_view(), name='project-create'),
]