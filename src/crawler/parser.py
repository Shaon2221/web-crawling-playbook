"""HTML parser for extracting book data from books.toscrape.com."""

import hashlib
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from src.logger import crawler_logger


class BookParser:
    """Parse HTML and extract book data."""

    @staticmethod
    def parse_books_listing(html: str) -> List[Dict[str, Any]]:
        """
        Extract book metadata from listing page.

        Args:
            html: HTML content of listing page

        Returns:
            List of book metadata dictionaries
        """
        soup = BeautifulSoup(html, "lxml")
        books = []

        try:
            for article in soup.find_all("article", class_="product_pod"):
                try:
                    # Extract book URL
                    link = article.h3.a
                    if not link or not link.get("href"):
                        crawler_logger.warning("Missing book link in article")
                        continue

                    book_url = link["href"]
                    # Convert relative to absolute URL
                    if not book_url.startswith("http"):
                        book_url = "https://books.toscrape.com/catalogue/" + book_url.lstrip("../")

                    # Extract title
                    title = link.get("title", "Unknown")

                    # Extract rating
                    rating_p = article.find("p", class_="star-rating")
                    rating_class = rating_p.get("class", [])[1] if rating_p else "Unknown"
                    rating_map = {
                        "One": 1.0,
                        "Two": 2.0,
                        "Three": 3.0,
                        "Four": 4.0,
                        "Five": 5.0,
                    }
                    rating = rating_map.get(rating_class, 0.0)

                    # Extract price
                    price_p = article.find("p", class_="price_color")
                    price_text = price_p.text.strip() if price_p else "£0.00"
                    price_match = re.search(r"£([\d.]+)", price_text)
                    price = float(price_match.group(1)) if price_match else 0.0

                    # Extract availability
                    avail_p = article.find("p", class_="instock availability")
                    availability = avail_p.text.strip() if avail_p else "Unknown"

                    books.append(
                        {
                            "url": book_url,
                            "name": title,
                            "rating": rating,
                            "price_incl_tax": price,
                            "availability": availability,
                        }
                    )

                except Exception as e:
                    crawler_logger.error(f"Error parsing book article: {e}")
                    continue

        except Exception as e:
            crawler_logger.error(f"Error parsing books listing: {e}")

        return books

    @staticmethod
    def parse_book_detail(html: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract detailed book information from product page.

        Args:
            html: HTML content of book detail page
            url: URL of the page

        Returns:
            Dictionary with book details or None if parsing fails
        """
        soup = BeautifulSoup(html, "lxml")

        try:
            # Extract title
            title_h1 = soup.find("h1")
            name = title_h1.text.strip() if title_h1 else "Unknown"

            # Extract prices from table
            table = soup.find("table", class_="table table-striped")
            price_incl_tax = 0.0
            price_excl_tax = 0.0

            if table:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) == 2:
                        label = cells[0].text.strip()
                        value = cells[1].text.strip()

                        if "Price (excl. tax)" in label:
                            match = re.search(r"£([\d.]+)", value)
                            price_excl_tax = float(match.group(1)) if match else 0.0
                        elif "Price (incl. tax)" in label:
                            match = re.search(r"£([\d.]+)", value)
                            price_incl_tax = float(match.group(1)) if match else 0.0

            # Extract rating
            rating_p = soup.find("p", class_="star-rating")
            rating_class = rating_p.get("class", [])[1] if rating_p else "Unknown"
            rating_map = {
                "One": 1.0,
                "Two": 2.0,
                "Three": 3.0,
                "Four": 4.0,
                "Five": 5.0,
            }
            rating = rating_map.get(rating_class, 0.0)

            # Extract availability
            avail_p = soup.find("p", class_="instock availability")
            availability = avail_p.text.strip() if avail_p else "Unknown"

            # Extract description (from meta tag)
            desc_meta = soup.find("meta", attrs={"name": "description"})
            description = desc_meta.get("content", "") if desc_meta else None

            # Extract number of reviews
            num_reviews = 0
            review_rows = soup.find_all("p")
            for p in review_rows:
                if "based on" in p.text.lower():
                    match = re.search(r"(\d+)", p.text)
                    num_reviews = int(match.group(1)) if match else 0
                    break

            # Extract image URL
            image_img = soup.find("img")
            image_url = None
            if image_img and image_img.get("src"):
                img_src = image_img["src"]
                if not img_src.startswith("http"):
                    image_url = "https://books.toscrape.com/" + img_src
                else:
                    image_url = img_src

            # Extract category from breadcrumb
            category = "Unknown"
            breadcrumb = soup.find("ul", class_="breadcrumb")
            if breadcrumb:
                items = breadcrumb.find_all("li")
                if len(items) >= 3:
                    category = items[-2].text.strip()

            # Compute content hash for change detection
            content = f"{name}|{price_incl_tax}|{availability}|{rating}"
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            return {
                "url": url,
                "name": name,
                "description": description,
                "category": category,
                "price_incl_tax": price_incl_tax,
                "price_excl_tax": price_excl_tax,
                "availability": availability,
                "num_reviews": num_reviews,
                "rating": rating,
                "image_url": image_url,
                "raw_html": html,
                "content_hash": content_hash,
            }

        except Exception as e:
            crawler_logger.error(f"Error parsing book detail for {url}: {e}", exc_info=True)
            return None
