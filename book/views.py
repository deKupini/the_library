from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    http_method_names = ("delete", "get", "patch", "post")
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def perform_destroy(self, instance):
        if instance.borrowed:
            raise ValidationError({"msg": "Cannot delete borrowed book."})
        super().perform_destroy(instance)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["patch"])
    def borrow(self, request, pk):
        book = self.get_object()
        try:
            book.borrow(request.data["borrower"])
        except ValidationError:
            return Response({"msg": "Book is already borrowed."}, status=400)
        return Response({"message": "Book borrowed successfully"}, status=200)