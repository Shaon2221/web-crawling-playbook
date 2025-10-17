"""HTML parser for extracting book data."""

from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from src.utils import logger


class BookParser:
    """Parser for extracting book information from HTML."""

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    @staticmethod
    def parse_book_listing(html: str, base_url: str) -> list[Dict[str, Any]]:
        """
        Parse book listing page to extract book URLs and basic info.

        Args:
            html: HTML content of listing page
            base_url: Base URL for resolving relative links

        Returns:
            List of book info dictionaries
        """
        soup = BeautifulSoup(html, "html.parser")
        books = []

        for article in soup.find_all("article", class_="product_pod"):
            try:
                # Get book URL
                h3 = article.find("h3")
                if not h3:
                    continue

                link = h3.find("a")
                if not link or not link.get("href"):
                    continue

                book_url = urljoin(base_url, link["href"])

                # Get title
                title = link.get("title", "")

                # Get price
                price_elem = article.find("p", class_="price_color")
                price_text = price_elem.text.strip() if price_elem else "£0.00"
                price = float(price_text.replace("£", "").strip())

                # Get rating
                rating_elem = article.find("p", class_="star-rating")
                rating_class = rating_elem.get("class", []) if rating_elem else []
                rating = 0
                for cls in rating_class:
                    if cls in BookParser.RATING_MAP:
                        rating = BookParser.RATING_MAP[cls]
                        break

                # Get availability
                availability_elem = article.find("p", class_="instock availability")
                availability = (
                    availability_elem.text.strip() if availability_elem else "Unknown"
                )

                books.append(
                    {
                        "url": book_url,
                        "title": title,
                        "price": price,
                        "rating": rating,
                        "availability": availability,
                    }
                )

            except Exception as e:
                logger.warning(f"Error parsing book listing item: {e}")
                continue

        return books

    @staticmethod
    def parse_book_detail(html: str, book_url: str, base_url: str) -> Dict[str, Any]:
        """
        Parse book detail page to extract complete book information.

        Args:
            html: HTML content of detail page
            book_url: URL of the book detail page
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary with book details
        """
        soup = BeautifulSoup(html, "html.parser")
        book_data: Dict[str, Any] = {"url": book_url}

        try:
            # Get title
            h1 = soup.find("h1")
            book_data["title"] = h1.text.strip() if h1 else "Unknown"

            # Get price
            price_elem = soup.find("p", class_="price_color")
            if price_elem:
                price_text = price_elem.text.strip().replace("£", "")
                book_data["price"] = float(price_text)
            else:
                book_data["price"] = 0.0

            # Get rating
            rating_elem = soup.find("p", class_="star-rating")
            rating_class = rating_elem.get("class", []) if rating_elem else []
            book_data["rating"] = 0
            for cls in rating_class:
                if cls in BookParser.RATING_MAP:
                    book_data["rating"] = BookParser.RATING_MAP[cls]
                    break

            # Get availability
            availability_elem = soup.find("p", class_="instock availability")
            book_data["availability"] = (
                availability_elem.text.strip() if availability_elem else "Unknown"
            )

            # Get category (breadcrumb)
            breadcrumb = soup.find("ul", class_="breadcrumb")
            if breadcrumb:
                category_link = breadcrumb.find_all("a")
                if len(category_link) >= 3:
                    book_data["category"] = category_link[2].text.strip()
                else:
                    book_data["category"] = "Unknown"
            else:
                book_data["category"] = "Unknown"

            # Get product information table
            product_table = soup.find("table", class_="table table-striped")
            if product_table:
                rows = product_table.find_all("tr")
                for row in rows:
                    th = row.find("th")
                    td = row.find("td")
                    if th and td:
                        key = th.text.strip()
                        value = td.text.strip()

                        if key == "UPC":
                            book_data["upc"] = value
                        elif key == "Product Type":
                            book_data["product_type"] = value
                        elif key == "Price (excl. tax)":
                            book_data["price_excl_tax"] = float(
                                value.replace("£", "").strip()
                            )
                        elif key == "Price (incl. tax)":
                            book_data["price_incl_tax"] = float(
                                value.replace("£", "").strip()
                            )
                        elif key == "Tax":
                            book_data["tax"] = float(value.replace("£", "").strip())
                        elif key == "Number of reviews":
                            book_data["num_reviews"] = int(value)

            # Get description
            description_elem = soup.find("div", id="product_description")
            if description_elem:
                desc_p = description_elem.find_next("p")
                book_data["description"] = desc_p.text.strip() if desc_p else None
            else:
                book_data["description"] = None

            # Get image URL
            image_elem = soup.find("div", class_="item active")
            if image_elem:
                img = image_elem.find("img")
                if img and img.get("src"):
                    book_data["image_url"] = urljoin(base_url, img["src"])
            else:
                book_data["image_url"] = None

        except Exception as e:
            logger.error(f"Error parsing book detail for {book_url}: {e}")

        return book_data

    @staticmethod
    def get_next_page_url(html: str, current_url: str) -> Optional[str]:
        """
        Extract next page URL from listing page.

        Args:
            html: HTML content
            current_url: Current page URL

        Returns:
            Next page URL or None
        """
        soup = BeautifulSoup(html, "html.parser")
        next_link = soup.find("li", class_="next")

        if next_link:
            a_tag = next_link.find("a")
            if a_tag and a_tag.get("href"):
                return urljoin(current_url, a_tag["href"])

        return None

    @staticmethod
    def get_category_urls(html: str, base_url: str) -> list[Dict[str, str]]:
        """
        Extract category URLs from the homepage.

        Args:
            html: HTML content
            base_url: Base URL

        Returns:
            List of category info dictionaries
        """
        soup = BeautifulSoup(html, "html.parser")
        categories = []

        # Find category navigation
        category_nav = soup.find("ul", class_="nav nav-list")
        if category_nav:
            category_list = category_nav.find("ul")
            if category_list:
                for li in category_list.find_all("li"):
                    a_tag = li.find("a")
                    if a_tag and a_tag.get("href"):
                        category_name = a_tag.text.strip()
                        category_url = urljoin(base_url, a_tag["href"])
                        categories.append(
                            {"name": category_name, "url": category_url}
                        )

        return categories
