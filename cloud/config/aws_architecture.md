# KrishiMind SustainAI - AWS Architecture

## Overview

KrishiMind SustainAI is deployed on AWS using a serverless-first architecture optimized for:
- **Cost efficiency** — Pay-per-request pricing
- **Scalability** — Auto-scaling with demand
- **Low latency** — Edge-optimized API Gateway
- **Security** — IAM least privilege, VPC isolation

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS CLOUD                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐        │
│    │   Route 53  │────────▶│ CloudFront  │────────▶│ API Gateway │        │
│    │    (DNS)    │         │    (CDN)    │         │   (REST)    │        │
│    └─────────────┘         └─────────────┘         └──────┬──────┘        │
│                                                           │                 │
│                                                           ▼                 │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                        AWS Lambda                                │     │
│    │  ┌─────────────────────────────────────────────────────────┐   │     │
│    │  │                  KrishiMind API                          │   │     │
│    │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │   │     │
│    │  │  │ FastAPI  │─▶│ Mangum   │─▶│ Predict  │─▶│ Response│ │   │     │
│    │  │  │  Router  │  │ Adapter  │  │  Logic   │  │  JSON   │ │   │     │
│    │  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │   │     │
│    │  └─────────────────────────────────────────────────────────┘   │     │
│    └───────────────────────────────┬─────────────────────────────────┘     │
│                                    │                                        │
│                                    ▼                                        │
│    ┌───────────────────────────────────────────────────────────────────┐   │
│    │                           Amazon S3                                │   │
│    │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐      │   │
│    │  │ models/        │  │ artifacts/     │  │ data/          │      │   │
│    │  │ yield_model.pkl│  │ yield_features │  │ (raw datasets) │      │   │
│    │  │ price_model.pkl│  │ price_features │  │                │      │   │
│    │  └────────────────┘  └────────────────┘  └────────────────┘      │   │
│    └───────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                   Batch Processing (Optional)                    │     │
│    │  ┌──────────────────┐         ┌──────────────────┐             │     │
│    │  │    SageMaker     │◀───────▶│    Step Functions│             │     │
│    │  │   Batch Transform│         │   (Orchestration) │             │     │
│    │  └──────────────────┘         └──────────────────┘             │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                       Monitoring & Security                      │     │
│    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │     │
│    │  │  CloudWatch  │  │     IAM      │  │   Secrets    │          │     │
│    │  │    Logs      │  │   Roles      │  │   Manager    │          │     │
│    │  └──────────────┘  └──────────────┘  └──────────────┘          │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Amazon S3 — Model & Data Storage

**Bucket Structure:**
```
s3://krishimind-ai-prod/
├── models/
│   ├── yield_model.pkl      # 11.8 MB
│   └── price_model.pkl      # 1.0 MB
├── artifacts/
│   ├── yield_features.json  # 15 KB
│   └── price_features.json  # 1 KB
├── reports/
│   └── model_metrics.json   # 1 KB
└── data/
    └── (raw CSVs - archived)
```

**Configuration:**
- Versioning: Enabled
- Encryption: AES-256 (SSE-S3)
- Lifecycle: 90-day transition to Glacier for data/
- Cross-region replication: Optional

### 2. AWS Lambda — Real-Time Inference

**Function Configuration:**
| Setting | Value |
|---------|-------|
| Runtime | Python 3.9 |
| Memory | 1024 MB |
| Timeout | 30 seconds |
| Ephemeral Storage | 512 MB |
| Concurrency | 100 (reserved) |

**Cold Start Optimization:**
- Provisioned concurrency: 5 instances
- Model loading at initialization (outside handler)
- Lambda Layers for dependencies

**Environment Variables:**
```
MODEL_BUCKET=krishimind-ai-prod
LOG_LEVEL=INFO
```

### 3. Amazon API Gateway — REST API

**Endpoint:**
```
https://api.krishimind.ai/v1/predict/crop-plan
```

