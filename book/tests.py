import datetime

import pytest
from freezegun import freeze_time
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from book.models import Book

BOOKS_URL = reverse("book-list")


@freeze_time("2025-04-25")
def test_borrow_book(book):
    borrower_number = "012345"
    book.borrow(borrower_number=borrower_number)

    assert book.borrowed
    assert book.borrow_date.strftime("%Y-%m-%d") == "2025-04-25"
    assert book.borrower == borrower_number


@freeze_time("2025-04-26")
def test_borrow_already_borrowed_book(borrowed_book):
    new_borrower_number = "123098"
    try:
        borrowed_book.borrow(borrower_number=new_borrower_number)
    except ValidationError:
        pass

    assert borrowed_book.borrowed
    assert borrowed_book.borrow_date.strftime('%Y-%m-%d') == "2025-04-25"
    assert borrowed_book.borrower != new_borrower_number


def test_return_book(borrowed_book):
    borrowed_book.return_book()

    assert not borrowed_book.borrowed
    assert not borrowed_book.borrow_date
    assert not borrowed_book.borrower


def test_return_already_returned_book(book):
    try:
        book.return_book()
    except ValidationError:
        pass

    assert not book.borrowed
    assert not book.borrow_date
    assert not book.borrower


def test_create_book(client, db):
    data = {
        "id": "123456",
        "title": "title",
        "author": "author",
    }
    response = client.post(BOOKS_URL, data)

    assert response.status_code == HTTP_201_CREATED
    assert response.json() == {
        "author": "author", "borrow_date": None, "borrowed": False, "borrower": None, "id": "123456", "title": "title"
    }


@pytest.mark.parametrize("field", ["id", "title", "author"])
def test_create_book_required_fields(client, db, field):
    data = {
        "id": "123456",
        "title": "title",
        "author": "author",
    }
    del data[field]
    response = client.post(BOOKS_URL, data)

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {f"{field}": ["This field is required."]}
    assert not Book.objects.exists()


def test_create_book_with_duplicated_id(book, client, db):
    data = {
        "id": book.id,
        "title": "title",
        "author": "author",
    }
    response = client.post(BOOKS_URL, data)

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {"id": ["book with this id already exists."]}
    assert len(Book.objects.all()) == 1
