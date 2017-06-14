import xlwt
import requests
from bs4 import BeautifulSoup

# Initialize Excel workbook
book = xlwt.Workbook(encoding="utf-8")

components_url = "https://developer.mbed.org/components"
base_url = "https://developer.mbed.org"
components_page = requests.get(components_url)
soup = BeautifulSoup(components_page.content, 'html.parser')


# Filters that gather HTML elements based on class name
def component_filter(tag):
    return (tag.name == 'a' and
        tag.parent.name == 'div' and
        'component-list-item' in tag.parent['class'])


def item_filter(tag):
    return (tag.name == 'a' and
        tag.parent.name == 'h4' and
        'ftitle' in tag.parent['class'])


def hello_world_filter(tag):
    return (tag.name == 'a' and
        tag.parent.name == 'td') # and 'styledtable' in tag.parent['class']

# Save the main Component URLs
remove = "/components/cat/"
component_links = [link.get('href') for link in soup(component_filter)]
main_components = [url[len(remove):-1].title().replace('-', ' ') for url in component_links]

worksheet = book.add_sheet("Components")
worksheet.write(0, 0, "Component Type")
worksheet.write(0, 1, "Component URL")
worksheet.write(0, 2, "Hello World URL")
worksheet.write(0, 3, "Contains mbed.bld?")

print "Begin component crawling..."
# Add main Component URLs to Excel Sheet
i = 1
for component in component_links:
    temp_name = component[len(remove):-1].title().replace('-', ' ')
    temp_url = base_url + component
    temp_page = requests.get(temp_url)
    temp_soup = BeautifulSoup(temp_page.content, 'html.parser')
    temp_links = [link.get('href') for link in temp_soup(component_filter)]

    for item in temp_links:
        # Find first instance of a program URL
        worksheet.write(i, 0, temp_name)
        worksheet.write(i, 1, item)
        item_url = base_url + item
        item_page = requests.get(item_url)
        item_soup = BeautifulSoup(item_page.content, 'html.parser')
        hello_world = ""
        try:
            item_table = [link.get('href') for link in item_soup.find_all(item_filter)]
            for link in item_soup(item_filter):
                this_link = link.get('href')
                if "https" not in this_link:
                    hello_world = this_link
                    break
        except KeyError:
            pass
        worksheet.write(i, 2, hello_world)

        # Find Hello World files table and output True if "mbed.bld" is present
        hello_url = base_url + hello_world
        hello_page = requests.get(hello_url)
        hello_soup = BeautifulSoup(hello_page.content, 'html.parser')
        old_mbed = ""
        try:
            hello_table = [link.get('href') for link in hello_soup.find_all(hello_world_filter)]
            old_mbed = any('mbed.bld' in link for link in hello_table)
        except KeyError:
            pass
        worksheet.write(i, 3, old_mbed)
        i = i + 1
        print item
    print "Saving " + temp_name + "..."
    book.save("mbed-components.xls")

print "Saving workbook..."
book.save("mbed-components.xls")