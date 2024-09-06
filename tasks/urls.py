from django.urls import path

from .views import *
from .views_auth import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
]
