import datetime

import pytest
from freezegun import freeze_time
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, \
    HTTP_200_OK

from book.models import Book

BOOKS_URL = reverse("book-list")
BOOK_DETAIL_URL = "book-detail"


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


def test_delete_book(book, client, db):
    url = reverse(BOOK_DETAIL_URL, kwargs={"pk": book.id})
    response = client.delete(url)

    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Book.objects.exists()


def test_delete_not_existing_book(client, db):
    url = reverse(BOOK_DETAIL_URL, kwargs={"pk": "123456"})
    response = client.delete(url)

    assert response.status_code == HTTP_404_NOT_FOUND
    assert not Book.objects.exists()


def test_delete_borrowed_book(borrowed_book, client, db):
    url = reverse(BOOK_DETAIL_URL, kwargs={"pk": borrowed_book.id})
    response = client.delete(url)

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {"msg": "Cannot delete borrowed book."}
    assert Book.objects.exists()


def test_get_list_of_single_book(book, client):
    response = client.get(BOOKS_URL)

    assert response.status_code == HTTP_200_OK
    assert response.json() == [
        {"id": "123456", "title": "title", "author": "author", "borrowed": False, "borrow_date": None, "borrower": None}
    ]


def test_get_list_of_two_books(book, borrowed_book, client):
    response = client.get(BOOKS_URL)

    assert response.status_code == HTTP_200_OK
    assert response.json() == [
        {
            "id": "123456",
            "title": "title",
            "author": "author",
            "borrowed": False,
            "borrow_date": None,
            "borrower": None
        },
        {
            "id": "012345",
            "title": "title_2",
            "author": "author_2",
            "borrowed": True,
            "borrow_date": "2025-04-25",
            "borrower": "098765"
        }
    ]


def test_get_list_of_empty_list(client, db):
    response = client.get(BOOKS_URL)

    assert response.status_code == HTTP_200_OK
    assert response.json() == []


def test_get_single_book(book, client):
    url = reverse(BOOK_DETAIL_URL, kwargs={"pk": book.id})
    response = client.get(url)

    assert response.status_code == HTTP_404_NOT_FOUND