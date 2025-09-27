#!/bin/bash

# MongoDB Docker Management Script for LexiGlow

case "$1" in
    start)
        echo "Starting MongoDB containers..."
        docker start lexiglow-mongodb lexiglow-mongo-express
        echo "MongoDB is running on port 27017"
        echo "Mongo Express is running on port 8081"
        echo "Access Mongo Express at: http://localhost:8081"
        echo "Username: admin, Password: admin123"
        ;;
    stop)
        echo "Stopping MongoDB containers..."
        docker stop lexiglow-mongodb lexiglow-mongo-express
        echo "MongoDB containers stopped"
        ;;
    restart)
        echo "Restarting MongoDB containers..."
        docker restart lexiglow-mongodb lexiglow-mongo-express
        echo "MongoDB containers restarted"
        ;;
    status)
        echo "MongoDB Container Status:"
        docker ps --filter name=lexiglow-mongodb
        echo ""
        echo "Mongo Express Container Status:"
        docker ps --filter name=lexiglow-mongo-express
        ;;
    logs)
        echo "MongoDB logs:"
        docker logs lexiglow-mongodb
        ;;
    connect)
        echo "Connecting to MongoDB..."
        docker exec -it lexiglow-mongodb mongosh --username lexiglow_user --password lexiglow_password --authenticationDatabase lexiglow
        ;;
    admin)
        echo "Connecting to MongoDB as admin..."
        docker exec -it lexiglow-mongodb mongosh --username admin --password password123 --authenticationDatabase admin
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|connect|admin}"
        echo ""
        echo "Commands:"
        echo "  start   - Start MongoDB containers"
        echo "  stop    - Stop MongoDB containers"
        echo "  restart - Restart MongoDB containers"
        echo "  status  - Show container status"
        echo "  logs    - Show MongoDB logs"
        echo "  connect - Connect to MongoDB as lexiglow_user"
        echo "  admin   - Connect to MongoDB as admin"
        exit 1
        ;;
esac
