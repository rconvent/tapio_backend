# Idees

## Should do

- Use Managers
- use source serializer inside post
- multi langual hstor field => display user language
- Assets
- source type => filter
- add company and permission on API (can only current company and children)
  - https://docs.djangoproject.com/en/4.1/topics/auth/default/
- in project description add user

## Could do

- Add path to company

# Instruction

- Build docker image
  - docker-compose up -d --build
- Connect to docker, create super user, and run migration
  - ./helper_connectDocker
  - python manage.py createsuperuser
  - python manage.py migrate
