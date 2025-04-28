from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    http_method_names = ("delete", "post")
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def perform_destroy(self, instance):
        if instance.borrowed:
            raise ValidationError({"msg": "Cannot delete borrowed book."})
        super().perform_destroy(instance)
