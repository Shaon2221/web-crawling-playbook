"""Unit tests for HTML parser module."""

from src.crawler.parser import BookParser


class TestBookParser:
    """Test BookParser functionality."""

    def test_parse_books_listing(self, sample_listing_html: str) -> None:
        """Test listing page parsing."""
        books = BookParser.parse_books_listing(sample_listing_html)

        assert len(books) == 2
        assert books[0]["name"] == "Book One"
        assert books[0]["rating"] == 3.0
        assert books[0]["price_incl_tax"] == 10.0
        assert "url" in books[0]

        assert books[1]["name"] == "Book Two"
        assert books[1]["rating"] == 4.0
        assert books[1]["price_incl_tax"] == 15.0

    def test_parse_books_listing_empty(self) -> None:
        """Test parsing empty listing."""
        empty_html = "<html><body></body></html>"
        books = BookParser.parse_books_listing(empty_html)

        assert len(books) == 0

    def test_parse_book_detail(self, sample_book_html: str) -> None:
        """Test detail page parsing."""
        url = "https://books.toscrape.com/catalogue/test-book/index.html"
        book = BookParser.parse_book_detail(sample_book_html, url)

        assert book is not None
        assert book["name"] == "Test Book Title"
        assert book["price_incl_tax"] == 12.0
        assert book["price_excl_tax"] == 10.0
        assert book["rating"] == 5.0
        assert book["category"] == "Fiction"
        assert book["url"] == url
        assert "content_hash" in book
        assert len(book["content_hash"]) == 64  # SHA256 hex

    def test_parse_book_detail_content_hash(self, sample_book_html: str) -> None:
        """Test content hash computation."""
        url = "https://books.toscrape.com/catalogue/test-book/index.html"
        book1 = BookParser.parse_book_detail(sample_book_html, url)

        # Parse again - should have same hash for same content
        book2 = BookParser.parse_book_detail(sample_book_html, url)

        assert book1["content_hash"] == book2["content_hash"]

    def test_parse_book_detail_invalid_html(self) -> None:
        """Test parsing invalid HTML."""
        invalid_html = "<html><body>No book data</body></html>"
        url = "https://example.com"

        book = BookParser.parse_book_detail(invalid_html, url)

        # Should return None or partial data
        assert book is None or book.get("name") == "Unknown"

    def test_parse_book_detail_malformed_price(self) -> None:
        """Test handling of malformed price data."""
        html = """
        <html>
            <body>
                <h1>Book Title</h1>
                <table class="table table-striped">
                    <tr><td>Price (incl. tax)</td><td>Invalid Price</td></tr>
                </table>
                <p class="star-rating Five">Five</p>
                <p class="instock availability">In stock</p>
                <ul class="breadcrumb"><li>Home</li><li>Fiction</li></ul>
            </body>
        </html>
        """
        url = "https://example.com"
        book = BookParser.parse_book_detail(html, url)

        assert book is not None
        # Should handle gracefully with default value
        assert book["price_incl_tax"] == 0.0
