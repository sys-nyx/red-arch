## Red-arch

## Overview
The goal of this project is to provide a framework for archiving websites and social media -  with a particular focus on subreddits - and creating compilations of information in ways that are very easy for non-tech-savy people to consume, copy, and distribute.

[reddit-html-archiver](https://github.com/libertysoft3/reddit-html-archiver) was chosen as the base for this project for a number of reasons:
- It generates a static website. This is very important due to a static website being the best option for compiling data according to the needs of this project.  
- Its styled nicely.
- Its written in python which will make integration with other web scrapers or data dumps very simple.
- Takes minimal changes to accept data from popular reddit data dumps like such as pushshift

At the moment this project is limited to creating static sites from https://academictorrents.com/details/56aa49f9653ba545f48df2e33679f014d2829c10. the user esponsible for the uplaods provides a repo [here](https://github.com/Watchful1/PushshiftDumps) with some tools for parsing through the files contained in the torrent. This repo provides a modified version of their 'single_file.py' as 'watchful.py' which can be used as to convert the subreddit dumps into json files. Those files can then be added to config.toml and used to create a website.
 
### install

```
git clone https://github.com/sys-nyx/red-arch
cd red-arch/
# Init a virtual environment first if you prefer
pip install requirements.txt

```

### Usage

```
cd red-arch/
python3 watchful.py subname1_submissions.zst subname1_submissions.json
python3 watchful.py subname1_comments.zst subname1_comments.json

python3 watchful.py subname2_submissions.zst subname2_submissions.json
python3 watchful.py subname2_comments.zst subname2_comments.json

```

```
nano config.toml

```
```
[subname1]
comments= subname1_comments.json
posts= subname1_submissions.json

[subname2]
comments= subname2_comments.json
posts= subname2_submissions.json
```

```
dumps.py config.toml
```

The resulting website will be located within the 'r/' directory and can be viewed by placing it in the webroot of any http server OR by opening index.html in your browser. 

The maintainers of this repo are NOT responsible for any problems with your system or data loss that might occur from using anything contained within this repo to modify your local files. Please make copies of our data before you begin modifying it. 

## Below is the readme from the original repository. [reddit-html-archiver](https://github.com/libertysoft3/reddit-html-archiver)
Please note that it is ONLY included here for archival purposes and does not necessarily reflect the goals/intentions/usage of red-arch.  

python3
## reddit html archiver

pulls reddit data from the [pushshift](https://github.com/pushshift/api) api and renders offline compatible html pages. uses the reddit markdown renderer.

### install

requires python 3 on linux, OSX, or Windows. 

**warning:** if `$ python --version` outputs a python 2 version on your system, then you need to replace all occurances of `python` with `python3` in the commands below.

    $ sudo apt-get install pip
    $ pip install psaw -U
    $ git clone https://github.com/chid/snudown
    $ cd snudown
    $ sudo python setup.py install
    $ cd ..
    $ git clone [this repo]
    $ cd reddit-html-archiver
    $ chmod u+x *.py

Windows users may need to run

    > chcp 65001
    > set PYTHONIOENCODING=utf-8

before running `fetch_links.py` or `write_html.py` to resolve encoding errors such as 'codec can't encode character'.

### fetch reddit data

fetch data by subreddit and date range, writing to csv files in `data`:

    $ python ./fetch_links.py politics 2017-1-1 2017-2-1
    
or you can filter links/posts to download less data:

    $ python ./fetch_links.py --self_only --score "> 2000" politics 2015-1-1 2016-1-1
    
to show all available options and filters run:

    $ python ./fetch_links.py -h

decrease your date range or adjust `pushshift_rate_limit_per_minute` in `fetch_links.py` if you are getting connection errors.

### write web pages

write html files for all subreddits to `r`:

    $ python ./write_html.py

you can add some output filtering to have less empty postssmaller archive size

    $ python ./write_html.py --min-score 100 --min-comments 100 --hide-deleted-comments
    
to show all available filters run:

    $ python ./write_html.py -h

your html archive has been written to `r`. once you are satisfied with your archive feel free to copy/move the contents of `r` to elsewhere and to delete the git repos you have created. everything in `r` is fully self contained.

to update an html archive, delete everything in `r` aside from `r/static` and re-run `write_html.py` to regenerate everything.

### hosting the archived pages

copy the contents of the `r` directory to a web root or appropriately served git repo.

### potential improvements

* fetch_links
  * num_comments filtering
  * thumbnails or thumbnail urls
  * media posts
  * score update
  * scores from reddit with [praw](https://github.com/praw-dev/praw)
* real templating
* choose [Bootswatch](https://bootswatch.com/) theme
* specify subreddits to output
* show link domain/post type
* user pages
  * add pagination, posts sorted by score, comments, date, sub
  * too many files in one directory
* view on reddit.com
* js powered search page, show no links by default
* js inline media embeds/expandos
* archive.org links

### see also

* [pushshift](https://github.com/pushshift/api), [r/pushshift](https://www.reddit.com/r/pushshift/)
* [psaw](https://github.com/dmarx/psaw)
* [snudown](https://github.com/reddit/snudown)
* [redditsearch.io](https://redditsearch.io/)
* [reddit post archiver](https://github.com/sJohnsonStoever/redditPostArchiver)
* [reddit downloader](https://github.com/shadowmoose/RedditDownloader)

### screenshots

![](screenshots/sub.jpg)
![](screenshots/post.jpg)
