# Tapio

## Environment Setup

- Build docker image
  - docker-compose up -d --build
- Connect to docker, create super user, and run migration
  - ./helper_connectDocker
  - python manage.py createsuperuser
  - python manage.py migrate
- The migrations give you an initial load  of sample data that you can play with

## Documentation

- API links : http://localhost:8000/api/
- API documentation :
  - http://localhost:8000/api/swagger/
  - http://localhost:8000/api/redoc/
