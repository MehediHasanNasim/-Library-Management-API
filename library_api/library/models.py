from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, date

from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True)
    total_copies = models.PositiveIntegerField()
    copies_available = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_available(self):
        return self.copies_available > 0

    def borrow(self):
        if self.is_available():
            self.copies_available -= 1
            self.save()

    def return_book(self):
        self.copies_available += 1
        self.save()


    def save(self, *args, **kwargs):
        if not self.pk:  
            self.copies_available = self.total_copies
        super(Book, self).save(*args, **kwargs)  # Call the original save method




class BorrowRecord(models.Model): 
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='borrowed_books')
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_due_date = models.DateTimeField()
    returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically set the return due date if not already set
        if not self.borrow_date:  # Only set if borrow_date is None
            self.borrow_date = timezone.now()  # Explicitly set borrow_date if not already set

        if not self.return_due_date:  # If return_due_date is not set
            self.return_due_date = self.borrow_date + timedelta(days=14)
            
        super().save(*args, **kwargs)




class BookReturn(models.Model):
    borrow_record = models.OneToOneField('BorrowRecord', on_delete=models.CASCADE, related_name='book_return')
    return_date = models.DateTimeField(auto_now_add=True)
    fine_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_fine(self):
        # Make sure return_due_date is timezone-aware
        if timezone.is_naive(self.borrow_record.return_due_date):
            self.borrow_record.return_due_date = timezone.make_aware(self.borrow_record.return_due_date)

        # Compare using timezone-aware datetime
        if self.borrow_record.return_due_date < timezone.now():
            overdue_days = (timezone.now() - self.borrow_record.return_due_date).days
            return overdue_days * 5  # Assuming 5 BDT per day
        return 0.0



class Fine(models.Model):
    borrow_record = models.OneToOneField('BorrowRecord', on_delete=models.CASCADE, related_name='fine')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Submission(models.Model):
    borrow_record = models.ForeignKey('BorrowRecord', on_delete=models.CASCADE, related_name='submissions')
    fine = models.ForeignKey('Fine', on_delete=models.CASCADE, null=True, blank=True, related_name='submissions')
    submission_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
