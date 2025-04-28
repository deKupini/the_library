import datetime
import pytest

from rest_framework.test import APIClient

from book.models import Book


@pytest.fixture
def book(db):
    return Book.objects.create(
        id='123456',
        title='title',
        author='author',
    )


@pytest.fixture
def borrowed_book(db):
    return Book.objects.create(
        id="012345",
        title="title_2",
        author="author_2",
        borrowed=True,
        borrower="098765",
        borrow_date=datetime.date(2025, 4, 25),
    )


@pytest.fixture
def client():
    return APIClient()
