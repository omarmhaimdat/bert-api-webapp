from flask import Flask
from flask_restful import Resource, Api
import twitter
from bert_model.Bert import Bert
import torch

app = Flask(__name__)
api = Api(app)

ACCESS_TOKEN = '526136285-OABt60RomqxJvfDxQZdQwldqVnuOdAHMt4sLhESw'
ACCESS_TOKEN_SECRET = 'TfxDxvp95uq4CHwJYiyFnIjlnj1wCm3M1Q4B62RLMm1B7'
CONSUMER_KEY = 'KfnSHNfppfQSH0KETwyI5sg4d'
CONSUMER_SECRET = 'Um3tbIvf3eGNghLKZ0YIw42ZhgLBsBh97ohG0HLKaotgEXo27v'

path = '/Users/omarmhaimdat/PycharmProjects/projet_synthese/bert_model/bert_version_4.pth'
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
classes = ['neutral', 'positive', 'negative']

LANGUAGES = ['en']

twitter_api = twitter.Api(CONSUMER_KEY,
                          CONSUMER_SECRET,
                          ACCESS_TOKEN,
                          ACCESS_TOKEN_SECRET)


def get_tweets(brand: str) -> list:
    query = 'q=%22' + brand + '%22%20-RT%20lang%3Aen%20until%3A2020-02-15%20since%3A2019-01-29%20-filter%3Alinks%20' \
                              '-filter%3Areplies&src=typed_query&count=20'
    results = twitter_api.GetSearch(raw_query=query,
                                    count=10,
                                    return_json=True,
                                    lang='en')
    return results


class Tweets(Resource):
    def get(self, brand):
        results = get_tweets(brand)
        only_tweets = results['statuses']
        tweets = []
        i = 0
        for tweet in only_tweets:
            tweets.append({'text': tweet['text']})
            i = i + 1
        final_tweets = {'tweets': tweets}
        return final_tweets


class Sentiments(Resource):
    def get(self, brand):
        tweets_text = Tweets.get(self, brand=brand)
        tweets_list = tweets_text['tweets']
        neutral = 0
        positive = 0
        negative = 0
        for tweet in tweets_list:
            inference_tensor = Bert.inference(model_path=path, sentence=tweet.get('text'), device=device)
            prediction = Bert.inference_class(tensor=inference_tensor, classes=classes)
            if prediction == 'neutral':
                neutral += 1
            elif prediction == 'positive':
                positive += 1
            else:
                negative += 1
        return {'neutral': neutral,
                'positive': positive,
                'negative': negative,
                'tweets': tweets_list}


class FinalApi(Resource):
    def get(self, brand):
        results = get_tweets(brand)
        only_tweets = results['statuses']
        tweets = []
        neutral = 0
        positive = 0
        negative = 0
        for tweet in only_tweets:
            inference_tensor = Bert.inference(model_path=path, sentence=tweet.get('text'), device=device)
            prediction = Bert.inference_class(tensor=inference_tensor, classes=classes)
            confidence = Bert.get_confidence(inference_tensor)
            if prediction == 'neutral':
                neutral += 1
            elif prediction == 'positive':
                positive += 1
            else:
                negative += 1
            tweets.append({'text': tweet['text'],
                           'created_at': tweet['created_at'],
                           'brand': brand,
                           'sentiment': prediction,
                           'confidence': float(confidence),
                           'lang': tweet['lang']})
        number_of_tweets = neutral + positive + negative
        final_tweets_with_prediction = {'number_of_tweets': number_of_tweets,
                                        'neutral': neutral,
                                        'positive': positive,
                                        'negative': negative,
                                        'tweets': tweets}
        return final_tweets_with_prediction


api.add_resource(Tweets, '/tweets/<string:brand>')
api.add_resource(Sentiments, '/sentiments/<string:brand>')
api.add_resource(FinalApi, '/<string:brand>')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
