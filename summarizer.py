import requests
from bs4 import BeautifulSoup
import os
import re
import openai
from slugify import slugify

openai.api_key = "YOUR_API_KEY_HERE"  # Replace with your actual OpenAI API key


def download_and_summarize(url):
    # Download the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the element with the main content
    main_content = soup.find("main") or soup.find("article") or soup.find("body")

    # Extract the title from the HTML
    title = soup.find("title").get_text()

    # Remove unwanted elements from main content
    for elem in main_content.select("script, style, meta, [document], head, title"):
        elem.extract()

    # slugify the title to create the folder name
    folder_name = slugify(title)

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Save the original element as an HTML file
    with open(
        os.path.join(folder_name, "original.html"), "w", encoding="utf-8"
    ) as file:
        file.write(str(main_content))

    # Generate a summary using OpenAI
    #  response = openai.Completion.create(
    #  engine="text-davinci-002",
    #  prompt=f"Summarize this web page: {url}",
    #  temperature=0.5,
    #  max_tokens=150,
    #  n=1,
    #  stop=None,
    #  timeout=15,
    #  )

    # Save the summary to a file
    #  summary = response.choices[0].text.strip()
    #  with open(os.path.join(folder_name, "summary.txt"), "w", encoding="utf-8") as file:
    #  file.write(summary)

    # Convert the HTML file to RST using pandoc
    os.system(
        f"pandoc {os.path.join(folder_name, 'original.html')} -f html -t rst -s -o {os.path.join(folder_name, 'original.rst')}"
    )

    print(f"Web page downloaded, summarized, and saved to {folder_name}.")


if __name__ == "__main__":
    url = input("Enter the URL of the web page to download and summarize: ")
    download_and_summarize(url)
