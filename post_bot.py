import praw
from configparser import ConfigParser
from datetime import datetime, timedelta
import requests, requests.auth
import json


class Post_Bot():

    def __init__(self):
        print('Starting up...', self.user_agent)
        CONFIG = ConfigParser()
        CONFIG.read('config.ini')
        self.user = CONFIG.get('main', 'USER')
        self.password = CONFIG.get('main', 'PASSWORD')
        self.client = CONFIG.get('main', 'CLIENT_ID')
        self.secret = CONFIG.get('main', 'SECRET')
        self.timelimit = timedelta(hours=int(CONFIG.get('main', 'TIMELIMIT')))
        self.subreddit = CONFIG.get('main', 'SUBREDDIT')
        self.token_url = "https://www.reddit.com/api/v1/access_token"
        self.reply = CONFIG.get('main', 'REPLY')
        self.token = ""
        self.t_type = ""
        self.user_agent = "'PostLockBot/V1.1 by ScoopJr'"
        self.check_timer = datetime.utcnow()
        self.com = False

    def get_token(self):
        client_auth = requests.auth.HTTPBasicAuth(self.client, self.secret)
        post_data = {'grant_type': 'password', 'username': self.user, 'password': self.password}
        headers = {'User-Agent': self.user_agent}
        response = requests.Session()
        response2 = response.post(self.token_url, auth=client_auth, data=post_data, headers=headers)
        self.token = response2.json()['access_token']
        self.t_type = response2.json()['token_type']

    def lock_posts(self):
        reddit = praw.Reddit(client_id=self.client,
                             client_secret=self.secret,
                             password=self.password,
                             user_agent=self.user_agent,
                             username=self.user)

        for post in reddit.subreddit(self.subreddit).new():
            post_time = datetime.utcfromtimestamp(int(post.created_utc)).strftime('%Y-%m-%d %H:%M:%S')
            post_time = datetime.strptime(post_time,'%Y-%m-%d %H:%M:%S')
            submission = reddit.submission(id=post.id)
            if (((self.check_timer - post_time) > self.timelimit) and (not submission.archived)):
                if submission.locked:
                    self.com = False
                    for comments in submission.comments:
                        if (comments.body == self.reply) & (comments.author == self.user):
                            self.com = True
                            break
                    if not self.com:
                        submission.mod.unlock()
                        submission.reply(self.reply)
                        submission.mod.lock()
                elif not submission.locked:
                    self.com = False
                    for comments in submission.comments:
                        if (comments.body == self.reply) & (comments.author == self.user):
                            self.com = True
                            break
                    if self.com:
                        submission.mod.lock()
                    else:
                        submission.reply(self.reply)
                        submission.mod.lock()
                        continue
        print('Finished locking posts that meet criteria.')













if __name__ == "__main__":
    bot = Post_Bot()
    bot.get_token()
    bot.lock_posts()

