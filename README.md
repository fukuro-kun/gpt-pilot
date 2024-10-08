<div align="center">

# 🧑‍✈️ GPT PILOT 🧑‍✈️

</div>

---

<div align="center">

### GPT Pilot generiert nicht nur Code, es baut Anwendungen!

</div>

---

<!-- Inhaltsverzeichnis -->
* [🔌 Anforderungen](#-anforderungen)
* [🚦Wie starte ich mit gpt-pilot?](#wie-starte-ich-mit-gpt-pilot)
* [🌐 Sprachunterstützung](#-sprachunterstützung)
* [🔎 Beispiele](#-beispiele)
* [🐳 Wie starte ich gpt-pilot in Docker?](#-wie-starte-ich-gpt-pilot-in-docker)
* [🧑‍💻️ CLI-Argumente](#-cli-argumente)
* [🏗 Wie funktioniert GPT Pilot?](#-wie-funktioniert-gpt-pilot)
* [📄 Lizenz und Ursprung](#-lizenz-und-ursprung)
<!-- Inhaltsverzeichnis -->

# 🔌 Anforderungen

- **Python 3.9+**

# 🚦Wie starte ich mit gpt-pilot?

### Wenn Sie neu bei GPT Pilot sind:

Nachdem Sie Python und (optional) PostgreSQL installiert haben, folgen Sie diesen Schritten:

1. `git clone https://github.com/fukuro-kun/gpt-pilot.git` (Repository klonen)
2. `cd gpt-pilot` (in den Repository-Ordner wechseln)
3. Virtuelle Umgebung erstellen:
   - Mit venv:
     `python3 -m venv venv`
   - Mit conda:
     `conda create --name gpt-pilot python=3.9`

4. Virtuelle Umgebung aktivieren:
   - Mit venv:
     - Unix/macOS: `source venv/bin/activate`
     - Windows: `venv\Scripts\activate`
   - Mit conda:
     `conda activate gpt-pilot`
5. `pip install -r requirements.txt` (Abhängigkeiten installieren)
6. `cp example-config.json config.json` (`config.json` Datei erstellen)
7. Setzen Sie Ihren Schlüssel und andere Einstellungen in der `config.json` Datei:
   - LLM-Anbieter (`openai`, `anthropic` oder `groq`) Schlüssel und Endpunkte (lassen Sie `null` für Standard) (beachten Sie, dass Azure und OpenRouter über die `openai`-Einstellung unterstützt werden)
   - Ihr API-Schlüssel (wenn `null`, wird er aus den Umgebungsvariablen gelesen)
   - Datenbankeinstellungen: standardmäßig wird sqlite verwendet, PostgreSQL sollte auch funktionieren
   - Optional aktualisieren Sie `fs.ignore_paths` und fügen Sie Dateien oder Ordner hinzu, die von GPT Pilot im Arbeitsbereich nicht verfolgt werden sollen, nützlich um von Compilern erstellte Ordner zu ignorieren
8. `python main.py` (GPT Pilot starten)

Aller generierter Code wird im Ordner `workspace` innerhalb des Ordners gespeichert, der nach dem App-Namen benannt ist, den Sie beim Starten des Piloten eingeben.

# 🌐 Sprachunterstützung

GPT Pilot unterstützt jetzt mehrere Sprachen für die Benutzeroberfläche, mit einem Fokus auf Deutsch und Englisch.

### Spracheinstellung

Die Sprache kann in der `config.json` Datei festgelegt werden:

```json
{
  "language": "de",
  ...
}
```

Unterstützte Sprachcodes:
- `"de"` für Deutsch
- `"en"` für Englisch

Wenn keine Sprache angegeben ist oder eine nicht unterstützte Sprache gewählt wurde, fällt das System auf Deutsch zurück.

### Wichtige Hinweise zur Mehrsprachigkeit

- Die Benutzeroberfläche und Systemmeldungen werden in der gewählten Sprache angezeigt.
- Die interne Kommunikation und Code-Generierung erfolgen weiterhin auf Englisch, um die Kompatibilität und Effizienz zu gewährleisten.
- Dynamisch generierte Inhalte (z.B. LLM-Ausgaben) bleiben unübersetzt.

Wir arbeiten kontinuierlich daran, die Sprachunterstützung zu verbessern und weitere Sprachen hinzuzufügen. Feedback und Beiträge zur Verbesserung der Übersetzungen sind willkommen!

# 🔎 Beispiele

[Klicken Sie hier](https://github.com/Pythagora-io/gpt-pilot/wiki/Apps-created-with-GPT-Pilot), um Beispiel-Apps zu sehen, die mit GPT Pilot erstellt wurden.

# 🐳 Wie starte ich gpt-pilot in Docker?
1. `git clone https://github.com/fukuro-kun/gpt-pilot.git` (Repository klonen)
2. Aktualisieren Sie die Umgebungsvariablen in `docker-compose.yml`, was über `docker compose config` erfolgen kann. Wenn Sie ein lokales Modell verwenden möchten, gehen Sie bitte zu [https://localai.io/basics/getting_started/](https://localai.io/basics/getting_started/).
3. Standardmäßig liest und schreibt GPT Pilot in `~/gpt-pilot-workspace` auf Ihrem Gerät, Sie können dies auch in `docker-compose.yml` bearbeiten
4. Führen Sie `docker compose build` aus. Dies wird einen gpt-pilot Container für Sie erstellen.
5. Führen Sie `docker compose up` aus.
6. Greifen Sie auf das Web-Terminal auf `Port 7681` zu
7. `python main.py` (GPT Pilot starten)

Dies startet zwei Container, einen als neues Image, das von der `Dockerfile` erstellt wurde, und eine Postgres-Datenbank. Das neue Image hat auch [ttyd](https://github.com/tsl0922/ttyd) installiert, sodass Sie einfach mit gpt-pilot interagieren können. Node ist ebenfalls auf dem Image installiert und Port 3000 ist freigegeben.

### PostgreSQL-Unterstützung

GPT Pilot verwendet standardmäßig die eingebaute SQLite-Datenbank. Wenn Sie die PostgreSQL-Datenbank verwenden möchten, müssen Sie zusätzlich die Pakete `asyncpg` und `psycopg2` installieren:

```bash
pip install asyncpg psycopg2
```

Dann müssen Sie die `config.json` Datei aktualisieren, um `db.url` auf `postgresql+asyncpg://<benutzer>:<passwort>@<db-host>/<db-name>` zu setzen.

# 🧑‍💻️ CLI-Argumente

### Erstellte Projekte (Apps) auflisten

```bash
python main.py --list
```

### Laden und Fortfahren vom letzten Schritt in einem Projekt (App)

```bash
python main.py --project <app_id>
```

### Laden und Fortfahren von einem bestimmten Schritt in einem Projekt (App)

```bash
python main.py --project <app_id> --step < step >
```

Warnung: Dies löscht den gesamten Fortschritt nach dem angegebenen Schritt!

### Projekt (App) löschen

```bash
python main.py --delete <app_id>
```

Löscht das Projekt mit der angegebenen `app_id`. Warnung: Dies kann nicht rückgängig gemacht werden!

### Andere Befehlszeilenoptionen

Es gibt mehrere andere Befehlszeilenoptionen. Um alle verfügbaren Optionen zu sehen, verwenden Sie das Flag `--help`:

```bash
python main.py --help
```

# 🏗 Wie funktioniert GPT Pilot?
Hier sind die Schritte, die GPT Pilot unternimmt, um eine App zu erstellen:

1. Sie geben den App-Namen und die Beschreibung ein.
2. **Product Owner Agent** macht wie im echten Leben nichts. :)
3. **Specification Writer Agent** stellt ein paar Fragen, um die Anforderungen besser zu verstehen, wenn die Projektbeschreibung nicht gut genug ist.
4. **Architect Agent** schreibt die Technologien auf, die für die App verwendet werden, und prüft, ob alle Technologien auf der Maschine installiert sind, und installiert sie, wenn nicht.
5. **Tech Lead Agent** schreibt Entwicklungsaufgaben auf, die der Entwickler implementieren muss.
6. **Developer Agent** nimmt jede Aufgabe und beschreibt, was getan werden muss, um sie zu implementieren. Die Beschreibung ist in menschenlesbarer Form.
7. **Code Monkey Agent** nimmt die Beschreibung des Entwicklers und die vorhandene Datei und implementiert die Änderungen.
8. **Reviewer Agent** überprüft jeden Schritt der Aufgabe und wenn etwas falsch gemacht wurde, sendet der Reviewer es zurück zum Code Monkey.
9. **Troubleshooter Agent** hilft Ihnen, GPT Pilot gutes Feedback zu geben, wenn etwas falsch ist.
10. **Debugger Agent** man sieht ihn ungern, aber er ist Ihr bester Freund, wenn die Dinge schief gehen.
11. **Technical Writer Agent** schreibt die Dokumentation für das Projekt.

# 📄 Lizenz und Ursprung

Dieses Projekt ist ein Fork des ursprünglichen [GPT Pilot Projekts](https://github.com/Pythagora-io/gpt-pilot) und wird unter der Functional Source License, Version 1.1, MIT Future License (FSL-1.1-MIT) lizenziert.

Während dieses Repository unabhängig weiterentwickelt wird, erkennen wir die Arbeit und den Beitrag der ursprünglichen Entwickler an. Für Informationen zur ursprünglichen Community und Entwicklung besuchen Sie bitte das [Originalrepository](https://github.com/Pythagora-io/gpt-pilot).
