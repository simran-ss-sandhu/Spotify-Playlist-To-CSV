import json
import requests


def __build_playlist_contents_request(fetch_playlist_request: dict, fetch_playlist_metadata_request: dict,
                                      playlist_len: int) -> (str, dict, dict):

    request_url = fetch_playlist_metadata_request["url"]

    custom_request_params = fetch_playlist_request["params"]
    custom_request_params["operationName"] = "fetchPlaylistContents"
    custom_request_params["variables"].pop("enableWatchFeedEntrypoint")
    custom_request_params["variables"]["offset"] = 0
    custom_request_params["variables"]["limit"] = playlist_len
    custom_request_params = {key: (json.dumps(value) if isinstance(value, dict) else value)
                             for key, value in custom_request_params.items()}

    request_headers = fetch_playlist_metadata_request["headers"]

    return request_url, custom_request_params, request_headers


def __format_playlist_contents(playlist_contents: dict) -> [dict]:
    items = playlist_contents["data"]["playlistV2"]["content"]["items"]

    all_songs_metadata = []

    for item in items:
        song_metadata = {"Artists": '', "Title": '', "URL": ''}
        item = item["itemV2"]["data"]

        # skip if the item does not describe a song track
        if item["__typename"] != "Track":
            continue

        artists = [artist_item["profile"]["name"] for artist_item in item["artists"]["items"]]
        artists = " / ".join(artists)
        song_metadata["Artists"] = artists

        song_metadata["Title"] = item["name"]

        url = item["uri"]
        url = url.split(":")
        url = "https://open.spotify.com/track/" + url[-1]
        song_metadata["URL"] = url

        all_songs_metadata.append(song_metadata)

    return all_songs_metadata


def get_formatted_playlist_contents(fetch_playlist_request: dict, fetch_playlist_metadata_request: dict,
                                    playlist_len: int) -> [dict]:
    request_url, params, headers = __build_playlist_contents_request(
        fetch_playlist_request, fetch_playlist_metadata_request, playlist_len)

    response = requests.get(request_url, params=params, headers=headers)  # make request to API

    all_songs_metadata = __format_playlist_contents(response.json())

    return all_songs_metadata
