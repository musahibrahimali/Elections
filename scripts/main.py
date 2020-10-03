"""
This script file extract tweets from the timeline of some targeted politician of the major
political parties of Ghana, it extracts the 1000 tweets at each run. and another 1000 from
the timelines of the targeted individuals
"""

import tweepy
from tweepy import Cursor
import unicodecsv
from unidecode import unidecode
from scripts import twitter_credentials as api

# Authentication and connection to Twitter API.
consumer_key = api.CONSUMER_KEY
consumer_secret = api.CONSUMER_SECRET
access_key = api.ACCESS_TOKEN
access_secret = api.ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
# api = tweepy.API(auth)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

terms = [
    "akuffo addo", "bawumia", "npp", "president of ghana", "vice president of Ghana",
    "nana addo dankwa akuffo addo", "nana akuffo addo led administration", "sitting government of ghana",
    "current president of Ghana", "john dramani mahama", "asiedu nketia", "ndc", "ex-president of ghana",
    "former president og Ghana", "ex president of Ghana", "mahama led administration"
]
searchQuery = ''
retweet_filter = '-filter:retweets'

q = searchQuery + retweet_filter
tweetsPerQry = 100
fName = 'tweets.txt'
sinceId = None

max_id = -1
maxTweets = 1000

tweetCount = 0

# Usernames whose tweets we want to gather.
users = [
    "NAkufoAddo",
    "MBawumia",
    "wontumi_1",
    "JDMahama",
    "officeofJJR",
    "NJOAgyemang",
]

print("Downloading tweets from user timelines...")

# extract tweets from timeline of targeted politicians of the major political parties
try:
    with open('../data/tweets.csv', 'ab') as file:
        writer = unicodecsv.writer(file, delimiter=',', quotechar='"')
        # Write header row.

        writer.writerow([
            "Tweet Date",
            "Tweet ID",
            "Tweet Text",
            "tweet_source",
            "tweet_retweet_count",
            "tweet_favorite_count"
        ])

        for user in users:
            user_obj = api.get_user(user)

            # Get 1000 most recent tweets for the current user.
            for tweet in Cursor(api.user_timeline, screen_name=user).items(1000):
                # Latitude and longitude stored as array of floats within a dictionary.
                lat = tweet.coordinates['coordinates'][1] if tweet.coordinates is not None else None
                long = tweet.coordinates['coordinates'][0] if tweet.coordinates is not None else None
                # If tweet is not in reply to a screen name, it is not a direct reply.
                direct_reply = True if tweet.in_reply_to_screen_name != "" else False
                # Retweets start with "RT ..."
                retweet_status = True if tweet.text[0:3] == "RT " else False

                # Get info specific to the current tweet of the current user.
                tweet_text = unidecode(tweet.text)

                tweet_date = str(tweet.created_at.year) + "/" + str(tweet.created_at.month) + "/" + str(
                    tweet.created_at.day)

                tweet_source = tweet.source

                retweet_count = tweet.retweet_count

                favorite_count = tweet.favorite_count

                tweet_id = tweet.id

                # Below entities are stored as variable-length dictionaries, if present.
                hashtags = []
                hashtags_data = tweet.entities.get('hashtags', None)
                if hashtags_data is not None:
                    for i in range(len(hashtags_data)):
                        hashtags.append(unidecode(hashtags_data[i]['text']))

                # get all urls of a tweet
                urls = []
                urls_data = tweet.entities.get('urls', None)
                if urls_data is not None:
                    for i in range(len(urls_data)):
                        urls.append(unidecode(urls_data[i]['url']))

                # get all mentions
                user_mentions = []
                user_mentions_data = tweet.entities.get('user_mentions', None)
                if user_mentions_data is not None:
                    for i in range(len(user_mentions_data)):
                        user_mentions.append(unidecode(user_mentions_data[i]['screen_name']))

                # get all media types
                media = []
                media_data = tweet.entities.get('media', None)
                if media_data is not None:
                    for i in range(len(media_data)):
                        media.append(unidecode(media_data[i]['type']))

                # get all contributors
                contributors = []
                if tweet.contributors is not None:
                    for contributor in tweet.contributors:
                        contributors.append(unidecode(contributor['screen_name']))

                # Write data to CSV.
                writer.writerow([
                    tweet_date, tweet_id, tweet_text, tweet_source,
                    retweet_count, favorite_count,
                ])

            # Show progress.
            print("Wrote tweets of %s to CSV." % user)

        print("streaming at least {0} tweets".format(maxTweets))
        for term in terms:
            searchQuery = term
            while tweetCount < maxTweets:
                tweets = []
                try:
                    if max_id <= 0:
                        if not sinceId:
                            new_tweets = api.search(q=q, lang="en", count=tweetsPerQry, tweet_mode='extended')

                        else:
                            new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                                    since_id=sinceId, tweet_mode='extended')
                    else:
                        if not sinceId:
                            new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                                    max_id=str(max_id - 1), tweet_mode='extended')
                        else:
                            new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                                    max_id=str(max_id - 1),
                                                    since_id=sinceId, tweet_mode='extended')

                    if not new_tweets:
                        print("No more tweets found")
                        break
                    for tweet in new_tweets:
                        tweet_text = unidecode(tweet.full_text)

                        tweet_date = str(tweet.created_at.year) + "/" + str(tweet.created_at.month) + "/" + str(
                            tweet.created_at.day)

                        tweet_source = tweet.source

                        retweet_count = tweet.retweet_count

                        favorite_count = tweet.favorite_count

                        tweet_id = tweet.id
                        writer.writerow([
                            tweet_date, tweet_id, tweet_text, tweet_source,
                            retweet_count, favorite_count,
                        ])

                    tweetCount += len(new_tweets)
                    print("Downloaded {0} tweets".format(tweetCount))
                    max_id = new_tweets[-1].id

                except tweepy.TweepError as e:
                    # Just exit if any error
                    print("some error : " + str(e))
                    break
        print("Downloaded at least {0} tweets, Saved to csv file".format(tweetCount))
except tweepy.TweepError as e:
    print("There was an error, find details below, else check your internet connection or your " +
          " credentials in the credentials.py file \n")
    print("If this is not your first time running this particular script, then there is a possibility that the "
          "maximum rate limit has been exceeded. wait a few more minutes and re run the script\n")
    print("Error Details: " + str(e))
