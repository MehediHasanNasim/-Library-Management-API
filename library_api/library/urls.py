from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet, 
    BookViewSet, 
    BorrowRecordViewSet, 
    BookReturnViewSet, 
    FineViewSet, 
    SubmissionViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('books', BookViewSet, basename='book')
router.register('borrow-records', BorrowRecordViewSet, basename='borrowrecord')
router.register('book-returns', BookReturnViewSet, basename='bookreturn')
router.register('fines', FineViewSet, basename='fine')
router.register('submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),  
]


