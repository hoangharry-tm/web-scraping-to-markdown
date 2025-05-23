import os
from pathlib import Path

from bs4 import BeautifulSoup
import requests

anatomy_data: dict[str, list[str]] = {}

os.makedirs("./data", exist_ok=True)

folder_path = Path("./").parent.joinpath("data")
file_names = os.listdir(folder_path)

for i, file_name in enumerate(file_names):
    file_names[i] = file_name.split(".md")[0]

print(len(file_names))

"""
def transform_html(content):
    return BeautifulSoup(str(content), "html.parser")

def process_data(from_page: int = 0):
    markdown_file = ""
    def add_to_markdown(content: str, heading_level: int = 0):
        nonlocal markdown_file
        if heading_level == 0:
            markdown_file += f"\n{content}\n"
            return
        markdown_file += f"\n{heading_level * '#'} {content}\n"

    def find_duplicates(lst):
        count_dict = {}
        duplicates = []

        for item in lst:
            if item in count_dict:
                count_dict[item] += 1
            else:
                count_dict[item] = 1

        for item, count in count_dict.items():
            if count > 1:
                duplicates.append(item)

        return duplicates

    print("Processing data...")

    path = Path("./").parent.joinpath("cache-requests/success-requests.txt")

    cache_requests = (open(path, "r")
                        .read()
                        .split("\n")
                        )
    cache_requests = list(filter(lambda x: x != "" and "#" not in x, cache_requests))

    test = cache_requests
    test = list(filter(lambda x: "http" not in x, test))
    dup = find_duplicates(test)
    # print(dup)
    # print(len(dup))

    link = ""
    anatomy_part = ""
    for _, item in enumerate(cache_requests):
        if "http" in item:
            link = item
        else:
            anatomy_part = item

        if link != "" and anatomy_part != "" and anatomy_part in dup:
            if anatomy_part not in anatomy_data:
                anatomy_data[anatomy_part] = []
            anatomy_data[anatomy_part].append(link)
            link = ""
            anatomy_part = ""

    for anatomy_part, links in anatomy_data.items():
        print(f"{anatomy_part}\nProcessing...")
        links.pop()

        for count, link in enumerate(links):

            markdown_file = f"# {anatomy_part}\n\n"

            res = requests.get(link, timeout=1000)
            parsed_res = BeautifulSoup(res.content, "html.parser")


            content_signature = parsed_res.find("div", id="article-content")
            assert (
                content_signature is not None
            ), "Could not find the specified element."
            content_parent = content_signature.parent
            assert content_parent is not None, "Could not find the specified element."

            content_structure = content_parent.find("nav")
            content_main_headings = []
            if content_structure is None:
                content_structure = transform_html(content_structure)
                content_structure = content_parent.find("div", id=False)
                content_structure = transform_html(content_structure)
                content_structure = content_structure.find_all(
                    lambda tag: tag.name == "div" and tag.has_attr("id")
                )[0]
                content_structure = transform_html(content_structure)
                content_structure = content_structure.find("div")
                assert content_structure is not None
                id = content_structure.get("id") # type: ignore
                name = content_structure.find("h2", {"data-heading-level": "2"}) # type: ignore
                assert name is not None
                name = name.text
                content_main_headings.append((name, id))
            else:
                content_structure = transform_html(content_structure)
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

                    content_main_headings.append((heading_text, heading_href))

            # print(f"{anatomy_part} >>> {content_main_headings}\n")
            for heading in content_main_headings:
                _, id = heading
                add_to_markdown(content=_, heading_level=2)
                content_section = content_parent.find_all("div", {"id": id})
                content_section = transform_html(content_section)
                content_section = content_section.find(
                    "h2", {"data-heading-level": "2"}
                )
                assert content_section is not None, content_section
                content_section = content_section.parent
                content_section = transform_html(content_section)
                content_section = content_section.find_all("p")
                for paragraph in content_section:
                    add_to_markdown(content=paragraph.text, heading_level=0)

            with open(f"./data/{anatomy_part} {count + 1}.md", "w") as f:
                f.write(markdown_file)
                print("Done.")
            content_main_headings = []
"""

if __name__ == "__main__":
    pass
    # process_data()
