import os
import re
from typing import Literal, Self

import requests
from bs4 import BeautifulSoup
import ratelimit


PAGE = 13

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

    def __init__(self, urls: list[str]):
        self.urls = urls
        self.headers = {
            'Authorization': 'Bearer jina_f1b8ba95da4f4590a25b7f6449672aa4UUiylztDt5YqvhRb5UN6QeVLHbDx'
        }

    def transform_html(self, content):
        return BeautifulSoup(str(content), "html.parser")

    @ratelimit.limits(calls=20, period=60)
    @ratelimit.sleep_and_retry
    def get_data(self) -> Self:
        print("Getting data...")
        os.makedirs("./cache-requests/", exist_ok=True)
        for i, url in enumerate(self.urls):
            print(i + 6)
            res = requests.request("POST", url, headers=self.headers, timeout=1000)
            parsed_res = BeautifulSoup(res.content, "html.parser")
            md_res: list[str] = str(parsed_res).split("\n")
            filtered_res: list[str] = list(
                filter(lambda x: "------" not in x and x != "", md_res)
            )

            line: int = 0
            is_delete: bool = True

            while line < len(filtered_res):
                # Delete top lines to "Search results updated [...]"
                if "Search results updated" in filtered_res[line]:
                    is_delete = False
                if filtered_res[line] == "1" and filtered_res[line + 1] == "2":
                    is_delete = True  # Delete all bottom parts
                if is_delete:
                    del filtered_res[line]
                    continue
                line += 1

            if filtered_res == [] or is_delete is False:
                print("Failed")
                # with open("./cache-requests/failed-requests.txt", "a") as f:
                #     f.write(f"{i + 1}\n")
                continue

            del filtered_res[0]  # Delete the top line "Search results..."

            # for i in filtered_res:
            #     print(i)

            line = 0

            log_md_link = []

            while line < len(filtered_res):
                extracted_md_link: list[tuple[str, str]] = re.findall(
                    r"\[(.*?)\]\((.*?)\)", filtered_res[line + 1]
                )

                log_md_link.append(extracted_md_link[0])

                category: str = filtered_res[line]
                anatomy_part: str = extracted_md_link[0][0]
                link: str = extracted_md_link[0][1]
                description: str = filtered_res[line + 2]

                self.anatomy_data[anatomy_part] = {
                    "category": category,
                    "link": link,
                    "description": description,
                }
                line += 3

            print("Success")
            with open("./cache-requests/success-requests.txt", "a") as f:
                f.write(f"#{i + 6}\n")
                for info in log_md_link:
                    f.write(f"{info[0]}\n{info[1]}\n")
                f.write("\n")

        return self

    def process_data(self):
        """
        Process data.
        Transform data into Markdown, dict, etc.
        """
        print("Processing data...")
        # Traverse the dictionary
        for anatomy_part, metadata in self.anatomy_data.items():
            link = metadata["link"]

            res = requests.get(link, timeout=1000)
            parsed_res = BeautifulSoup(res.content, "html.parser")

            markdown_file = f"# {anatomy_part}\n\ncategory: {
                metadata['category']}\n\ndescription: {metadata['description']}\n"

            def add_to_markdown(content: str, heading_level: int = 0):
                nonlocal markdown_file
                if heading_level == 0:
                    markdown_file += f"\n{content}\n"
                    return
                markdown_file += f"\n{heading_level * '#'} {content}\n"

            content_signature = parsed_res.find("div", id="article-content")
            assert (
                content_signature is not None
            ), "Could not find the specified element."
            content_parent = content_signature.parent
            assert content_parent is not None, "Could not find the specified element."

            content_structure = content_parent.find("nav")
            if content_structure is None:
                content_structure = self.transform_html(content_structure)
                content_structure = content_parent.find("div", id=False)
                content_structure = self.transform_html(content_structure)
                content_structure = content_structure.find_all(
                    lambda tag: tag.name == "div" and tag.has_attr("id")
                )[0]
                content_structure = self.transform_html(content_structure)
                content_structure = content_structure.find("div")
                assert content_structure is not None
                id = content_structure.get("id")
                name = content_structure.find("h2", {"data-heading-level": "2"})
                assert name is not None
                name = name.text
                self.content_main_headings.append((name, id))
            else:
                content_structure = self.transform_html(content_structure)
                content_structure = content_structure.find_all(
                    "span", {"data-heading-level": "5"}
                )

                for heading in content_structure:
                    heading_text = heading.text
                    heading_href = (
                        heading.parent["href"] if heading.parent is not None else None
                    )
                    assert heading_href is not None
                    heading_href = heading_href[1:]

                    self.content_main_headings.append((heading_text, heading_href))

            # print(f"{anatomy_part} >>> {self.content_main_headings}\n")
            for heading in self.content_main_headings:
                _, id = heading
                add_to_markdown(content=_, heading_level=2)
                content_section = content_parent.find_all("div", {"id": id})
                content_section = self.transform_html(content_section)
                content_section = content_section.find(
                    "h2", {"data-heading-level": "2"}
                )
                assert content_section is not None, content_section
                content_section = content_section.parent
                content_section = self.transform_html(content_section)
                content_section = content_section.find_all("p")
                for paragraph in content_section:
                    add_to_markdown(content=paragraph.text, heading_level=0)

            self.anatomy_data[anatomy_part]["markdown"] = markdown_file
            self.content_main_headings = []

        return self

    def save_data(self, flag: Literal["File", "Variable"] = "File"):
        """
        Save data:
        - If flag is "File" -> Save markdown data to a file and return an object
          that points to the file location.
        - If flag is "Variable" -> Save all data to a variable which includes
          category, link, description, and markdown data.
        """
        if flag == "Variable":
            return self.anatomy_data
        elif flag == "File":
            confirmation = input("Save data to file? (y/n): ")
            if confirmation.lower() == "n":
                return
            os.makedirs("./data", exist_ok=True)
            for anatomy_part, metadata in self.anatomy_data.items():
                with open(f"./data/{anatomy_part}.md", "w") as f:
                    f.write(metadata["markdown"])
            return


def main():
    Jina_AI = "r.jina.ai"
    URLs = [
        (
            f"https://{Jina_AI}/www.elsevier.com/resources/anatomy"
            + f"?query=&page={page_index}&sortBy=alphabeticalAsc"
        )
        # FIXME: Change the range to 1 - 772
        for page_index in range(6, 772)
    ]

    anatomy_data = DataCollector(URLs)
    # data pipeline
    (anatomy_data.get_data())
        #.process_data().save_data("File"))


if __name__ == "__main__":
    main()
