

import os
import json
import argparse
import configparser
from lunr import lunr
from datetime import datetime
from urllib.parse import urlparse
from write_html import generate_html
from watchful import return_redd_objects

def rebuild_threads(threads: list[dict], comments:list[dict]) -> list[dict]:
    print('Rebuilding threads...')
    threads_dict = {}

    for t in threads:
        t['comments'] = []
        threads_dict[t['id']] = t
        t['subreddit'] = t['subreddit'].lower()

    for c in comments:
        if 'permalink' not in c.keys():
            continue

        parent_thread_id = c['permalink'].split('/')[4]

        if parent_thread_id not in threads_dict.keys():
            continue

        threads_dict[parent_thread_id]['comments'].append(c)

    return [threads_dict[t] for t in threads_dict.keys()]


def rebuild_subreddits(threads: list[dict]) -> dict:
    print("Rebuilding subreddits...")
    subreddits = {}

    for t in threads:
        if t['subreddit'] not in subreddits.keys():
            subreddits[t['subreddit']] = []
        subreddits[t['subreddit']].append(t)

    return subreddits


def get_thread_meta(thread: dict) -> dict:
    return {
        'id': thread['id'],
        'path': thread['permalink'].lower().replace(f'r/{thread["subreddit"]}', '').strip('/') + '.html',
        'title': thread['title'],
        'score': thread['score'],
        'replies': str(len(thread['comments'])),
        'body_short': thread['selftext'][:200],
        'date': datetime.utcfromtimestamp(int(thread['created_utc'])).strftime('%Y-%m-%d'),
        'author': thread['author'],
        'subreddit': thread['subreddit']
    }


def get_comment_meta(comment: dict) -> dict:
    return {
        'id': comment['id'],
        'path': comment['path'],
        'title': comment['title'],
        'score': comment['score'],
        'body_short': comment['selftext'][:200],
        'date': datetime.utcfromtimestamp(int(comment['created_utc'])).strftime('%Y-%m-%d'),
        'author': comment['author']
    }


def get_lunr_index(subreddits: list[dict]):
    print('Generating search index...')
    to_index = []
    chunk_size = 1000
    idxs = []
    metadata = {}
    for s in subreddits.keys():
        for t in subreddits[s]:
            meta = get_thread_meta(t)
            metadata[t['id']] = meta
            i = (t, {'boost': t['score']})
            to_index.append(i)

    chunks = [to_index[i * chunk_size:(i + 1) * chunk_size] for i in range((len(to_index) + chunk_size - 1) // chunk_size )]
    for chunk in chunks:
        print(f'\rParsing index chunk: {chunks.index(chunk) + 1}/{len(chunks)}', end='')

        idxs.append(lunr(
            ref='id',
            fields=[
                dict(field_name='title', boost=15),
                dict(field_name='selftext', boost=10),
                'score',
                'author'
            ],
            documents=chunk,
        ))

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

    raw_posts = []
    raw_comments = []

    for s in config.sections():

        posts_path = config[s]['posts']
        comments_path = config[s]['comments']
        
        print(f"Loading from {posts_path}")
        raw_posts += return_redd_objects(posts_path)
        
        print(f"Loading from {comments_path}")
        raw_comments += return_redd_objects(comments_path)

    threads = rebuild_threads(raw_posts, raw_comments)
    subreddits = rebuild_subreddits(threads)

    idxs, metadata = get_lunr_index(subreddits)

    os.makedirs('r/static/js/search/', exist_ok=True)

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

    generate_html(subreddits)

if __name__ == "__main__":
    main()
