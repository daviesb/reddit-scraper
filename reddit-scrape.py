# -*- coding: utf-8 -*-

import praw
import psaw
import requests
import time
import datetime
import pandas as pd
import numpy as np


### connect to API
reddit = praw.Reddit(client_id='', \
                     client_secret='', \
                     user_agent='', \ # description of crawler
                     username='', \ # reddit username
                     password='') # reddit pw

### function found 
def submissions_pushshift_praw(subreddit, start=None, end=None, limit=1000, extra_query=""):

    matching_praw_submissions = []
    
    # Convert String dates to Unix timestamp
    start = int(time.mktime(datetime.datetime.strptime(start, "%d/%m/%Y").timetuple()))
    end = int(time.mktime(datetime.datetime.strptime(end, "%d/%m/%Y").timetuple()))

    # Format our search link properly.
    search_link = ('https://api.pushshift.io/reddit/submission/search/'
                   '?subreddit={}&after={}&before={}&sort_type=score&sort=asc&limit={}&q={}')
    search_link = search_link.format(subreddit, start, end, limit, extra_query)
    
    # Get the data from Pushshift as JSON.
    retrieved_data = requests.get(search_link)
    returned_submissions = retrieved_data.json()['data']
    
    # Iterate over the returned submissions to convert them to PRAW submission objects.
    for submission in returned_submissions:
        
        # Take the ID, fetch the PRAW submission object, and append to our list
        praw_submission = reddit.submission(id=submission['id'])
        matching_praw_submissions.append(praw_submission)
     
    # Return all PRAW submissions that were obtained.
    return matching_praw_submissions



test = submissions_pushshift_praw(subreddit="<INSERT-SUBREDDIT-NAME>", start="12/01/2019", end="12/03/2019", limit=5000)

### get top 20 posts as of now
posts = []
sub = reddit.subreddit('<INSERT-SUBREDDIT-NAME>')
for post in sub.hot(limit=10):
    posts.append([post.title, post.score, post.upvote_ratio, post.author, post.url, post.permalink, post.num_comments, post.selftext, post.created, post.id])
### convert to DF
posts = pd.DataFrame(posts, columns=['title', 'score', 'upvote_ratio', 'author', 'url', 'comments_url', 'num_comments', 'body', 'created', 'id'])

### get comments from top 20 posts
comments_list = []
for i, post in posts.iterrows():
    comments = []
    submission = reddit.submission(id=post.id)
    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
        comments.append([comment.body, comment.author, comment.score])
    comments = pd.DataFrame(comments, columns=['body', 'author', 'score'])
    comments_list.append(comments)
