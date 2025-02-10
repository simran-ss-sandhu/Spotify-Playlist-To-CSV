from playwright.sync_api import sync_playwright
import urllib.parse
import json
from bs4 import BeautifulSoup
from tqdm import tqdm


def __parse_query(query: str):
    query = urllib.parse.unquote(query)  # url decode
    query = query.split("&")  # split attributes
    query = [key_value.split("=") for key_value in query]  # split 'attribute=value' pairings
    query = [[key, json.loads(value)]  # convert appropriate str values to dict type
             if value[0] == "{" and value[-1] == "}"
             else [key, value]
             for [key, value] in query]
    query = {key: value for [key, value] in query}  # convert list to dict
    return query


def __scrape_page_content(page_content: str) -> (str, int):

    # parse page html tags
    soup = BeautifulSoup(page_content, "html.parser")

    # extract playlist metadata
    if not soup.head:
        tqdm.write("ERROR: Web page has no <head> tag")
        return None, None
    playlist_name = soup.head.find("meta", attrs={"property": "og:title"}).get("content")
    playlist_len = int(soup.head.find("meta", attrs={"name": "music:song_count"}).get("content"))

    return playlist_name, playlist_len


def scrape_page(playlist_url) -> (str, int, dict, dict):

    # target requests search status
    found_fetch_playlist_request = False
    found_fetch_playlist_metadata_request = False

    # target requests information
    fetch_playlist_request = {"url": '', "params": {}, "headers": {}}
    fetch_playlist_metadata_request = {"url": '', "params": {}, "headers": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def check_for_target_requests(request):
            nonlocal found_fetch_playlist_request, found_fetch_playlist_metadata_request

            # target requests use GET method
            if not request.method == "GET":
                return

            # target requests uses pathfinder spotify API
            if not request.url.startswith("https://api-partner.spotify.com/pathfinder/"):
                return

            # parse request url and parameters
            parsed_url = urllib.parse.urlparse(request.url)
            query_params = __parse_query(parsed_url.query)

            # looking for specific API operations
            if not found_fetch_playlist_request and query_params["operationName"] == "fetchPlaylist":
                found_fetch_playlist_request = True
                fetch_playlist_request["url"] = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
                fetch_playlist_request["params"] = query_params
                fetch_playlist_request["headers"] = request.headers
            elif not found_fetch_playlist_metadata_request and query_params["operationName"] == "fetchPlaylistMetadata":
                found_fetch_playlist_metadata_request = True
                fetch_playlist_metadata_request["url"] = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
                fetch_playlist_metadata_request["params"] = query_params
                fetch_playlist_metadata_request["headers"] = request.headers
        page.on("request", check_for_target_requests)

        page.goto(playlist_url)  # load playlist page

        playlist_name, playlist_len = __scrape_page_content(page.content())

        # wait for targets requests to be found
        while not found_fetch_playlist_request and not found_fetch_playlist_metadata_request:
            page.wait_for_timeout(100)

        browser.close()

    return playlist_name, playlist_len, fetch_playlist_request, fetch_playlist_metadata_request
