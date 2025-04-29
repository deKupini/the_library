from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_200_OK

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

    @staticmethod
    def _validate_borrower(borrower):
        if len(borrower) != 6 or not borrower.isdigit():
            raise ValidationError({"borrower": "Ensure this value is digit with 6 characters."})

    @action(detail=True, methods=["patch"])
    def borrow(self, request, pk):
        book = self.get_object()
        borrower = request.data.get("borrower")
        if not borrower:
            return Response({"msg": "Borrower is required."}, status=HTTP_400_BAD_REQUEST)
        self._validate_borrower(borrower)

        try:
            book.borrow(request.data["borrower"])
        except ValidationError:
            return Response({"msg": "Book is already borrowed."}, status=HTTP_400_BAD_REQUEST)

        return Response({"msg": "Book borrowed successfully"}, status=HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="return", url_name="return")
    def return_(self, request, pk):
        book = self.get_object()
        try:
            book.return_book()
        except ValidationError:
            return Response({"msg": "Book is already returned."}, status=HTTP_400_BAD_REQUEST)

        return Response({"msg": "Book returned successfully"}, status=HTTP_200_OK)