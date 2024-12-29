

import os
import json
import argparse
import configparser
from lunr import lunr
from urllib.parse import urlparse
from write_html import generate_html
from watchful import return_redd_objects

def get_lunr_posts_index(subreddits: list[dict]):
    print('Generating search index')
    to_index = []
    chunk_size = 1000
    idxs = []
    metadata = {}
    for s in subreddits.keys():
        for t in subreddits[s]:
            meta = {}
            t['path'] = t['permalink'].lower().replace(f'r/{s}', '').strip('/') + '.html'
            meta['path'] = t['path']
            meta['title'] = t['title']
            meta['score'] = t['score']
            meta['replies'] = str(len(t['comments']))
            meta['body_short'] = t['selftext'][:200]
            meta['date'] = t['created_utc']
            metadata[t['id']] = meta

            to_index.append(t)

    chunks = [to_index[i * chunk_size:(i + 1) * chunk_size] for i in range((len(to_index) + chunk_size - 1) // chunk_size )]
    for chunk in chunks:
        idxs.append(lunr(
            ref='id',
            fields=[
                'id',
                dict(field_name='title', boost=15),
                dict(field_name='selftext', boost=10),
                'score',
                'author'
            ],
            documents=chunk,
            ))
        print(f'\rCreating index chunk: {chunks.index(chunk) + 1}/{len(chunks)}', end='')
    print('')
    return idxs, metadata
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


        complete_reddit_threads = []

        for p in raw_posts:
            p['comments'] = []
            postp = urlparse(p['permalink']).path
            if postp.endswith('/'):
                postp = postp[:-1]
            if postp in comments.keys():
                p['comments'] = comments[postp]

                complete_reddit_threads.append(p)

        subreddits[s.lower()] = complete_reddit_threads

    print("Total threads: ",len(raw_posts))
    print("Total comments: ", len(raw_comments))
    print("Comments missing permalinks: ", len(missing_perm))
    print("Comment chains found: ", len(comments))
    print("Threads rebuilt: ", len(complete_reddit_threads))

    idxs, metadata = get_lunr_posts_index(subreddits)

    idx_path_list = []
    for idx in idxs:
        idx_name = f'static/js/search/idx-00{idxs.index(idx) + 1}.json'

        idx_path_list.append(idx_name) 
        print(f'\rWriting: {idx_name}',end='')
        with open(f'r/{idx_name}', 'w') as f:
            json.dump(idx.serialize(),f)
    with open('r/static/js/search/search-idx-list.json','w') as f:
        json.dump(idx_path_list, f)
    with open('r/static/js/search/metadata.json', 'w') as f:
        json.dump(metadata, f)
    print('')
    generate_html([s.lower() for s in config.sections()], subreddits)

if __name__ == "__main__":
    main()
