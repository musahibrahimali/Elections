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
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def main():
    # the Script targets any of these keywords in the loop
    terms = [
        "akuffo addo", "bawumia", "npp", "vice president of Ghana", "nana addo dankwa akuffo addo", "4MoreForNana",
        "sitting government of ghana", "john dramani mahama", "ndc", "former president of Ghana", "JMandJane2020",
        "mahama led administration", "JohnMahama2020", "NDCmanifesto"
    ]

    # insert the keyword here for the extraction to continue
    retweet_filter = '-filter:retweets'

    # append the term to search parameters
    q = retweet_filter
    tweets_per_qry = 100
    since_id = None

    max_id = -1
    max_tweets = 1000

    tweet_count = 0

    # Usernames whose tweets we want to gather.
    users = [
        "NAkufoAddo",
        "JDMahama",
        "MBawumia",
        "NJOAgyemang",
        "wontumi_1",
        "ndcgreenarmy",
    ]

    # giving the user some feed back that the script is running
    print("Downloading tweets from user timelines...")

    # extract tweets from timeline of targeted politicians of the major political parties
    try:
        with open('../data/tweets.csv', 'ab') as file:
            writer = unicodecsv.writer(file, delimiter=',', quotechar='"')
            # Write header row.

            # write the titles for each column
            writer.writerow([
                "Tweet Date",
                "Tweet ID",
                "Tweet Text",
                "tweet_source",
                "tweet_retweet_count",
                "tweet_favorite_count"
            ])

            # loop through all the users and extract tweets from their relative timelines
            for user in users:

                # Get 1000 most recent tweets for the current user.
                for tweet in Cursor(api.user_timeline, screen_name=user).items(1000):
                    # Get info specific to the current tweet of the current user.
                    tweet_text = unidecode(tweet.text)

                    # format the date
                    tweet_date = str(tweet.created_at.year) + "/" + str(tweet.created_at.month) + "/" + str(
                        tweet.created_at.day)

                    tweet_source = tweet.source

                    retweet_count = tweet.retweet_count

                    favorite_count = tweet.favorite_count

                    tweet_id = tweet.id

                    # Write the extracted tweets to CSV.
                    writer.writerow([
                        tweet_date, tweet_id, tweet_text, tweet_source,
                        retweet_count, favorite_count,
                    ])

                # Show progress.
                print("Wrote tweets of %s to CSV." % user)

            print("streaming at least {0} tweets".format(max_tweets))
            for term in terms:
                search_query = term + q
                while tweet_count < max_tweets:
                    try:
                        if max_id <= 0:
                            if not since_id:
                                new_tweets = api.search(q=search_query, lang="en", count=tweets_per_qry,
                                                        tweet_mode='extended')

                            else:
                                new_tweets = api.search(q=search_query, lang="en", count=tweets_per_qry,
                                                        since_id=since_id, tweet_mode='extended')
                        else:
                            if not since_id:
                                new_tweets = api.search(q=search_query, lang="en", count=tweets_per_qry,
                                                        max_id=str(max_id - 1), tweet_mode='extended')
                            else:
                                new_tweets = api.search(q=search_query, lang="en", count=tweets_per_qry,
                                                        max_id=str(max_id - 1),
                                                        since_id=since_id, tweet_mode='extended')

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

                        tweet_count += len(new_tweets)
                        print("Downloaded {0} tweets".format(tweet_count))
                        max_id = new_tweets[-1].id

                    except tweepy.TweepError as e:
                        # Just exit if any error
                        print("some error : " + str(e))
                        break
            print("Downloaded at least {0} tweets, Saved to csv file".format(tweet_count))
    except tweepy.TweepError as e:
        print("There was an error, find details below, else check your internet connection or your " +
              " credentials in the credentials.py file \n")
        print("If this is not your first time running this particular script, then there is a possibility that the "
              "maximum rate limit has been exceeded. wait a few more minutes and re run the script.\n")
        print(f"Error Details: {str(e)}")


if __name__ == "__main__":
    main()
