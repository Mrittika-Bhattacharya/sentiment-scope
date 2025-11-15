import boto3
from collections import defaultdict, Counter
from datetime import datetime
from decimal import Decimal
import csv
import io

# --- DynamoDB setup ---
dynamodb = boto3.resource('dynamodb')
reviews_table = dynamodb.Table('SentimentScopeReviews')
agg_table = dynamodb.Table('SentimentScopeAggregated')

# --- S3 setup ---
s3 = boto3.client('s3')
BUCKET = 'sentiment-scope-mrittika-ap-south-1'
OUTPUT_KEY = 'processed/aggregated/latest/aggregated_metrics.csv'

def lambda_handler(event, context):
    # 1 Read all reviews (paginate if large)
    items, response = [], reviews_table.scan()
    items.extend(response.get('Items', []))
    while 'LastEvaluatedKey' in response:
        response = reviews_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    # 2 Group by ProductID
    grouped = defaultdict(list)
    for item in items:
        grouped[item.get('ProductID', 'Unknown')].append(item)

    # 3 Prepare to write CSV
    headers = [
        'ProductID','AverageSatisfactionIndex',
        'HappyCount','AngryCount','DisappointedCount','NeutralCount',
        'TopPositiveThemes','TopNegativeThemes','LastUpdatedTimestamp'
    ]
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=headers)
    writer.writeheader()

    # 4 Aggregate and update DDB + collect CSV rows
    for pid, reviews in grouped.items():
        sat_scores = []
        counts = Counter({'Happy':0,'Angry':0,'Disappointed':0,'Neutral':0})
        pos_phrases, neg_phrases = [], []

        for r in reviews:
            try:
                sat_scores.append(Decimal(str(r.get('SatisfactionIndex', 0))))
            except:
                sat_scores.append(Decimal('0'))

            emotion = r.get('EmotionLabel', 'Neutral')
            if emotion in counts:
                counts[emotion] += 1

            for kp in r.get('KeyPhrases', []):
                phrase = str(kp.get('S', kp)) if isinstance(kp, dict) else str(kp)
                if r.get('SentimentLabel') == 'POSITIVE':
                    pos_phrases.append(phrase)
                elif r.get('SentimentLabel') == 'NEGATIVE':
                    neg_phrases.append(phrase)

        avg_sat = (sum(sat_scores) / Decimal(len(sat_scores))) if sat_scores else Decimal('0')
        top_pos = list(dict.fromkeys(pos_phrases))[:3]
        top_neg = list(dict.fromkeys(neg_phrases))[:3]
        ts = datetime.utcnow().isoformat()

        # --- Write back to aggregated table ---
        agg_table.put_item(Item={
            'ProductID': pid,
            'AverageSatisfactionIndex': avg_sat,
            'HappyCount': Decimal(counts['Happy']),
            'AngryCount': Decimal(counts['Angry']),
            'DisappointedCount': Decimal(counts['Disappointed']),
            'NeutralCount': Decimal(counts['Neutral']),
            'TopPositiveThemes': top_pos,
            'TopNegativeThemes': top_neg,
            'LastUpdatedTimestamp': ts
        })

        # --- Append to CSV ---
        writer.writerow({
            'ProductID': pid,
            'AverageSatisfactionIndex': float(avg_sat),
            'HappyCount': counts['Happy'],
            'AngryCount': counts['Angry'],
            'DisappointedCount': counts['Disappointed'],
            'NeutralCount': counts['Neutral'],
            'TopPositiveThemes': '|'.join(top_pos),
            'TopNegativeThemes': '|'.join(top_neg),
            'LastUpdatedTimestamp': ts
        })

    # 5 Upload CSV to S3
    csv_data = csv_buffer.getvalue().encode('utf-8')
    s3.put_object(
        Bucket=BUCKET,
        Key=OUTPUT_KEY,
        Body=csv_data,
        ContentType='text/csv'
    )

    return {
        'status': 'Aggregation complete',
        'products': len(grouped),
        's3_output': f's3://{BUCKET}/{OUTPUT_KEY}'
    }
