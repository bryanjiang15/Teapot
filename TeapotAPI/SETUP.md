# TeapotAPI - Database Setup Guide

## Prerequisites

1. **PostgreSQL** - Install PostgreSQL 12+ on your system
2. **Python 3.8+** - Make sure you have Python 3.8 or higher
3. **Virtual Environment** - Create and activate a virtual environment

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install additional packages for development
pip install alembic psycopg2-binary
```

### 2. Database Setup

#### Option A: Local PostgreSQL
```bash
# Create database
createdb tcg_db

# Or using psql
psql -U postgres
CREATE DATABASE tcg_db;
```

#### Option B: Docker PostgreSQL
```bash
# Run PostgreSQL in Docker
docker run --name tcg-postgres \
  -e POSTGRES_DB=tcg_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15
```

### 3. Environment Configuration

```bash
# Copy environment file
cp env.example .env

# Edit .env with your database credentials
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/tcg_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

### 4. Initialize Database

```bash
# Run the setup script
python setup_database.py

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Start the Server

```bash
# Run the development server
python run.py
```

## Database Schema

The following tables will be created:

- **users** - User authentication and profiles
- **rulesets** - Game rules and versions
- **cards** - TCG card definitions
- **matches** - Game sessions
- **match_events** - Event sourcing for matches

## Alembic Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# Show migration history
alembic history

# Show current revision
alembic current
```

## Troubleshooting

### Common Issues:

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify database credentials in .env
   - Ensure database exists

2. **Import Errors**
   - Make sure you're in the TeapotAPI directory
   - Check virtual environment is activated
   - Install missing dependencies

3. **Migration Errors**
   - Check alembic.ini configuration
   - Ensure all models are imported in database.py
   - Verify database URL is correct

### Debug Mode:

```bash
# Run with debug logging
DEBUG=True python run.py

# Check database connection
python -c "from app.database import engine; print('Database connected!')"
```

## Production Setup

For production deployment:

1. **Use environment variables** for all secrets
2. **Set up connection pooling** for better performance
3. **Configure SSL** for database connections
4. **Set up database backups**
5. **Use managed PostgreSQL** (AWS RDS, Google Cloud SQL, etc.)

## Next Steps

After successful setup:

1. Test the API endpoints at `http://localhost:8000/docs`
2. Create your first user via `/auth/register`
3. Start building your game logic
4. Add more models and endpoints as needed
