# 🚀 LexiGlow Backend - Quick Start Guide

Get the LexiGlow backend running in 5 minutes!

## Prerequisites
- Docker and Docker Compose installed
- Python 3.13.7 (via pyenv)

## ⚡ 5-Minute Setup

### 1. Clone and Setup
```bash
git clone <repository-url>
cd lexiglow-backend
```

### 2. Start MongoDB
```bash
docker compose up -d
```

### 3. Setup Python Environment
```bash
pyenv install 3.13.7
pyenv local 3.13.7
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run Flask App
```bash
python wsgi.py
```

### 5. Test Everything Works
```bash
# Health check
curl http://localhost:5000/health

# Database test
curl http://localhost:5000/about/db-test

# API documentation
open http://localhost:5000/ui
```

## 🎯 What You Get

- **Flask API**: http://localhost:5000
- **MongoDB**: localhost:27017
- **Mongo Express**: http://localhost:8081 (admin/admin123)
- **API Docs**: http://localhost:5000/ui

## 🛠️ Essential Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Connect to MongoDB
docker compose exec mongodb mongosh -u lexiglow_user -p lexiglow_password --authenticationDatabase lexiglow
```

## 🆘 Need Help?

- **Full Documentation**: See [README.md](README.md)
- **Docker Details**: See [docker/README.md](docker/README.md)
- **Issues**: Check the troubleshooting section in docker/README.md

## 🎉 You're Ready!

Your LexiGlow backend is now running with MongoDB! Start building your application.
