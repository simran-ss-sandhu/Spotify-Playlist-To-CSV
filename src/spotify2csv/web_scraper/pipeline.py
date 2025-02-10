import spotify2csv.web_scraper.page_scraper
import spotify2csv.web_scraper.api_scraper


def web_scraper_pipeline(playlist_url: str) -> (str, [dict]):

    # scrape directly from the playlist webpage
    (playlist_name,
     playlist_len,
     fetch_playlist_request,
     fetch_playlist_metadata_request) = spotify2csv.web_scraper.page_scraper.scrape_page(playlist_url)

    # scrape from Spotify's API
    all_songs_metadata = spotify2csv.web_scraper.api_scraper.get_formatted_playlist_contents(
        fetch_playlist_request,
        fetch_playlist_metadata_request,
        playlist_len)

    return playlist_name, all_songs_metadata
