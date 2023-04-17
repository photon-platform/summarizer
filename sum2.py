import json
import os
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from slugify import slugify
import html2text
import markdown
from collections import Counter
import re


def generate_outline(soup):
    """Generates an outline (table of contents) from the headings in a BeautifulSoup object."""
    outline = []

    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        level = int(heading.name[1])
        title = heading.text.strip()
        item = {"level": level, "title": title}

        outline.append(item)

    return outline


def extract_keywords(soup):
    """Extracts likely keywords from a BeautifulSoup object and returns the top `count` keywords as a list."""
    # Extract text content from soup object
    text = " ".join(soup.stripped_strings)

    # Split text into words
    words = re.findall(r"\b\w+\b", text.lower())

    # Filter out stop words and common words
    common_words = [
        "the",
        "of",
        "and",
        "in",
        "to",
        "a",
        "that",
        "is",
        "for",
        "on",
        "with",
        "by",
        "at",
    ]
    words = [word for word in words if word not in common_words]

    #  with open('stopwords.txt', 'r') as file:
    #  stopwords = [line.strip() for line in file]
    #  words = [word for word in words if word not in stopwords]

    # Count occurrences of each word and return top `count` words
    word_counts = Counter(words)
    #  top_words = [word for word, count in word_counts.most_common(count)]

    return word_counts


def download_web_page(url):
    """Downloads a web page and returns its HTML content."""
    response = requests.get(url)
    return response.text


def parse_web_page(html_content):
    """Parses a web page using BeautifulSoup and returns the BeautifulSoup object without certain elements."""
    soup = BeautifulSoup(html_content, "html.parser")

    removals = [
        "nav",
        "form",
        "input",
        "style",
        "script",
    ]

    # Remove navigation elements
    for element in removals:
        for node in soup.find_all(element):
            node.extract()

    # Remove any other elements that are not content-related
    for element in soup.descendants:
        if isinstance(element, Comment):
            element.extract()
        #  elif element.name in ['script', 'style']:
        #  element.extract()
        elif element.name == "a":
            if element.find("img"):
                continue
            if element.has_attr("href") and element["href"].startswith("#"):
                continue
            element.unwrap()

    return soup


def find_main_content(soup):
    """Identifies the HTML element that most likely contains the main content and returns it."""
    # Search for common main content tags and IDs
    possible_tags = ["main", "article"]
    possible_ids = ["main", "content"]

    # Look for the first tag or ID that appears in the HTML
    for tag in possible_tags:
        result = soup.find(tag)
        if result is not None:
            return result

    for id in possible_ids:
        result = soup.find(id=id)
        if result is not None:
            return result

    # If no main content element is found, return None
    return None


def create_folder(title):
    """Creates a folder with a slugified version of the title."""
    folder_name = slugify(title)
    os.makedirs(folder_name, exist_ok=True)
    return folder_name


def save_html_file(soup, folder_name):
    """Saves the original web page HTML as a file in the specified folder."""
    file_name = os.path.join(folder_name, "original.html")
    with open(file_name, "w") as file:
        file.write(str(soup))


def convert_to_md(soup, folder_name, name):
    """Converts the main content of the web page to markdown and saves it in a file in the specified folder."""
    if soup is None:
        return

    md_content = html2text.html2text(str(soup))
    file_name = os.path.join(folder_name, f"{name}.md")
    with open(file_name, "w") as file:
        file.write(md_content)


def save_links(soup, folder_name, name):
    """Returns a list of all links (href attributes) found in the BeautifulSoup object."""
    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href is not None:
            links.append(link)

    convert_to_md(links, folder_name, "links")


def main(url):
    """TODO: Docstring for main.
    :returns: TODO

    """
    # Download and parse the web page
    html_content = download_web_page(url)
    soup = parse_web_page(html_content)

    # Find the main content element and create a folder
    main_content = find_main_content(soup)
    folder_name = create_folder(soup.title.string)

    # Save the HTML, plain text, and Markdown versions of the content
    save_html_file(main_content, folder_name)
    convert_to_md(main_content, folder_name, "main")
    save_links(main_content, folder_name, "main")

    keywords = extract_keywords(main_content)
    file_name = os.path.join(folder_name, f"keywords.json")
    with open(file_name, "w") as file:
        #  file.write(str(keywords))
        json.dump(keywords, file, indent=4)

    outline = generate_outline(main_content)
    file_name = os.path.join(folder_name, f"outline.json")
    with open(file_name, "w") as file:
        json.dump(outline, file, indent=4)


if __name__ == "__main__":
    main("https://en.wikipedia.org/wiki/Golden_ratio")
