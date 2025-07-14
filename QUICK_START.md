# 🚀 TimeTracker Pro - Szybki Start dla home.pl

## ✅ Build Aplikacji Gotowy!

Aplikacja została pomyślnie zbudowana i jest gotowa do wdrożenia na hosting home.pl.

## 📦 Pliki do pobrania:

- **📁 Folder**: `/app/frontend/build/` (2.0MB)
- **📦 Archiwum**: `/app/frontend/timetracker-pro-build.tar.gz` (482KB)

## ⚡ Szybkie wdrożenie:

### 1. **WAŻNE: Zmień URL backendu**
Przed wdrożeniem MUSISZ zmienić URL backendu w pliku `.env`:

```bash
# Obecny (deweloperski):
REACT_APP_BACKEND_URL=https://1ece32d4-e477-4330-968e-4ff479ed65b7.preview.emergentagent.com

# Zmień na swój serwer:
REACT_APP_BACKEND_URL=https://twoja-domena.home.pl
```

Następnie przebuduj aplikację:
```bash
cd /app/frontend
yarn build
```

### 2. **Wdróż na home.pl**:
1. Pobierz archiwum `timetracker-pro-build.tar.gz`
2. Rozpakuj w katalogu `public_html/` na swoim hostingu
3. Plik `.htaccess` jest już dołączony do buildu

### 3. **Skonfiguruj backend**:
- Skopiuj pliki z `/app/backend/` na swój serwer
- Zainstaluj zależności: `pip install -r requirements.txt`
- Skonfiguruj MongoDB
- Uruchom: `uvicorn server:app --host 0.0.0.0 --port 8001`

## 🔑 Domyślne loginy:
- **Admin**: `admin` / `admin123`
- **Owner**: `owner` / `owner123`  
- **User**: `user` / `user123`

## 📖 Pełna dokumentacja:
Szczegółowe instrukcje znajdziesz w pliku `/app/DEPLOYMENT_GUIDE.md`

---
**Status**: ✅ **GOTOWE DO WDROŻENIA** 🎉