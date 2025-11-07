# App Directory Structure

This directory contains the core application code organized using **Clean Architecture** principles. The structure separates concerns into distinct layers, ensuring maintainability, testability, and scalability.

## 📁 Directory Overview

```
app/
├── core/              # Application-wide configuration and infrastructure
├── domain/            # Business logic and domain models
├── infrastructure/   # External system integrations (databases, APIs)
├── application/       # Application services and use cases
├── presentation/      # API layer (controllers, schemas, routes)
├── __init__.py        # Application factory
└── main.py            # Application entry point
```

## 🏗️ Layer Descriptions

### 1. **`core/`** - Core Infrastructure

Contains application-wide configurations, cross-cutting concerns, and foundational services.

**Components:**
- **`config.py`**: Application configuration management
- **`container.py`**: Dependency Injection (DI) container for managing dependencies
- **`dependencies.py`**: Dependency injection helpers and resolvers
- **`logging_config.py`**: Centralized logging configuration

**Responsibilities:**
- Dependency injection and service lifecycle management
- Logging configuration and setup
- Application-wide configuration
- Cross-cutting concerns

**Key Features:**
- Singleton pattern for repositories and services
- Dependency override support for testing
- Centralized logging with file and console handlers

---

### 2. **`domain/`** - Domain Layer

Contains the core business logic, entities, and interfaces. This layer is independent of external frameworks and infrastructure.

**Subdirectories:**

#### **`entities/`** - Domain Entities
Pydantic models representing business entities:
- `user.py`: User and UserLanguage entities
- `language.py`: Language entity
- `text.py`: Text, TextTag, and TextTagAssociation entities
- `vocabulary.py`: UserVocabulary and UserVocabularyItem entities
- `enums.py`: Domain enumerations (e.g., ProficiencyLevel)
- `models.py`: Central export point for all entities

#### **`interfaces/`** - Repository Interfaces
Abstract interfaces defining contracts for data access:
- `base_repository.py`: Base repository interface with CRUD operations
- `user_repository.py`: User-specific repository interface
- `language_repository.py`: Language-specific repository interface
- `text_repository.py`: Text-specific repository interface

**Responsibilities:**
- Define business entities and their relationships
- Define repository contracts (interfaces)
- Enforce business rules and validations
- Maintain domain logic independence

**Key Features:**
- Pydantic models for validation and serialization
- Repository pattern for data access abstraction
- Domain-driven design principles

---

### 3. **`infrastructure/`** - Infrastructure Layer

Contains implementations of external systems and technical concerns.

**Subdirectories:**

#### **`database/`** - Database Implementations
Concrete implementations of repository interfaces for different databases:

- **`mongodb/`**: MongoDB repository implementations
  - `repositories/`: MongoDB-specific repository implementations
  - Handles UUID encoding/decoding with `uuidRepresentation="standard"`
  - Converts between MongoDB `_id` and entity `id` fields

- **`sqlite/`**: SQLite repository implementations
  - `repositories/`: SQLite-specific repository implementations
  - SQLAlchemy ORM models and database session management

**Responsibilities:**
- Implement repository interfaces for specific databases
- Handle database-specific concerns (UUID encoding, field mapping)
- Manage database connections and sessions
- Provide data persistence implementations

**Key Features:**
- Multiple database backend support (MongoDB, SQLite)
- Repository pattern implementation
- Database-agnostic domain layer

---

### 4. **`application/`** - Application Services Layer

Contains application services that orchestrate domain logic and coordinate between layers.

**Subdirectories:**

#### **`services/`** - Application Services
Business logic orchestration and use case implementation:
- `user_service.py`: User-related business operations

#### **`dto/`** - Data Transfer Objects
DTOs for data transfer between layers (if needed)

**Responsibilities:**
- Orchestrate domain logic
- Coordinate between repositories and domain entities
- Implement use cases and business workflows
- Handle application-level validations

**Key Features:**
- Service layer pattern
- Use case implementation
- Business logic orchestration

---

### 5. **`presentation/`** - Presentation Layer

Contains API definitions, request/response schemas, and route handlers.

**Subdirectories:**

#### **`api/`** - API Definitions
- `v1/`: Version 1 API endpoints
  - `spec/`: OpenAPI specification files
  - `controllers/`: API endpoint handlers

#### **`schemas/`** - Request/Response Schemas
Pydantic schemas for API request/response validation:
- Request schemas (e.g., `UserCreate`, `TextCreate`)
- Response schemas (e.g., `UserResponse`)

**Responsibilities:**
- Define API endpoints and contracts
- Handle HTTP requests and responses
- Validate input data
- Transform between API models and domain entities

**Key Features:**
- OpenAPI/Connexion integration
- Swagger UI documentation
- Request/response validation
- RESTful API design

---

## 🔄 Data Flow

```
Request → Presentation Layer (API/Schemas)
         ↓
    Application Layer (Services)
         ↓
    Domain Layer (Entities/Interfaces)
         ↓
    Infrastructure Layer (Repositories)
         ↓
    Database
```

**Flow Example:**
1. **Presentation**: API receives HTTP request, validates schema
2. **Application**: Service orchestrates business logic
3. **Domain**: Domain entities enforce business rules
4. **Infrastructure**: Repository persists/retrieves data
5. **Response**: Data flows back through layers

---

## 🔧 Key Files

### **`__init__.py`**
Application factory function that:
- Creates and configures the Connexion/Flask application
- Sets up OpenAPI/Swagger integration
- Configures CORS
- Initializes the dependency injection container

### **`main.py`**
Application entry point that:
- Creates the application instance
- Runs the development server

---

## 🎯 Design Principles

1. **Separation of Concerns**: Each layer has a distinct responsibility
2. **Dependency Inversion**: Domain layer doesn't depend on infrastructure
3. **Repository Pattern**: Abstract data access through interfaces
4. **Dependency Injection**: Centralized dependency management
5. **Clean Architecture**: Business logic independent of frameworks

---

## 📝 Usage Examples

### Accessing the DI Container
```python
from app.core.dependencies import get_container

container = get_container()
user_repository = container.get_user_repository()
```

### Using Domain Entities
```python
from app.domain.entities.user import User
from app.domain.entities.language import Language
```

### Using Repository Interfaces
```python
from app.domain.interfaces.user_repository import IUserRepository
```

### Using Application Services
```python
from app.application.services.user_service import UserService
```

---

## 🧪 Testing

The architecture supports easy testing through:
- **Interface-based design**: Mock repositories for unit tests
- **Dependency injection**: Override dependencies in tests
- **Layer isolation**: Test each layer independently

---

## 📚 Related Documentation

- [Main README.md](../README.md) - Project overview and setup
- [docker/README.md](../docker/README.md) - Docker setup

