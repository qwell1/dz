import requests
from parsel import Selector
import json

print("Загрузка...")


class BookParser:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.selectors = self.get_selectors(url)

    def get_selectors(self, url):
        response = requests.get(url, headers=self.headers)
        return Selector(response.text)

    def save_html(self, filename="book.html"):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(self.selectors.get())

    def parse(self):
        data = []
        while True:
            book_elements = self.selectors.css("li.col-xs-6.col-sm-4.col-md-3.col-lg-3")

            for position, book_element in enumerate(book_elements, start=1):
                title = book_element.css("h3 a::attr(title)").get()
                image = self.url + book_element.css(".image_container img::attr(src)").get()

                link = book_element.css(".image_container a::attr(href)").get()
                if not link.startswith("catalogue/"):
                    link = "catalogue/" + link
                link = self.url + link

                rating = book_element.css(".star-rating::attr(class)").get()[12:]
                price = book_element.css(".product_price p::text").get()[1:]
                stock = "In stock" if book_element.css(".instock::text").get() else "Out of stock"

                data.append({
                    "title": title,
                    "image": image,
                    "link": link,
                    "rating": rating,
                    "price": price,
                    "stock": stock,
                    "position": position
                })

            next_button = self.selectors.css("li.next a::attr(href)").get()

            if next_button:
                if next_button.startswith("catalogue/"):
                    next_url = self.url + next_button
                else:
                    next_url = self.url + "catalogue/" + next_button
                self.selectors = self.get_selectors(next_url)
            else:
                break

        return data

    def get_categories(self):
        categories = []

        category_elements = self.selectors.css("ul.nav-list li a")
        for category_element in category_elements:
            category_name = category_element.css("::text").get().strip()

            category_link = category_element.css("::attr(href)").get()
            if not category_link.startswith("catalogue/"):
                category_link = "catalogue/" + category_link
            category_link = self.url + category_link

            categories.append({
                "name": category_name,
                "link": category_link,
            })

        return categories


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/121.0.0.0/Safari/537.36"
    }

    url = "https://books.toscrape.com/"
    book_parser = BookParser(url, headers)

    result = book_parser.parse()
    print(json.dumps(result, indent=2, ensure_ascii=False))

    categories = book_parser.get_categories()
    print(json.dumps(categories, indent=2, ensure_ascii=False))
