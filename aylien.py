from aylienapiclient import textapi
input = open("sample.txt", "r")
client = textapi.Client("d621808f", "0dce361412a8b1daefdbcd7ec0de1184")
for i in input.readlines():
    sentiment = client.Sentiment({'text': i})
    print(sentiment)