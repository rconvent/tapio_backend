# Tapio

## To do

* [X] scenario_delta()

  * [X] serait très gourmand en ressources au vue de la taille de certains rapports
  * [X] permet-il vraiment d'afficher la valeur de modifications appliquées en série?
* [X] stocker les scénarios et les liens entre modified_sources et sources dans un json est une architecture qui ne sera pas tenable sur le long terme et qui provoque beaucoup de redondance avec le reste de ton implémentation
* [ ] to_representation() serait très gourmand en ressources au vue de la taille de certains rapports
* [ ] source a maintenant une FK vers company et report a un M2M vers les sources -> un report peut être à plusieurs companies ?

  * [ ] Dans la même idée qu'est-ce-qui est supposé se passer lors du post_save de modified_sources du coup?
  * [ ] Et d'ailleurs dans cette optique pour resave report alors qu'il n'y a rien dans les pre, post et save de report?
* [X] return (self.source.total_emission + self.total_emission) - self.source.total_emission  n'y a-t-il pas plus simple?
* [X] ~~modified source est créé par défaut quand une source est créée, pourquoi?~~
* [ ] pas de create dans modifiedSource Serializer donc on doit créer une source pour pouvoir en créer plusieurs et en séries?
* [X] 0 est retourné dans get_delta si acq_year > year, mais total_emission n'est jamais mit à jour => dans le
* [ ] Tests  One by specs !!! :

  * [X] Model test
  * [ ] still API to test



### drop database (before last commit)

python manage.py sqlflush

python manage.py makemigrations
python manage.py migrate

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
