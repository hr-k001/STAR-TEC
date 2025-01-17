from flask import Flask, request, render_template, jsonify
from googleapiclient.discovery import build
from textblob import TextBlob
from pymongo import MongoClient

API_KEY = 'Your_API'

app = Flask(__name__)

client = MongoClient("mongodb+srv://<your_username>:<your_pass>@cluster0.q6klp.mongodb.net/")
db = client['YouTubeAnalyzer']
contact_collection = db['ContactUs'] 
@app.route('/')
def index():
    return render_template('index.html', comments=None, positivePercentage=0, neutralPercentage=0, negativePercentage=0)

@app.route('/scrape-comments', methods=['POST'])
def scrape_comments():
    video_id = request.json.get('videoId') 
    comments = get_youtube_comments(video_id)
    sentiments = analyze_sentiments(comments)
    return jsonify({
        'comments': comments,
        'positivePercentage': sentiments['positive'],
        'neutralPercentage': sentiments['neutral'],
        'negativePercentage': sentiments['negative']
    })

def get_youtube_comments(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100
    ).execute()
    comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]
    return comments

def analyze_sentiments(comments):
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    for comment in comments:
        analysis = TextBlob(comment)
        if analysis.sentiment.polarity > 0:
            positive_count += 1
        elif analysis.sentiment.polarity == 0:
            neutral_count += 1
        else:
            negative_count += 1
    total = positive_count + neutral_count + negative_count
    positive_percentage = (positive_count / total) * 100 if total > 0 else 0
    neutral_percentage = (neutral_count / total) * 100 if total > 0 else 0
    negative_percentage = (negative_count / total) * 100 if total > 0 else 0
    return {
        'positive': positive_percentage,
        'neutral': neutral_percentage,
        'negative': negative_percentage
    }
@app.route('/contact', methods=['POST'])
def contact_us():
    
    data = request.json 
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    contact_collection.insert_one({
        "name": name,
        "email": email,
        "message": message
    })
    
    return jsonify({"message": "Thank you for reaching out!"}), 201

if __name__ == '__main__':
    app.run(debug=True)
