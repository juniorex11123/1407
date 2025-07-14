# TimeTracker Pro - Instrukcja wdrożenia na home.pl

## 📦 Pliki gotowe do wdrożenia

Aplikacja została zbudowana i jest gotowa do wdrożenia. Pliki znajdują się w:
- **Folder**: `/app/frontend/build/`
- **Archiwum**: `/app/frontend/timetracker-pro-build.tar.gz` (482KB)

## 🚀 Instrukcja wdrożenia na home.pl

### Krok 1: Przygotowanie backendu
Przed wdrożeniem frontendu musisz przygotować backend na swoim serwerze:

1. **Skopiuj pliki backendu** z folderu `/app/backend/` na swój serwer
2. **Zainstaluj Python i wymagane biblioteki**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Skonfiguruj bazę danych MongoDB** na swoim serwerze
4. **Skonfiguruj plik .env** z prawidłowymi danymi:
   ```
   MONGO_URL="mongodb://localhost:27017"
   DB_NAME="timetracker_database"
   JWT_SECRET="your-production-secret-key-here"
   ```
5. **Uruchom backend**:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8001
   ```

### Krok 2: Konfiguracja URL backendu dla frontendu

**WAŻNE**: Przed wdrożeniem frontendu musisz zaktualizować URL backendu.

Aktualnie aplikacja jest skonfigurowana dla środowiska deweloperskiego:
```
REACT_APP_BACKEND_URL=https://1ece32d4-e477-4330-968e-4ff479ed65b7.preview.emergentagent.com
```

**Musisz zmienić to na URL swojego serwera backendu na home.pl:**

1. Edytuj plik `/app/frontend/.env`:
   ```
   REACT_APP_BACKEND_URL=https://twoja-domena.home.pl
   ```
   
2. Przebuduj aplikację:
   ```bash
   cd /app/frontend
   yarn build
   ```

### Krok 3: Wdrożenie frontendu na home.pl

1. **Pobierz pliki**: Pobierz archiwum `timetracker-pro-build.tar.gz`
2. **Rozpakuj na serwerze**: 
   ```bash
   tar -xzf timetracker-pro-build.tar.gz
   ```
3. **Skopiuj pliki**: Skopiuj zawartość folderu `build/` do głównego katalogu swojej domeny na home.pl (zazwyczaj `public_html/`)

### Krok 4: Konfiguracja serwera web

Dla prawidłowego działania React Router, musisz skonfigurować przekierowania:

**Dla Apache (.htaccess)**:
```apache
Options -MultiViews
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^ index.html [QR,L]
```

**Dla Nginx**:
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

## 🔧 Struktura aplikacji

### Frontend (React)
- **Główna strona**: Marketing/informacje o produkcie
- **Panel logowania**: `/panel`
- **Dashboardy**: 
  - Owner: Zarządzanie firmami i użytkownikami
  - Admin: Zarządzanie pracownikami i czasem pracy
  - User: Skanowanie QR i podstawowe funkcje

### Backend (FastAPI)
- **API**: Wszystkie endpointy pod `/api/`
- **Dokumentacja**: `/docs` (Swagger UI)
- **Baza danych**: MongoDB z kolekcjami:
  - `users` - użytkownicy systemu
  - `companies` - firmy
  - `employees` - pracownicy
  - `time_entries` - wpisy czasu pracy

## 👥 Domyślni użytkownicy

Po uruchomieniu aplikacji automatycznie tworzeni są użytkownicy:

- **Owner**: 
  - Login: `owner`
  - Hasło: `owner123`
  - Uprawnienia: Pełny dostęp do systemu

- **Admin**:
  - Login: `admin` 
  - Hasło: `admin123`
  - Uprawnienia: Zarządzanie pracownikami firmy "Firma ABC"

- **User**:
  - Login: `user`
  - Hasło: `user123`
  - Uprawnienia: Podstawowe funkcje użytkownika

## 🔒 Bezpieczeństwo

### Produkcyjne ustawienia bezpieczeństwa:
1. **Zmień JWT_SECRET** na długi, losowy ciąg znaków
2. **Zmień domyślne hasła** użytkowników
3. **Skonfiguruj HTTPS** na swoim serwerze
4. **Ogranicz dostęp do bazy danych** tylko dla aplikacji
5. **Regularne kopie zapasowe** bazy danych

## 📋 Lista kontrolna wdrożenia

- [ ] Backend zainstalowany i uruchomiony
- [ ] Baza danych MongoDB skonfigurowana
- [ ] Zmieniony REACT_APP_BACKEND_URL w .env
- [ ] Aplikacja przebudowana z nowym URL
- [ ] Pliki frontendu skopiowane na serwer
- [ ] Skonfigurowane przekierowania dla React Router
- [ ] Zmienione domyślne hasła użytkowników
- [ ] Skonfigurowane HTTPS
- [ ] Przetestowane logowanie i podstawowe funkcje

## 🆘 Rozwiązywanie problemów

### Częste problemy:

1. **"Cannot connect to backend"**
   - Sprawdź czy backend jest uruchomiony
   - Sprawdź URL w REACT_APP_BACKEND_URL
   - Sprawdź CORS na backendzie

2. **"404 Not Found" po odświeżeniu strony**
   - Skonfiguruj przekierowania serwera web (.htaccess/nginx)

3. **Błędy logowania**
   - Sprawdź czy baza danych jest dostępna
   - Sprawdź logi backendu
   - Sprawdź JWT_SECRET

## 📞 Wsparcie

Aplikacja została przetestowana i wszystkie funkcje działają poprawnie:
- ✅ Logowanie wszystkich typów użytkowników
- ✅ Zarządzanie firmami (Owner)
- ✅ Zarządzanie użytkownikami (Owner)  
- ✅ Zarządzanie pracownikami (Admin)
- ✅ Generowanie kodów QR (Admin)
- ✅ Zarządzanie czasem pracy (Admin)
- ✅ Autoryzacja i uprawnienia

Powodzenia z wdrożeniem! 🚀