from rest_framework import serializers
from .models import User, Book, BorrowRecord, BookReturn, Fine, Submission


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'created_at', 'updated_at']
        read_only_fields = ['role', 'created_at', 'updated_at']

class UserCreateSerializer(serializers.ModelSerializer):
    role = serializers.CharField()

    """For user registration"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user



class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'total_copies', 'copies_available', 'created_at', 'updated_at']
        read_only_fields = ['copies_available', 'created_at', 'updated_at']

    def validate_total_copies(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total copies must be greater than zero.")
        return value


class BorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRecord
        fields = ['id', 'book', 'borrow_date', 'return_due_date', 'returned', 'created_at', 'updated_at']  
        read_only_fields = ['borrow_date', 'return_due_date', 'returned', 'created_at', 'updated_at']

    def validate(self, data):
        request = self.context.get('request')  
        user = request.user  # Use the authenticated user
        book = data['book']

        if BorrowRecord.objects.filter(user=user, returned=False).count() >= 5:
            raise serializers.ValidationError("You have reached your borrowing limit.")

        # Check if the book is available
        if not book.is_available():
            raise serializers.ValidationError(f"The book '{book.title}' is currently not available.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')  
        user = request.user  # Use the authenticated user
        validated_data['user'] = user  # Assign the user to validated_data

        book = validated_data['book']
        book.borrow()  # Reduce available copies
        return super().create(validated_data)



class BookReturnSerializer(serializers.ModelSerializer):
    fine = serializers.SerializerMethodField()

    class Meta:
        model = BookReturn
        fields = ['id', 'borrow_record', 'return_date', 'fine_paid', 'fine', 'created_at', 'updated_at']
        read_only_fields = ['return_date', 'fine', 'created_at', 'updated_at']

    def get_fine(self, obj):
        return obj.calculate_fine()

    def create(self, validated_data):
        book_return = super().create(validated_data)
        borrow_record = book_return.borrow_record
        borrow_record.returned = True
        borrow_record.book.return_book()  # Increase available copies
        borrow_record.save()
        return book_return



class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fine
        fields = ['id', 'borrow_record', 'fine_amount', 'paid', 'created_at', 'updated_at']
        read_only_fields = ['fine_amount', 'created_at', 'updated_at']



class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'borrow_record', 'fine', 'submission_date', 'amount_paid', 'created_at', 'updated_at']
        read_only_fields = ['submission_date', 'created_at', 'updated_at']




















# from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
# from rest_framework import serializers
# from .models import User, Book, BorrowRecord


# class UserCreateSerializer(BaseUserCreateSerializer): 
#     role = serializers.CharField()
#     class Meta(BaseUserCreateSerializer.Meta):
#         fields = ['id', 'username', 'email', 'password', 'role']


# class BookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Book
#         fields = ['id', 'title', 'author', 'is_available']

# class BorrowRecordSerializer(serializers.ModelSerializer):
#     fine = serializers.SerializerMethodField()  # Include fine in the response

#     class Meta:
#         model = BorrowRecord
#         fields = ['id', 'user', 'book', 'borrow_date', 'return_deadline', 'return_date', 'fine']

#     def get_fine(self, obj):
#         return obj.calculate_fine()



# # from rest_framework import serializers
# # from .models import Book, Member, Borrow

# # class BookSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Book
# #         fields = ['id', 'title', 'author', 'available', 'created_at', 'updated_at']


# # class MemberSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Member
# #         fields = ['id', 'user', 'max_borrow_limit']


# # class BorrowSerializer(serializers.ModelSerializer):
# #     fine = serializers.SerializerMethodField()

# #     class Meta:
# #         model = Borrow
# #         fields = ['id', 'member', 'book', 'borrowed_at', 'due_date', 'returned_at', 'fine']

# #     def get_fine(self, obj):
# #         return obj.overdue_fine()
