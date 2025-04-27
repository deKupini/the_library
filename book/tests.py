from freezegun import freeze_time
from rest_framework.exceptions import ValidationError


@freeze_time("2025-04-25")
def test_borrow_book(book):
    borrower_number = "012345"
    book.borrow(borrower_number=borrower_number)

    assert book.borrowed
    assert book.borrow_date.strftime('%Y-%m-%d') == '2025-04-25'
    assert book.borrower == borrower_number


@freeze_time("2025-04-26")
def test_borrow_borrowed_book(borrowed_book):
    new_borrower_number = "123098"
    try:
        borrowed_book.borrow(borrower_number=new_borrower_number)
    except ValidationError:
        pass

    assert borrowed_book.borrowed
    assert borrowed_book.borrow_date.strftime('%Y-%m-%d') == "2025-04-25"
    assert borrowed_book.borrower != new_borrower_number
