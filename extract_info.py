import wikipedia

def extract_country_info(country_name):
    # Specify the title of the page
    wiki = wikipedia.page(country_name)
    # Extract the plain text content of the page, just text
    text = wiki.context
    text = text.replace("==", "")
    text = text.replace("\n", "")
    print(text)



