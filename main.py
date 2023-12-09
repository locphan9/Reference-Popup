# Find link location and
from pypdf import PdfReader,PdfWriter

from pypdf import Text
from bs4 import BeautifulSoup
import requests
pdf_path = "<REPLACE_WITH_PATH_TO_PDF>"
reader = PdfReader(pdf_path)

def reference_and_link(page_num):
    page = reader.pages[page_num]
    writer = PdfWriter()
    writer.add_page(page)
    annotations = page.get('/Annots')
    link = []
    reference = []
    for annotation in annotations:
        annotation_object = annotation.get_object()
        if annotation_object['/A']['/S'] == '/URI':
            link.append(annotation_object)
        else:
            reference.append(annotation_object)
    return reference,link


def scrape_authors_from_meta_tags(url):
    # Make an HTTP request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, )

        # Find all <meta> tags with name="citation_author"
        author_meta_tags = soup.find_all('meta', {'name': 'citation_author'})

        # # Extract the content of each <meta> tag
        authors = [tag['content'] for tag in author_meta_tags]
        abstract = soup.find('meta', {'property': 'og:description'})

        return [str(authors),abstract]
    else:
        # Print an error message if the request was not successful
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return []
    
def author_dictionary(link):
    author_dict = {}
    fixed_links = [l['/A']['/URI'].replace(' ', '') for l in link[1]] # extract URI and fix spacing error
    for l in fixed_links:
        author_dict[l] = scrape_authors_from_meta_tags(l)

def reference_and_content(reference,author_dict):
    author_name = [ref['/A']['/D'].split('.')[1].split(':')[0] for ref in reference[0]]
    reference_and_content = []
    for i in range(len(author_name)):
        for l in author_dict:
            if author_name[i] in str(author_dict[l]):
                reference_and_content.append([reference[0][i],author_dict[l]])

def annotate_paper():

    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)
    annotations = page.get('/Annots')
    # Example usage
    output_pdf_path = 'new-annotated.pdf'

    for ref,content in reference_and_content:
        rect = ref['/Rect']
        annotation_text = Text(
            text=content[1],
            rect=tuple(rect),
            open=False
        )
        writer.add_annotation(page_number=0, annotation=annotation_text)


    with open(output_pdf_path, "wb") as fp:
        writer.write(fp)