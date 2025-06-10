# BSO Greenbone Scanner

## Instalacja

1. **Klonowanie repozytorium**

```sh
# Linux:
git clone https://gitlab-stud.elka.pw.edu.pl/kgromko/bso_projekt.git
cd bso_projekt
```

2. **Przygotowanie konfiguracji**

- Skopiuj pliki `.env.example` do `.env` :

```sh
cp .env.example .env
cp msmtprc.example msmtprc
```

- Uzupełnij plik `.env`  swoimi danymi (adresy e-mail, hasła, zakresy sieci itp.).

3. **Instalacja i uruchomienie**

- Upewnij się, że masz zainstalowane: Docker, Docker Compose, git, curl.
- Uruchom instalację:

```sh
chmod +x install_all.sh
./install_all.sh
```

4. **Automatyzacja**

- Przykładowy wpis do crontaba znajdziesz w `crontab.example`.
- Domyślnie raport PDF generuje się i wysyła na e-mail codziennie o 2:00.

5. **Ręczne uruchamianie skanowania i eksportu**

- Skanowanie sieci LAN i wysyłka raportu:

```sh
./scripts/scan-and-export.gmp.sh
```

- Wysyłka raportu PDF na e-mail (jeśli masz już plik PDF):

```sh
./scripts/send-report.sh ./raport.pdf
```

## Pliki konfiguracyjne

- `.env` – dane dostępowe, adresy e-mail, zakresy skanowania (szablon: `.env.example`)


## Struktura projektu

- `install_all.sh` – główny skrypt instalacyjny
- `docker-compose.yml` – definicja kontenerów
- `scripts/` – automatyzacja skanowania, eksportu, wysyłki
- `crontab.example` – przykładowy wpis do crona

## Bezpieczeństwo

- **Nie przechowuj danych prywatnych w repozytorium!**
- Pliki `.env` i `msmtprc` powinny być dodane do `.gitignore`.

---

Projekt: https://gitlab-stud.elka.pw.edu.pl/kgromko/bso_projekt.git
