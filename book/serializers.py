from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["borrowed", "borrower", "borrowed_date"]

    def validate_id(self, value):
        if len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError("Ensure this value is digit with 6 characters.")
