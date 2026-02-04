import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pprint import pprint
from collections import defaultdict

unique_urls: set[str]               = set()
unique_subdomains: dict[str, int]   = defaultdict(int)
word_count: dict[str, int]          = {}

def write_statistics():
    """Writes statistics required for the report in report.txt"""
    a = sorted(word_count)

    with open("report.txt", 'w', encoding='utf-8') as file:
        # 1. how many unique pages did you find?
        file.write(f"1. Number of Unique URLs: {len(unique_urls)}\n")

        # 2. 
        file.write(f"2. Longest page: {max(word_count, key=lambda item: item[1])}\n")

        # 3. 

        # 4. how many unique subdomains
        sorted_unique_subdomains = sorted(unique_subdomains.items(), key=lambda item: (item[0], item[1]))
        file.write(f"4. Unique Subdomains:\n")
        for subdomain, cnt in sorted_unique_subdomains:
            file.write(f"\t{subdomain}: {int(cnt)}\n")



def scraper(url, resp):
    # initial check on response
    if resp.status != 200:
        print('connection not successful')
        return []
    elif not resp.raw_response.content:
        print('page without content')
        return []

    # getting wordcount
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    paragraph = soup.get_text()
    token_list = tokenize(url, paragraph)

    # getting statistics
    parsed = urlparse(url)
    unique_urls.add(parsed._replace(fragment='').geturl())      # no fragment
    unique_subdomains[parsed._replace(fragment='').netloc] += 1

    # only visit 100 pages for the test
    if len(unique_urls) > 100:
        return []

    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def tokenize(url, raw_words) -> list:

    #lowercase all char to be lowercase to deal with edge cases
    lowercase = raw_words.casefold()
    
    token_list = []
    tmp_word = []

    #check current char for valid alpha-numerical, then add it to tmp list until non-valid char. Then add complete string to list
    for char in lowercase:
        if char.isascii() and char.isalnum():
            tmp_word.append(char)
        elif char == "'" or char == "-":
            continue
        else:
            if tmp_word:
                new_word = "".join(tmp_word)
                token_list.append(new_word)
                tmp_word = []
                
    word_count[url] = len(token_list)
    
    return token_list

def printMostWordUrl(word_count):
    max_url = max(word_count, key=lambda item: item[1])
    max_count = word_count[max_url]
    
    print(f"Max URL: {max_url} with {max_count} words")
        
def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    urls = []

    content = resp.raw_response.content

    # parse the link
    soup = BeautifulSoup(content, 'html.parser')

    # finds all hyperlinks
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and is_valid(href):
            # @TODO: I might also want to check if the page has a low information value
            urls.append(href)

    return urls

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:    

        # if an empty string, return False
        if not url:
            return False

        # only valid http
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # Is it ICS?
        ics_paths = ("ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu")
        if parsed.hostname and \
                ics_paths[0] not in parsed.hostname and \
                ics_paths[1] not in parsed.hostname and \
                ics_paths[2] not in parsed.hostname and \
                ics_paths[3] not in parsed.hostname:
            return False

        
        # links to avoid 
        traps = ('isg.ics.uci.edu/events/tag/talk',)
        for trap in traps:
            if trap in parsed.geturl():
                return False
        
        # avoidng textbook because we don't really need all textbook content from information retreival perspective
        textbooks = ('www.ics.uci.edu/~wjohnson/BIDA',)
        for textbook in textbooks:
            if textbook in parsed.geturl():
                return False

        # '.edu/people/...' always gives 608 and is redundant with '.edu/?people=...'
        if 'ics.uci.edu/people/' in parsed.geturl():
            return False

        # check for robots.txt
        # NeedToImplement

        return not re.match(
                    r".*\.(css|js|bmp|gif|jpe?g|ico"
                    + r"|png|tiff?|mid|mp2|mp3|mp4"
                    + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                    + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                    + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                    + r"|epub|dll|cnf|tgz|sha1"
                    + r"|thmx|mso|arff|rtf|jar|csv"
                    + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
    except Exception as e:
        print ("Error for ", parsed)
        print(e)
        return False

