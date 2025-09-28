# Docker Setup for LexiGlow Backend

This directory contains Docker-related files and configurations for the LexiGlow backend project.

## 📁 Directory Structure

```
docker/
└── mongo-init/
    └── 01-init-database.js    # MongoDB initialization script
```

## 🚀 Quick Start

### 1. Start MongoDB Services
```bash
# From project root
docker compose up -d
```

### 2. Run Flask Application
```bash
# Install Python dependencies
pyenv install 3.13.7
pyenv local 3.13.7
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start Flask app
python wsgi.py
```

### 3. Verify Setup
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test database connection
curl http://localhost:5000/about/db-test
```

## 🐳 Docker Services

### MongoDB Service
- **Image**: mongo:7.0
- **Port**: 27017
- **Database**: lexiglow
- **Admin User**: admin / password123
- **App User**: lexiglow_user / lexiglow_password

### Mongo Express (Web UI)
- **Image**: mongo-express:1.0.2
- **Port**: 8081
- **URL**: http://localhost:8081
- **Credentials**: admin / admin123

## 📋 Docker Compose Commands

### Basic Operations
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart services
docker compose restart

# View service status
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs mongodb
docker compose logs mongo-express
```

### Database Operations
```bash
# Connect to MongoDB as application user
docker compose exec mongodb mongosh -u lexiglow_user -p lexiglow_password --authenticationDatabase lexiglow

# Connect to MongoDB as admin
docker compose exec mongodb mongosh -u admin -p password123 --authenticationDatabase admin

# Access Mongo Express web interface
open http://localhost:8081
```

### Development Commands
```bash
# Rebuild containers
docker compose up -d --build

# Remove containers and volumes (clean slate)
docker compose down -v

# View container resource usage
docker compose top
```

## 🔧 Configuration

### Environment Variables
All configuration is managed through the `.env` file in the project root:

```env
# MongoDB Configuration
MONGO_URI=mongodb://lexiglow_user:lexiglow_password@localhost:27017/lexiglow
MONGO_ADMIN_USERNAME=admin
MONGO_ADMIN_PASSWORD=password123
MONGO_APP_USERNAME=lexiglow_user
MONGO_APP_PASSWORD=lexiglow_password

# Docker MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password123
MONGO_INITDB_DATABASE=lexiglow
```

### MongoDB Initialization
The `mongo-init/01-init-database.js` script runs when MongoDB starts for the first time and:
- Creates the `lexiglow` database
- Creates the application user with read/write permissions
- Sets up initial collections with validation
- Creates indexes for better performance

## 🐛 Troubleshooting

### Common Issues

#### MongoDB Connection Failed
```bash
# Check if MongoDB is running
docker compose ps

# Check MongoDB logs
docker compose logs mongodb

# Restart MongoDB
docker compose restart mongodb
```

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :27017
lsof -i :8081

# Stop conflicting services or change ports in docker-compose.yml
```

#### Permission Issues
```bash
# Ensure Docker has proper permissions
sudo usermod -aG docker $USER
# Then logout and login again
```

### Reset Everything
```bash
# Stop and remove all containers and volumes
docker compose down -v

# Remove any orphaned containers
docker system prune -f

# Start fresh
docker compose up -d
```

## 📊 Monitoring

### Health Checks
```bash
# Check service health
curl http://localhost:5000/health
curl http://localhost:5000/about/db-test

# Check container health
docker compose ps
```

### Logs
```bash
# Follow all logs
docker compose logs -f

# Follow specific service logs
docker compose logs -f mongodb
docker compose logs -f mongo-express
```

## 🔒 Security Notes

- Default credentials are for development only
- Change passwords in production
- Use environment-specific `.env` files
- Never commit `.env` files to version control
- Consider using Docker secrets for production

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB Docker Image](https://hub.docker.com/_/mongo)
- [Mongo Express Documentation](https://github.com/mongo-express/mongo-express)
