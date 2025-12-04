# init project
Linux/Mac:
python3 -m venv .venv (ili venv)
Windows:
python -m venv .venv

Linux/Mac:
source .venv/bin/activate
Windows (CMD):
.venv\Scripts\activate.bat
Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

PyCharm:
file/settings/python/interceptor - use local .venv

# init server
python manage.py runserver

# exposing local host to public url (ngrok is free service)
ako će ti trebati za neki vanjski servis...
ngrok http localhost:8000
http://127.0.0.1:4040/inspect/http

# migratioins
python manage.py makemigrations
python manage.py migrate

# settings.py MariaDB

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myprojectdb',
        'USER': 'myprojectuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306', # Default port for MySQL
    }
}

# Debuger
na manage.py pod script parameters dodaj: runserver 127.0.0.1:9001 
dodaj si drugi port da ne moraš ubijati server na kojem vrtiš virtualku a debuger kad odradi svoje - isključiš pa ugasi insttancu servera

# adminuser create
python manage.py createsuperuser

# new app
python manage.py startapp gallery

# config/settings.py
INSTALLED_APPS = [
    # ... other apps
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'gallery', # Add our new app here
]

# query sample
daj mi pliz modele, admin i front za cms post(id, title, category_id(relation to category.id - multiple selection), subtitle, content, published, date_of_publishing(date/time), share_on_instagram(boolean), share_on_facebook(boolean), created_at) post_image(id, image_path, post_id(relation many_to_one), order) post_category(id, name, parent_id) Admin - category, post Front: grid view - bootstrap grid

napravi mi i post view - dodaj linkove i url patern po naslovu, u model dodaj url i akciju na save koja će parsati naslov članka u naslov.url

Ova 2 prompta odrade cms

gdje god da kreiraš ili radiš nekaj po modelu 
- python manage.py makemigrations
- python manage.py migrate

dosta libova u requirements.txt vjerovatno ne treba, ali mi se neda čistiti

postupak:
python manage.py - iizlista sve komande
pyhmon manage.py startapp bla

odeš na gemini zapise u adminu, napišeš kaj hoćeš, izabereš folder od tog apa kaj si kreiral - pokreni query...
uđeš u item koji dobiješ -> primjeni na fileove

- python manage.py makemigrations
- python manage.py migrate

to bi trebalo raditi

prije nekog ozbiljnijeg zahvata - comitaj, lako revertaš kasnije

ai studio - prijavi karticu, postavi si limit na 5€, dođe ti mail
1000000 tokena je 15ak $

za napraviti cms ode cca - 20000 tokena - stvar je besplatna skoro

Ima gumb history - tu mu je kontekst...pa ne moraš folder slati...

Ako kaj zapne - 095 533 533 6 - Goc

Disclamer - kod je odvratan ali sam ga pisal pred 2 mjeseca, radi kaj treba pa mi se neda prepisivati :)