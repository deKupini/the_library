from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class Book(models.Model):
    id = models.CharField(primary_key=True)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    borrowed = models.BooleanField(default=False)
    borrow_date = models.DateField(null=True, default=None)
    borrower = models.CharField(null=True, default=None)

    def __str__(self):
        return self.title

    def borrow(self, borrower_number):
        if self.borrowed:
            raise ValidationError
        self.borrowed = True
        self.borrower = borrower_number
        self.borrow_date = timezone.now().date()
        self.save()

    def return_book(self):
        if not self.borrowed:
            raise ValidationError
        self.borrowed = False
        self.borrower = None
        self.borrow_date = None
        self.save()
