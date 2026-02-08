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

## Push to Container Registry (Optional)

```bash
# Tag image for your registry
docker tag krishimind-ai:latest YOUR_REGISTRY/krishimind-ai:latest

# Push
docker push YOUR_REGISTRY/krishimind-ai:latest
```

> Any container registry (Docker Hub, GitHub Container Registry, or cloud-specific) can be used. No specific cloud provider is required.
