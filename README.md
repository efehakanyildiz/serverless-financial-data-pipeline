# 🚀 Serverless Event-Driven Financial Data Pipeline (Medallion Architecture)

## 📌 Project Overview
This project is a fully automated, serverless data pipeline built on AWS. It fetches real-time financial data from Wall Street, processes it using a decoupled event-driven architecture, and implements a cost-optimized **Medallion Data Lakehouse** (Bronze to Silver) strategy alongside real-time NoSQL storage.

The system is designed with **FinOps principles**, bypassing expensive ETL tools (like AWS Glue) in favor of zero-cost, serverless SQL transformations using Amazon Athena.

## 🏗️ Architecture Diagram
yfinance_diagram.png
*(The pipeline orchestrates multiple AWS microservices to ensure fault tolerance, scalability, and zero data loss.)*

## ✨ Key Features & Engineering Decisions

* **Decoupled Ingestion:** API data is not written directly to databases. Instead, AWS Lambda pushes raw data to an **Amazon SQS** queue, preventing data loss during database downtimes and ensuring high availability.
* **Dual-Storage Strategy:** A processor Lambda function consumes the SQS queue and performs concurrent writes:
  * **Amazon DynamoDB:** For low-latency, real-time application access.
  * **Amazon S3 (Bronze Layer):** For historical raw data storage (NDJSON format).
* **Cost-Optimized ETL (Medallion Architecture):** Instead of provisioning costly PySpark/AWS Glue clusters for small data batches, the pipeline uses **Amazon Athena (CTAS/INSERT)** to transform raw JSON into highly compressed, columnar **Parquet** format (Silver Layer), reducing query costs by 80%.
* **Dual-Layer Monitoring & Smart Alerts:** * **System Health:** AWS Step Functions triggers an **Amazon SNS** notification upon successful pipeline execution.
  * **Business Logic (Volatility Alert):** The Lambda processor calculates real-time price changes. If a stock fluctuates by more than **15%**, it dynamically triggers a critical SNS alert to stakeholders.
* **100% Serverless & Automated:** The entire workflow is orchestrated via **AWS Step Functions** and scheduled by **Amazon EventBridge** to run autonomously.

## 🛠️ Technology Stack
* **Cloud Provider:** Amazon Web Services (AWS)
* **Compute & Orchestration:** AWS Lambda, Step Functions, EventBridge
* **Messaging & Queues:** Amazon SQS, Amazon SNS
* **Database & Storage:** Amazon DynamoDB, Amazon S3
* **Analytics & ETL:** Amazon Athena, SQL, Parquet
* **Languages & Libraries:** Python (boto3, pandas, yfinance)

## 🚀 How It Works
1. **EventBridge** triggers the State Machine (Step Functions) every hour.
2. **Lambda (Fetcher)** pulls live stock data and sends it to **SQS**.
3. **Lambda (Processor)** reads from SQS, checks the previous price in **DynamoDB**, and triggers an **SNS** alert if volatility > 15%.
4. Data is saved to **DynamoDB** (latest state) and **S3 Bronze Bucket** (raw history).
5. **Athena** automatically cleans, transforms, and compresses the new data into Parquet format, moving it to the **S3 Silver Bucket**.

---
*Developed by **Efe Hakan Yıldız***
