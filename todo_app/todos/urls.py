from django.urls import path
from .views import (
    RegisterView, LoginView, ToDoListCreateView, ToDoDetailView,
    GroupListCreateView, GroupDetailView, AdminAssignToDoView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('todos/', ToDoListCreateView.as_view(), name='todo-list'),
    path('todos/<int:pk>/', ToDoDetailView.as_view(), name='todo-detail'),
    path('groups/', GroupListCreateView.as_view(), name='group-list'),
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group-detail'),
    path('admin/assign-todo/', AdminAssignToDoView.as_view(), name='admin-assign-todo'),
]
