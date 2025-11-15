SentimentScope – Serverless Review Sentiment Processing Pipeline

A Real-Time Serverless Data Processing & Visualization System using AWS Lambda, DynamoDB, S3 & QuickSight

📌 Overview

SentimentScope is a serverless application built using AWS services to automatically analyze customer product reviews and extract meaningful insights.
The system processes raw review data, extracts emotional signals, aggregates product-level metrics, and visualizes them in Amazon QuickSight dashboards.

This project demonstrates:

Scalable data processing

Event-driven automation

DynamoDB-backed storage

End-to-end insight generation through QuickSight

🚀 Architecture

✔ Architecture Components
Component	Purpose
Amazon S3	Stores uploaded raw CSV review files
AWS Lambda – Ingest	Parses each review, classifies sentiments, extracts themes
Amazon DynamoDB	Stores processed review-level data
AWS Lambda – Aggregate	Generates emotion counts & satisfaction metrics
Amazon QuickSight	Builds dashboards for visualization
S3 Event Trigger	Automatically invokes the ingest Lambda on file upload
📂 Repository Structure
sentiment-scope/
│
├── lambda/
│   ├── ingest_lambda.py
│   └── aggregate_lambda.py
│
├── data/
│   ├── sample_reviews.csv
│   └── aggregated_output.csv
│
├── architecture/
│   └── architecture_diagram.png
│
├── docs/
│   ├── QuickSight_Visuals.pdf
│   └── Screenshots/
│
└── README.md


✔ This repository intentionally does NOT include project reports or internal documentation PDFs.

🧠 Key Features
🔹 Automated Review Processing

Upload CSV → Lambda auto-triggered

Extracts keywords, sentiments, and themes

Writes processed data into DynamoDB

🔹 Sentiment Classification

😀 Happy

😡 Angry

😞 Disappointed

😐 Neutral

🔹 Product-Level Metrics

Emotion counts

Average satisfaction index

Top positive & negative themes

Last updated timestamp

🔹 QuickSight Visualizations

(Located in docs/QuickSight_Visuals.pdf)

Includes charts for:

Emotion distribution

Product comparison

Trend analysis

KPI cards

Theme frequencies

💻 Lambda Functions Overview
/lambda/ingest_lambda.py

Triggered when a CSV file is uploaded

Reads raw review rows

Extracts sentiment & keywords

Stores review-level data in DynamoDB

/lambda/aggregate_lambda.py

Scans DynamoDB

Aggregates results at product level

Calculates satisfaction metrics

Exports aggregated output

🧪 Data Samples
/data/sample_reviews.csv

A small sample dataset used for:

Testing

Debugging

Demo / walkthrough

/data/aggregated_output.csv

Output after running the aggregation Lambda (exported from DynamoDB).

📊 Dashboard Visuals

Located under:

docs/QuickSight_Visuals.pdf

docs/Screenshots/

Shows:

Emotion distribution

Satisfaction KPIs

Product sentiment comparison

Trends over time

🔮 Future Enhancements

Integrate Amazon Comprehend for NLP

Build user-level dashboards

Real-time streaming with AWS Kinesis

Alerts for low satisfaction scores
