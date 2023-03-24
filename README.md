# Tapio

## To do

* [X] Tests  One by specs !!! :

  * [X] Model test
  * [ ] still API to test
* [ ] Add silk to inspect queries



## Environment Setup

- Build docker image
  - `docker-compose up -d --build`
- Connect to docker, create super user, and run migration
  - `./helper_connectDocker`
  - `python manage.py migrate`
  - create super user : `echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@tapio.io', 'tapio1234')" | python manage.py shell`
- The migrations give you an initial load  of sample data that you can play with

## Documentation

- API links : http://localhost:8000/api/
- API documentation :
  - http://localhost:8000/api/swagger/
  - http://localhost:8000/api/redoc/

## Test API

* If you use Thunder VScode extension : there are some exemples of POST/PATCH for source, reduction strategy and report API in thunder-test folder.
