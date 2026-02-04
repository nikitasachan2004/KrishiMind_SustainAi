# Docker Build Instructions

## Build Image

```bash
# From project root
docker build -t krishimind-ai:latest -f docker/Dockerfile .
```

## Run Container

```bash
# Run in foreground
docker run -p 8000:8000 krishimind-ai:latest

# Run in background
docker run -d -p 8000:8000 --name krishimind krishimind-ai:latest
```

## Docker Compose (Development)

```bash
cd docker
docker-compose up -d
```

## Test the API

```bash
curl -X POST http://localhost:8000/predict/crop-plan \
  -H "Content-Type: application/json" \
  -d '{"district": "Guntur", "season": "Kharif", "area": 10.0}'
```

## View Logs

```bash
docker logs -f krishimind
```

## Stop Container

```bash
docker stop krishimind
docker rm krishimind
```

## Push to ECR (AWS)

```bash
# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com

# Tag image
docker tag krishimind-ai:latest ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com/krishimind-ai:latest

# Push
docker push ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com/krishimind-ai:latest
```
