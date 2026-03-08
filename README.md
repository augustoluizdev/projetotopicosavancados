# Event Management System

A Django-based event management system built with Clean Architecture principles.

## Architecture

This project follows Clean Architecture with the following layers:

- **Domain**: Core business entities and rules
- **Application**: Use cases and business logic
- **Infrastructure**: External concerns (database, frameworks)
- **Presentation**: API and user interfaces

## Features

- Create and manage events
- Register participants for events
- List events and participants
- Event status management (Draft, Published, Cancelled, Completed)

## Project Structure

```
├── src/
│   ├── domain/                 # Domain layer
│   │   ├── entities/          # Business entities
│   │   ├── value_objects/     # Value objects
│   │   └── exceptions/        # Domain exceptions
│   ├── application/           # Application layer
│   │   ├── dto/              # Data transfer objects
│   │   ├── ports/            # Abstract interfaces
│   │   └── use_cases/        # Business use cases
│   ├── infrastructure/        # Infrastructure layer
│   │   ├── django_app/       # Django models and admin
│   │   ├── repositories/     # Repository implementations
│   │   └── config/           # Dependency injection
│   └── presentation/         # Presentation layer
│       └── api/              # REST API
├── tests/                     # Test suite
├── config/                    # Django configuration
├── manage.py                  # Django management script
└── pyproject.toml            # Project dependencies
```

## Setup

1. Install dependencies:
```bash
pip install -e .
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Events
- `GET /api/events/` - List all events
- `POST /api/events/create/` - Create a new event
- `GET /api/events/{id}/` - Get event details

### Participants
- `POST /api/participants/register/` - Register for an event
- `GET /api/events/{id}/participants/` - List event participants

## Testing

Run tests with:
```bash
pytest
```

## Development

This project follows Clean Architecture principles:

- **Dependency Rule**: Inner layers don't depend on outer layers
- **Abstraction**: Interfaces define contracts between layers
- **Dependency Injection**: Dependencies are injected, not hardcoded
- **Single Responsibility**: Each class has one reason to change

## License

MIT License