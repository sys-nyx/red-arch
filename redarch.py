

import os
import json
import argparse
import configparser
from urllib.parse import urlparse
from write_html import generate_html
from watchful import return_redd_objects

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=str, help='Path to configuration file.')
    args = parser.parse_args()
    if not args.config:
        print("No config file found")
        exit()

    config = configparser.ConfigParser()
    config.read(args.config)

    subreddits = {}

    for s in config.sections():
        
        posts_path = config[s]['posts']
        comments_path = config[s]['comments']

        links = []
        
        print(f"loading from {posts_path}")
        raw_posts = return_redd_objects(posts_path)
        print('done')
        print(f"loading from {comments_path}")
        raw_comments = return_redd_objects(comments_path)
        print('done')

        missing_perm = []
        comments = {}
        for c in raw_comments:
            if 'permalink' not in c.keys():
                missing_perm.append(c)
                continue
            
            parent_url = '/'.join(urlparse(c['permalink']).path.split('/')[:6])
            if parent_url.endswith('/'):
                parent_url = parent_url[:-1]
            if parent_url not in comments.keys():
                comments[parent_url] = []
            comments[parent_url].append(c)


        complete_threads = []

        for p in raw_posts:
            p['comments'] = []
            postp = urlparse(p['permalink']).path
            if postp.endswith('/'):
                postp = postp[:-1]
            if postp in comments.keys():
                p['comments'] = comments[postp]

                complete_threads.append(p)

        subreddits[s.lower()] = complete_threads

    print("Total threads: ",len(raw_posts))
    print("Total comments: ", len(raw_comments))
    print("Comments missing permalinks: ", len(missing_perm))
    print("Comment chains found: ", len(comments))
    print("Threads rebuilt: ", len(complete_threads))


    generate_html([s.lower() for s in config.sections()], subreddits)

if __name__ == "__main__":
    main()
