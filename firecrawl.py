import os
import re
import json
from typing import Literal, Self
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
import ratelimit

PAGE = 381

load_dotenv(".env")

class DataCollector:
    anatomy_data: dict[str, dict[str, str]] = {}
    """
    This dictionary holds information of anatomy parts. It has the structure
    ```python
    {
        anatomy_part: {
            "category": category,
            "link": link,
            "description": description,
            "markdown": markdown_content
        }
    }
    ```
    """

    content_main_headings: list[tuple] = []

    def __init__(self, urls: list[str] =[], page: int = PAGE):
        self.page = PAGE
        self.firecrawl_url = "https://api.firecrawl.dev/v1/scrape"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('FIRECRAWL_TOKEN')}",
            "Content-Type": "application/json"
        }
        self.track_fails = 0

    def transform_html(self, content):
        return BeautifulSoup(str(content), "html.parser")

    @ratelimit.limits(calls=10, period=60)
    @ratelimit.sleep_and_retry
    def get_data(self):
        print("Getting data...")
        os.makedirs("./cache-requests/", exist_ok=True)
        self.urls = [
            (
                f"https://www.elsevier.com/resources/anatomy"
                + f"?query=&page={page_index}&sortBy=alphabeticalAsc"
            )
            # FIXME: Change the range to 1 - 772
            for page_index in range(self.page, 391)
        ]
        for i, url in enumerate(self.urls):
            print(self.page + i)
            payload = {
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True,
                "waitFor": 0,
                "mobile": False,
                "skipTlsVerification": False,
                "timeout": 300000000,
                "removeBase64Images": True,
                "blockAds": True,
                "proxy": "basic",
            }
            res = requests.request("POST", self.firecrawl_url, json=payload, headers=self.headers)
            # res = open("firecrawl.txt", "r").read()
            parsed_res = BeautifulSoup(res.content, "html.parser")
            print(parsed_res)
            # parsed_res = BeautifulSoup(res, "html.parser")
            parsed_res = json.loads(parsed_res.text)['data']['markdown']
            md_res = str(parsed_res).split("\n")

            line: int = 0
            is_delete: bool = True

            while line < len(md_res):
                # Delete top lines to "Search results updated [...]"
                if "Search results updated" in md_res[line]:
                    is_delete = False
                if "Related body systems" in md_res[line]:
                    is_delete = True  # Delete all bottom parts
                if is_delete:
                    del md_res[line]
                    continue
                line += 1

            if md_res == [] or is_delete is False:
                print("Failed")
                # with open("./cache-requests/failed-requests.txt", "a") as f:
                #     f.write(f"{i + 1}\n")
                if self.track_fails >= 2:
                    return
                self.page = self.page + i
                self.track_fails += 1
                self.get_data()

            del md_res[0]  # Delete the top line "Search results..."
            md_res = list(filter(lambda x: x != "" and "[" in x, md_res))

            # for i in md_res:
            #     print(i)

            log_md_link = []

            line: str = ""

            for line in md_res:
                extracted_md_link: list[tuple[str, str]] = re.findall(r"\[(.*?)\]\((.*?)\)", line)

                log_md_link.append(extracted_md_link[0])

                anatomy_part: str = extracted_md_link[0][0]
                link: str = extracted_md_link[0][1]

                self.anatomy_data[anatomy_part] = {
                    "link": link,
                }

            print("Success")
            self.track_fails = 0
            with open("./cache-requests/success-requests.txt", "a") as f:
                f.write(f"#{self.page + i}\n")
                for info in log_md_link:
                    f.write(f"{info[0]}\n{info[1]}\n")
                f.write("\n")

def main():
    # page_index = 7
    anatomy_data = DataCollector()
    anatomy_data.get_data()


if __name__ == "__main__":
    main()
