import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pprint import pprint

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

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

    # initial check on response
    if resp.status != 200:
        print('connection not successful') # @TODO: handle error
        return urls
    elif not resp.raw_response.content:
        return urls

    content = resp.raw_response.content

    # parse the content
    soup = BeautifulSoup(content, 'html.parser')

    # finds all hyperlinks
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and is_valid(href):
            # @TODO: I might also want to check if the page has a low information value
            # @TODO: And also check to avoid traps
            urls.append(href)

    # @TODO: word ananlysis
    #  soup.get_text() # This will give us all the text content
    #  We can now use our assignment1 code on the text to analyze the word statistics

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
        # @TODO: Find more elegant way to do this
        if parsed.hostname and \
                ics_paths[0] not in parsed.hostname and \
                ics_paths[1] not in parsed.hostname and \
                ics_paths[2] not in parsed.hostname and \
                ics_paths[3] not in parsed.hostname:
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

    except TypeError:
        print ("TypeError for ", parsed)
        raise
