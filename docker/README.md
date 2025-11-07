# Docker Setup for LexiGlow Backend

This directory contains Docker-related files and configurations for the LexiGlow backend project.

## 📁 Directory Structure

```
docker/
├── docker-compose.yml
├── README.md
└── mongo-init/
    ├── 01-mongodb-init.js    # MongoDB initialization script
    └── 02-seed-data.js       # MongoDB seed data script
```

## 🚀 Quick Start

### 1. Start MongoDB Services
```bash
# From project root
docker compose --env-file .env -f docker/docker-compose.yml up -d
```

### 2. Verify Setup
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
- **Database**: Configured via `MONGO_INITDB_DATABASE` in `.env`
- **Admin User**: Configured via `MONGO_INITDB_ROOT_USERNAME` in `.env`
- **Admin Password**: Configured via `MONGO_INITDB_ROOT_PASSWORD` in `.env`

### Mongo Express (Web UI)
- **Image**: mongo-express:1.0.2
- **Port**: 8081
- **URL**: http://localhost:8081
- **Credentials**: Configured via `ME_CONFIG_BASICAUTH_USERNAME` and `ME_CONFIG_BASICAUTH_PASSWORD` in `.env`

## 📋 Docker Compose Commands

### Basic Operations
```bash
# Start all services
docker compose --env-file .env -f docker/docker-compose.yml up -d

# Stop all services
docker compose --env-file .env -f docker/docker-compose.yml down

# Restart services
docker compose --env-file .env -f docker/docker-compose.yml restart

# View service status
docker compose --env-file .env -f docker/docker-compose.yml ps

# View logs
docker compose --env-file .env -f docker/docker-compose.yml logs -f

# View specific service logs
docker compose --env-file .env -f docker/docker-compose.yml logs mongodb
docker compose --env-file .env -f docker/docker-compose.yml logs mongo-express
```

### Database Operations
```bash
# Connect to MongoDB as application user (replace with your .env values)
docker compose --env-file .env -f docker/docker-compose.yml exec mongodb mongosh -u $MONGO_APP_USERNAME -p $MONGO_APP_PASSWORD --authenticationDatabase $MONGO_INITDB_DATABASE

# Connect to MongoDB as admin (replace with your .env values)
docker compose --env-file .env -f docker/docker-compose.yml exec mongodb mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin

# Access Mongo Express web interface
open http://localhost:8081
```

### Development Commands
```bash
# Rebuild containers
docker compose --env-file .env -f docker/docker-compose.yml up -d --build

# Remove containers and volumes (clean slate)
docker compose --env-file .env -f docker/docker-compose.yml down -v

# View container resource usage
docker compose --env-file .env -f docker/docker-compose.yml top
```

## 🔧 Configuration

### Environment Variables
All configuration is managed through the `.env` file in the project root. Ensure the following variables are set:

```env
# MongoDB Configuration
MONGO_URI=mongodb://lexiglow_user:lexiglow_password@localhost:27017/lexiglow
MONGO_ADMIN_USERNAME=admin
MONGO_ADMIN_PASSWORD=password123
MONGO_APP_USERNAME=lexiglow_user
MONGO_APP_PASSWORD=lexiglow_password

# Docker MongoDB Configuration (used by docker-compose.yml)
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password123
MONGO_INITDB_DATABASE=lexiglow

# Mongo Express Configuration (used by docker-compose.yml)
ME_CONFIG_BASICAUTH_USERNAME=admin
ME_CONFIG_BASICAUTH_PASSWORD=admin123
```

### MongoDB Initialization
The `mongo-init/01-mongodb-init.js` and `mongo-init/02-seed-data.js` scripts run when MongoDB starts for the first time.
- `01-mongodb-init.js`: Creates the `lexiglow` database, creates the application user with read/write permissions, sets up initial collections with validation, and creates indexes for better performance.
- `02-seed-data.js`: Seeds the database with initial data.

## 🐛 Troubleshooting

### Common Issues

#### MongoDB Connection Failed
```bash
# Check if MongoDB is running
docker compose --env-file .env -f docker/docker-compose.yml ps

# Check MongoDB logs
docker compose --env-file .env -f docker/docker-compose.yml logs mongodb

# Restart MongoDB
docker compose --env-file .env -f docker/docker-compose.yml restart mongodb
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
docker compose --env-file .env -f docker/docker-compose.yml down -v

# Remove any orphaned containers
docker system prune -f

# Start fresh
docker compose --env-file .env -f docker/docker-compose.yml up -d
```

## 📊 Monitoring

### Health Checks
```bash
# Check service health
curl http://localhost:5000/health
curl http://localhost:5000/about/db-test

# Check container health
docker compose --env-file .env -f docker/docker-compose.yml ps
```

### Logs
```bash
# Follow all logs
docker compose --env-file .env -f docker/docker-compose.yml logs -f

# Follow specific service logs
docker compose --env-file .env -f docker/docker-compose.yml logs -f mongodb
docker compose --env-file .env -f docker/docker-compose.yml logs -f mongo-express
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