**Configuration:**
- Type: REST API (Regional)
- Stage: prod
- Throttling: 1000 requests/second
- Burst: 2000 requests
- API Key: Required for production

**Request Validation:**
- JSON Schema validation enabled
- Required headers: Content-Type, X-API-Key

### 4. Amazon SageMaker — Batch Inference

**Use Case:** Bulk predictions for district-wide planning

**Endpoint Configuration:**
| Setting | Value |
|---------|-------|
| Instance Type | ml.m5.large |
| Instance Count | 1 |
| Model Data | s3://krishimind-ai-prod/models/ |

**Batch Transform Job:**
```python
sagemaker.transformer.Transformer(
    model_name='krishimind-yield-model',
    instance_count=1,
    instance_type='ml.m5.large',
    output_path='s3://krishimind-ai-prod/predictions/'
)
```

### 5. Amazon CloudWatch — Monitoring

**Metrics Tracked:**
- Lambda invocations, errors, duration
- API Gateway 4xx/5xx errors
- S3 request counts
- Custom: prediction_count, avg_response_time

**Alarms:**
| Alarm | Threshold | Action |
|-------|-----------|--------|
| Lambda Errors | > 5% | SNS Notification |
| API 5xx | > 1% | SNS Notification |
| Response Time | > 5s p95 | SNS Notification |

**Log Groups:**
```
/aws/lambda/krishimind-api
/aws/api-gateway/krishimind-api
/aws/sagemaker/endpoints/krishimind-endpoint
```

### 6. IAM — Least Privilege

**Lambda Execution Role:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::krishimind-ai-prod/models/*",
        "arn:aws:s3:::krishimind-ai-prod/artifacts/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

---

## Deployment Steps

### 1. Create S3 Bucket
```bash
aws s3 mb s3://krishimind-ai-prod --region ap-south-1
aws s3 cp models/ s3://krishimind-ai-prod/models/ --recursive
aws s3 cp artifacts/ s3://krishimind-ai-prod/artifacts/ --recursive
```

### 2. Create Lambda Layer
```bash
pip install -r requirements.txt -t python/
zip -r layer.zip python/
aws lambda publish-layer-version \
    --layer-name krishimind-deps \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.9
```

### 3. Deploy Lambda Function
```bash
cd cloud/lambda
zip -r function.zip handler.py ../api/
aws lambda create-function \
    --function-name krishimind-api \
    --runtime python3.9 \
    --handler handler.handler \
    --role arn:aws:iam::ACCOUNT:role/krishimind-lambda-role \
    --zip-file fileb://function.zip \
    --memory-size 1024 \
    --timeout 30 \
    --layers arn:aws:lambda:REGION:ACCOUNT:layer:krishimind-deps:1
```

### 4. Create API Gateway
```bash
aws apigateway create-rest-api \
    --name "KrishiMind API" \
    --endpoint-configuration types=REGIONAL
```

---

## Cost Estimation (Monthly)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 1M requests, 500ms avg | $3.00 |
| API Gateway | 1M requests | $3.50 |
| S3 | 50 GB storage | $1.15 |
| CloudWatch | 10 GB logs | $5.00 |
| **Total** | | **~$12.65/month** |

*Based on ap-south-1 pricing, actual costs may vary.*

---

## Security Checklist

- [ ] S3 bucket policy restricts public access
- [ ] Lambda function in VPC (optional)
- [ ] API Gateway with API key required
- [ ] CloudWatch logs encrypted
- [ ] IAM roles follow least privilege
- [ ] No secrets in code or environment variables
- [ ] HTTPS only (TLS 1.2+)

---

## Disaster Recovery

**RTO:** 15 minutes  
**RPO:** 24 hours

**Strategy:**
1. S3 versioning for model rollback
2. Lambda aliases for blue-green deployment
3. Multi-AZ by default (Lambda, API Gateway)
4. Cross-region replication (optional)
