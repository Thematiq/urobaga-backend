
# Urobaga

Instrukcja uruchomienia:

1. Sklonuj repozytorium.
2. Ustaw w pliku hackaton/quiz_questions/questions.csv swoje pytania.
3. Zainstaluj docker
4. W katalogu głównym użyj `docker build .` i zaobserwuj nazwę obrazu
5. Użyj nazwy obrazu przy `docker run -p 8000:8000 <nazwa_obrazu>`
6. Frontend uruchom przez:
   W głównym katalogu:
   git submodule update
   Wewnątrz katalogu web:
   npm install
   npm run dev
