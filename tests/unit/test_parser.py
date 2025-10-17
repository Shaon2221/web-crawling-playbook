"""Unit tests for book parser."""

import pytest
from src.crawler.parser import BookParser


@pytest.fixture
def sample_book_listing_html():
    """Sample book listing HTML."""
    return """
    <html>
        <body>
            <article class="product_pod">
                <h3><a href="catalogue/book_1/index.html" title="A Light in the Attic">A Light in the Attic</a></h3>
                <p class="price_color">£51.77</p>
                <p class="star-rating Three"></p>
                <p class="instock availability">In stock</p>
            </article>
            <article class="product_pod">
                <h3><a href="catalogue/book_2/index.html" title="Tipping the Velvet">Tipping the Velvet</a></h3>
                <p class="price_color">£53.74</p>
                <p class="star-rating One"></p>
                <p class="instock availability">In stock</p>
            </article>
        </body>
    </html>
    """


@pytest.fixture
def sample_book_detail_html():
    """Sample book detail HTML."""
    return """
    <html>
        <body>
            <h1>A Light in the Attic</h1>
            <p class="price_color">£51.77</p>
            <p class="star-rating Three"></p>
            <p class="instock availability">In stock (22 available)</p>
            <ul class="breadcrumb">
                <li><a href="/">Home</a></li>
                <li><a href="/books">Books</a></li>
                <li><a href="/category/poetry">Poetry</a></li>
                <li class="active">A Light in the Attic</li>
            </ul>
            <table class="table table-striped">
                <tr><th>UPC</th><td>a897fe39b1053632</td></tr>
                <tr><th>Product Type</th><td>Books</td></tr>
                <tr><th>Price (excl. tax)</th><td>£51.77</td></tr>
                <tr><th>Price (incl. tax)</th><td>£51.77</td></tr>
                <tr><th>Tax</th><td>£0.00</td></tr>
                <tr><th>Number of reviews</th><td>0</td></tr>
            </table>
            <div id="product_description"></div>
            <p>A wonderful collection of poems.</p>
        </body>
    </html>
    """


def test_parse_book_listing(sample_book_listing_html):
    """Test parsing book listing page."""
    parser = BookParser()
    books = parser.parse_book_listing(sample_book_listing_html, "https://books.toscrape.com/")

    assert len(books) == 2

    # First book
    assert books[0]["title"] == "A Light in the Attic"
    assert books[0]["price"] == 51.77
    assert books[0]["rating"] == 3

    # Second book
    assert books[1]["title"] == "Tipping the Velvet"
    assert books[1]["price"] == 53.74
    assert books[1]["rating"] == 1


def test_parse_book_detail(sample_book_detail_html):
    """Test parsing book detail page."""
    parser = BookParser()
    book = parser.parse_book_detail(
        sample_book_detail_html,
        "https://books.toscrape.com/catalogue/book_1/index.html",
        "https://books.toscrape.com/",
    )

    assert book["title"] == "A Light in the Attic"
    assert book["price"] == 51.77
    assert book["rating"] == 3
    assert book["category"] == "Poetry"
    assert book["upc"] == "a897fe39b1053632"
    assert book["product_type"] == "Books"
    assert book["num_reviews"] == 0


def test_rating_map():
    """Test rating mapping."""
    assert BookParser.RATING_MAP["One"] == 1
    assert BookParser.RATING_MAP["Two"] == 2
    assert BookParser.RATING_MAP["Three"] == 3
    assert BookParser.RATING_MAP["Four"] == 4
    assert BookParser.RATING_MAP["Five"] == 5


def test_parse_empty_html():
    """Test parsing empty HTML."""
    parser = BookParser()
    books = parser.parse_book_listing("<html></html>", "https://books.toscrape.com/")

    assert len(books) == 0
