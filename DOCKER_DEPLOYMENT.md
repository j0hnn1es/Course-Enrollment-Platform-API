# Docker Deployment Guide

## Local Development with Docker

### Prerequisites
- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (comes with Docker Desktop)

### Quick Start

1. **Clone and navigate to the project:**
```bash
cd "Course Enrollment Platform API"
```

2. **Copy environment file:**
```bash
cp .env.example .env
```

3. **Build and run with Docker Compose:**
```bash
docker-compose up -d
```

4. **Access the application:**
- API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

5. **View logs:**
```bash
docker-compose logs -f web
```

6. **Stop the application:**
```bash
docker-compose down
```

## Building the Docker Image

### Build for production:
```bash
docker build -t course-enrollment-api:latest .
```

### Run the image standalone:
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@db_host:5432/course_db" \
  -e SECRET_KEY="your-secret-key" \
  course-enrollment-api:latest
```

## Cloud Deployment Options

### AWS ECS
1. Tag your image: `docker tag course-enrollment-api:latest <your-ecr-uri>:latest`
2. Push to ECR registry
3. Create ECS task definition
4. Set DATABASE_URL and SECRET_KEY as environment variables
5. Create RDS PostgreSQL instance and link to ECS service

### Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/<project-id>/course-enrollment-api
gcloud run deploy course-enrollment-api \
  --image gcr.io/<project-id>/course-enrollment-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=<cloud-sql-connection-string>,SECRET_KEY=<your-key>
```

### Azure Container Instances
```bash
az acr build --registry <registry-name> --image course-enrollment-api:latest .
az container create \
  --resource-group <group> \
  --name course-enrollment-api \
  --image <registry-name>.azurecr.io/course-enrollment-api:latest \
  --environment-variables DATABASE_URL=<connection-string> SECRET_KEY=<key>
```

### Heroku (using Container Registry)
```bash
heroku container:login
docker tag course-enrollment-api:latest registry.heroku.com/<app-name>/web
docker push registry.heroku.com/<app-name>/web
heroku container:release web -a <app-name>
```

## Environment Variables

Set these in your cloud provider's secrets/environment configuration:

- `DATABASE_URL`: Full PostgreSQL connection string
- `SECRET_KEY`: Strong secret key for JWT tokens (change from default!)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiry time (default: 60)

## Database Migrations

### Run migrations in Docker:
```bash
docker-compose exec web alembic upgrade head
```

### Create new migration:
```bash
docker-compose exec web alembic revision --autogenerate -m "Description"
```

## Testing

### Run tests in Docker:
```bash
docker-compose exec web pytest
```

### Run tests with coverage:
```bash
docker-compose exec web pytest --cov=app
```

## Troubleshooting

### Database connection issues
- Ensure `DATABASE_URL` is correct and includes the host (use service name `db` for docker-compose)
- Check PostgreSQL container is healthy: `docker-compose ps`

### Port conflicts
- Change ports in docker-compose.yml if 8000 or 5432 are in use
- Update Dockerfile EXPOSE if changing the application port

### Rebuilding after changes
```bash
docker-compose up --build
```

## Production Checklist

- [ ] Change `SECRET_KEY` to a strong random string
- [ ] Use a managed database service (RDS, Cloud SQL, Azure Database)
- [ ] Set up proper logging and monitoring
- [ ] Configure CORS for your frontend domain
- [ ] Enable HTTPS/SSL
- [ ] Set up automated backups for database
- [ ] Configure health checks and auto-restart policies
- [ ] Review and update dependencies regularly
