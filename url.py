import xlwt
import requests
from bs4 import BeautifulSoup

# Initialize Excel workbook
book = xlwt.Workbook(encoding="utf-8")

components_url = "https://developer.mbed.org/components"
base_url = "https://developer.mbed.org"
components_page = requests.get(components_url)
soup = BeautifulSoup(components_page.content, 'html.parser')


# Filters that gather HTML elements based on class name and/or tag type
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
        tag.parent.name == 'td')


def progress(count, total, status):
    percentage = round(100.0 * count / float(total), 1)
    percent = '[' + '{0}%'.format(percentage) + ']: '
    print(percent + status)


# Save the main Components
component_links = [link.get('href') for link in soup(component_filter)]

# Set up Excel worksheet
worksheet = book.add_sheet("Components")
worksheet.write(0, 0, "Component Type")
worksheet.write(0, 1, "Component URL")
worksheet.write(0, 2, "Hello World URL")
worksheet.write(0, 3, )

print "Begin component crawling..."

i = 1
count_components = 0
total_components = 530 # Total number of components available on mbed website as of

for component in component_links:
    remove = "/components/cat/"
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
        mbed_os_lib = ""
        try:
            hello_table = [link.get('href') for link in hello_soup.find_all(hello_world_filter)]
            mbed_os_lib = any('mbed-os.lib' in link for link in hello_table)
        except KeyError:
            pass
        worksheet.write(i, 3, mbed_os_lib)
        i += 1
        count_components += 1
        progress(count_components, total_components, item)

    # progress(count_components, total_components, "Saving " + temp_name)
    book.save("mbed-components.xls")

book.save("mbed-components.xls")