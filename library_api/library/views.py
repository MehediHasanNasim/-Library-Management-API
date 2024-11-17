from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.db import transaction

from .models import User, Book, BorrowRecord, BookReturn, Fine, Submission
from .serializers import (
    UserSerializer, UserCreateSerializer,
    BookSerializer,
    BorrowRecordSerializer,
    BookReturnSerializer,
    FineSerializer,
    SubmissionSerializer
)

from .permissions import IsAdminUser, IsMemberUser



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]



class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def available(self, request):
        """List all available books."""
        books = Book.objects.filter(copies_available__gt=0)
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)



class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated, IsMemberUser]

    def perform_create(self, serializer):
        user = self.request.user
        book_id = serializer.validated_data['book'].id 
        
        # Start a database transaction to handle concurrency
        with transaction.atomic():
            # Lock the book row to prevent simultaneous modifications
            book = Book.objects.select_for_update().get(id=book_id)

            # Check if the book is available
            if book.copies_available <= 0:
                raise ValidationError(f"The book '{book.title}' is currently not available.")

            # Check if the user has reached their borrowing limit
            if BorrowRecord.objects.filter(user=user, returned=False).count() >= 5:
                raise ValidationError("You have reached your borrowing limit.")

            book.copies_available -= 1  
            book.save()  
            serializer.save(user=user) 
            
    def get_queryset(self):
        user = self.request.user
        if user.role == 'member':
            return self.queryset.filter(user=user)  
        return self.queryset




class BookReturnViewSet(viewsets.ModelViewSet):
    queryset = BookReturn.objects.all()
    serializer_class = BookReturnSerializer
    permission_classes = [IsAuthenticated, IsMemberUser]

    def perform_create(self, serializer):
        borrow_record = serializer.validated_data['borrow_record']
        
        # Check if the book has already been returned
        if borrow_record.returned:
            raise ValidationError({"error": "This book has already been returned."})
        
        # Proceed to save the book return if not already returned
        serializer.save()



class FineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Ensure members only view their fines."""
        user = self.request.user
        if user.role == 'member':
            return self.queryset.filter(borrow_record__user=user)
        return self.queryset




class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated, IsMemberUser]

    def perform_create(self, serializer):
        borrow_record = serializer.validated_data['borrow_record']
        fine = serializer.validated_data.get('fine')

        # Ensure the book has been returned before submission
        if not borrow_record.returned:
            return Response({"error": "Book must be returned before submission."}, status=status.HTTP_400_BAD_REQUEST)

        # Handle fine payment logic
        if fine and not fine.paid:
            fine.paid = True
            fine.save()

        serializer.save()

