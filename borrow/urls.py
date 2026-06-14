from django.urls import path
from . import views

app_name = "borrow"
urlpatterns = [
    path("requests/", views.BorrowRequestListView.as_view(), name="request_list"),
    path("history/", views.BorrowHistoryView.as_view(), name="history"),
    path("request/<int:book_id>/", views.request_book, name="request_book"),
    path("<int:pk>/approve/", views.approve_request, name="approve"),
    path("<int:pk>/issue/", views.issue_book, name="issue"),
    path("<int:pk>/return/", views.return_book, name="return"),
    path("<int:pk>/reject/", views.reject_request, name="reject"),
]
