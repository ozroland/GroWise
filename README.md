GroWise – Növény- és Betegségfelismerő Rendszer
Ez a projekt egy Django alapú webalkalmazás, amely mesterséges intelligencia segítségével képes növények és növénybetegségek azonosítására feltöltött képek alapján.

Szükséges alkalmazások és eszközök
Visual Studio Code	Kódszerkesztés
pgAdmin	PostgreSQL adatbázis kezelése
Postman (opcionális)	API tesztelése
Python 3.12+	Backend futtatásához
Git	Verziókezelés

Repo klónozása:
git clone https://github.com/<felhasznalonev>/growise.git
cd growise

Virtuális környezet létrehozása és aktiválása:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

Követelmények telepítése:
pip install -r requirements.txt

.env fájl létrehozása (példa):
SECRET_KEY=valami_titkos_kulcs
DB_NAME=growise
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=valami@gmail.com
EMAIL_HOST_PASSWORD=valamiJelszo
DEFAULT_FROM_EMAIL=valami@gmail.com
PLANTNET_API_KEY=plantnetkulcs123
SENTRY_DSN=https://...

Modell tanitasi notebook:
https://colab.research.google.com/drive/1cCqHHhIiIFEZ5UZC662f-1wn5JyaTpy-

Adatbázis migrálása:
python manage.py makemigrations
python manage.py migrate

Admin user létrehozása (opcionális):
python manage.py createsuperuser

Szerver indítása:
python manage.py runserver

URL-ek:
Backend: http://127.0.0.1:8000/
Admin felület: http://127.0.0.1:8000/admin/
Betegségfelismerő oldal: http://127.0.0.1:8000/recognition/disease/
Növényfelismerő oldal: http://127.0.0.1:8000/recognition/plant/

Tesztfuttatás parancsa:
python manage.py test
