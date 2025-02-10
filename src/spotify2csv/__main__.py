import math
import pandas as pd
import re
from tqdm import tqdm
import sys
import os
import spotify2csv.web_scraper.pipeline


def __partition_list(data: list, num_of_partitions: int):
    partition_size = math.ceil(len(data) / num_of_partitions)
    partitions = [data[i:i+partition_size] for i in range(0, len(data), partition_size)]
    return partitions


def __save_to_csv_file(data: [dict], playlist_name):

    # create name for unnamed playlists
    if not playlist_name:
        counter = 1
        output_filename = f"unnamed_playlist_{counter}.csv"
        while os.path.exists(output_filename):
            counter += 1
            output_filename = f"unnamed_playlist_{counter}.csv"

    else:
        output_filename = re.sub(r'[^a-zA-Z0-9]', '_', playlist_name) + '.csv'

    # save to csv file
    df = pd.DataFrame(data)
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    tqdm.write(f"Saved output to '{output_filename}'")


def __process_playlist(playlist_url):

    playlist_name, all_songs_metadata = spotify2csv.web_scraper.pipeline.web_scraper_pipeline(playlist_url)
    if not all_songs_metadata:
        tqdm.write(f"ERROR: Could not process '{playlist_url}'")
        return

    __save_to_csv_file(all_songs_metadata, playlist_name)


def main():
    # program startup instructions
    print("Enter a Spotify Playlist URL below (or type 'run' to start conversions, or 'exit' to quit).")

    playlist_urls = set()

    while True:
        playlist_url = input("URL: ")
        if playlist_url.lower() == 'exit':
            break
        elif playlist_url.lower() == 'run':
            for url in tqdm(playlist_urls, desc=f"Processing Playlists...", file=sys.stdout):
                tqdm.write(f"Processing '{url}'")
                __process_playlist(url)
            playlist_urls.clear()
        elif playlist_url.startswith("https://open.spotify.com/playlist/"):
            playlist_urls.add(playlist_url)
        else:
            tqdm.write("ERROR: INVALID PLAYLIST URL OR COMMAND")

    print("Done.")


if __name__ == "__main__":
    main()
