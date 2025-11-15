import boto3
import csv
import io
from decimal import Decimal

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
comprehend = boto3.client('comprehend')

# DynamoDB table
table = dynamodb.Table('SentimentScopeReviews')

def lambda_handler(event, context):
    # 1 Get bucket & object info from the S3 trigger or test event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print(f"Processing file from bucket: {bucket}, key: {key}")

    # 2 Read CSV file from S3
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj['Body'].read().decode('utf-8', errors='ignore')
    csv_reader = csv.DictReader(io.StringIO(body))

    MAX_ROWS = 200  # 🔸 process first 200 reviews per execution
    processed_count = 0

    # 3 Iterate through CSV rows
    for i, row in enumerate(csv_reader, start=1):
        if i > MAX_ROWS:
            print(f"Reached {MAX_ROWS} rows. Stopping batch to prevent timeout.")
            break

        review_id = str(i)
        product_id = row.get('Clothing ID', '').strip()
        review_txt = (row.get('Review Text') or '').strip()
        rating = int(row['Rating']) if row.get('Rating') else 0

        # Skip empty or invalid reviews
        if not review_txt:
            print(f"Skipping empty review at row {i}")
            continue

        try:
            # 4 Run Comprehend analysis
            sent_res = comprehend.detect_sentiment(Text=review_txt, LanguageCode='en')
            key_phrases = comprehend.detect_key_phrases(Text=review_txt, LanguageCode='en')['KeyPhrases']
            entities = comprehend.detect_entities(Text=review_txt, LanguageCode='en')['Entities']

            sentiment = sent_res['Sentiment']
            scores = sent_res['SentimentScore']
            pos, neg, neu = float(scores['Positive']), float(scores['Negative']), float(scores['Neutral'])

            # 5 Derive emotion and satisfaction index
            emotion = derive_emotion(sentiment, pos, neg, rating)
            sat_index = max(0, min(100, int((pos - neg) * 100)))

            # 6 Store in DynamoDB
            table.put_item(
                Item={
                    'ReviewID': review_id,
                    'ProductID': product_id,
                    'ReviewText': review_txt,
                    'Rating': rating,
                    'SentimentLabel': sentiment,
                    'SentimentScorePositive': Decimal(str(pos)),
                    'SentimentScoreNegative': Decimal(str(neg)),
                    'SentimentScoreNeutral': Decimal(str(neu)),
                    'EmotionLabel': emotion,
                    'SatisfactionIndex': sat_index,
                    'KeyPhrases': [kp['Text'] for kp in key_phrases],
                    'Entities': [en['Text'] for en in entities]
                }
            )

            processed_count += 1
            if processed_count % 25 == 0:
                print(f"Processed {processed_count} reviews so far...")

        except Exception as e:
            print(f"Error processing row {i}: {e}")
            continue

    print(f" Completed batch. Total reviews processed: {processed_count}")
    return {
        'status': 'Batch completed',
        'processed': processed_count,
        'file': key
    }

# 7 Emotion derivation helper
def derive_emotion(sentiment, pos, neg, rating):
    if sentiment == 'POSITIVE' and pos >= 0.75:
        return 'Happy'
    if sentiment == 'NEGATIVE' and neg >= 0.75:
        return 'Angry' if rating <= 2 else 'Disappointed'
    if sentiment == 'NEUTRAL':
        return 'Neutral'
    return 'Mixed'
