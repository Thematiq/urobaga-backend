
# Urobaga

Instrukcja uruchomienia:

1. Sklonuj repozytorium.
2. Ustaw w pliku hackaton/quiz_questions/questions.csv swoje pytania.
3. W głównym katalogu:
   - Wywołaj `git submodule init`
   - Wywołaj `git submodule update`
4. W katalogu web:
   - Wywołaj `git fetch`
   - Wywołaj `git switch dev`
   - Zmień zmienną środowiskową SOCKET_URL, żeby wskazywała na adres, na którym odpalony będzie backend.
   - Wywołaj `npm install`
   - Wywołaj `npm run build:prod`
6. Zainstaluj docker
7. W katalogu głównym użyj `docker build .` i zaobserwuj nazwę obrazu
8. Użyj nazwy obrazu przy `docker run -p 8000:8000 <nazwa_obrazu>`

