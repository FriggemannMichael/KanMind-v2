# Checkliste Django/DRF-Projekte

Stand: Review am 20.06.2026

Dieser Bericht bewertet den aktuellen Projektstand gegen die Vorgaben der
Checkliste. Erfuellte Punkte sind abgehakt. Punkte mit Einschraenkungen bleiben
offen und enthalten einen kurzen Hinweis.

## 1. Allgemeines

### Endpoints

- [x] Alle Endpoints sind nach Dokumentation erstellt.
  - Die dokumentierten Auth-, Board-, Task- und Comment-Endpunkte sind vorhanden.
- [x] Das Projekt muss durch unsere PM-Tests bei Abgabe eine Test-Coverage von mind. 95% erreichen.
  - Frischer Coverage-Lauf: 97% inklusive Tests, 95% bei Auswertung ohne Testdateien.

### Clean Code/Dokumentation

- [x] Eine Funktion/Methode hat max. eine Aufgabe und maximal 14 Zeilen.
  - Produktionscode ist inzwischen unter der 14-Zeilen-Grenze.
  - Mehrere Testmethoden und `setUp()`-Methoden sind laenger als 14 Zeilen;
    diese Abweichung ist fuer Tests akzeptiert.
- [x] Kein auskommentierter Code oder `print()`-Befehle verbleiben im Projekt.
  - Keine `print()`-Aufrufe oder auskommentierten Codebloecke gefunden.
- [x] Code ist PEP8-konform.
  - In den relevanten Python-Dateien wurden keine Zeilen ueber 79 Zeichen gefunden.
  - Hinweis: `pycodestyle`/`flake8` sind lokal nicht installiert, daher kein offizieller Linterlauf.
- [x] Der Code ist dokumentiert/kommentiert.
  - Produktionscode ist mit Modul-, Klassen- und Methoden-Docstrings dokumentiert.
  - Testmodule, Testklassen und Testmethoden beschreiben, welches Verhalten geprueft wird.

## 2. GitHub Repository

- [x] Es existiert eine aussagekraeftige README.md mit Startanleitung und Besonderheiten.
  - README enthaelt Projektbeschreibung, Stack, Setup, Tests, Serverstart, API-Uebersicht, Auth und DB-Policy.
- [x] Die README.md ist auf Englisch verfasst.
- [x] Das Backend ist in einem eigenen Repository hochgeladen ohne Frontend.
  - Remote: `FriggemannMichael/KanMind.git`.
  - Keine typischen Frontend-Dateien wie `package.json`, `src/`, `public/`, `node_modules/`, `dist/` getrackt.
- [x] Es existiert eine vollstaendige `requirements.txt`.
  - `pip check` meldet keine kaputten Abhaengigkeiten.
- [x] Die Datenbank sollte niemals auf GitHub geladen werden.
  - `db.sqlite3` existiert lokal, ist aber nicht getrackt.
  - `.gitignore` ignoriert `db.sqlite3`, `*.sqlite3`, `*.sqlite`, `*.db`.

## 3. Conventions

### Projekt- & App-Struktur

- [x] Das Projekt wird beim Starten `core` genannt.
  - `core/` enthaelt `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`.
- [x] Alle Apps erhalten ein sprechendes Praefix oder Suffix.
  - `auth_app` und `kanban_app` sind sprechend benannt.
- [x] Jede App enthaelt einen `api/`-Ordner mit API-spezifischen Dateien.
  - Beide Apps enthalten `api/serializers.py`, `api/views.py`, `api/urls.py`, `api/permissions.py`.
- [x] Die Admin-Umgebung ist nutzbar.
  - `/admin/` ist registriert.
  - `Board`, `Task` und `Comment` sind im Admin registriert.
  - `python manage.py check` meldet keine Probleme.

### Models

- [x] Sprechende Klassennamen im PascalCase.
  - `Board`, `Task`, `Comment`.
- [x] Felder im snake_case.
  - Beispiele: `due_date`, `created_at`, `member_boards`, `assigned_tasks`.
- [x] Sinnvolle Darstellung ueber `__str__` und Meta-Optionen.
  - Alle Models haben `__str__`.
  - Alle Models definieren `Meta.ordering`.
- [x] Keine Logik in Modellen.
  - Models enthalten nur Datenstruktur, Choices, Meta und `__str__`.
- [x] Model-Beziehungen sauber mit `related_name` und `on_delete`.
  - ForeignKeys und ManyToMany-Beziehungen sind mit passenden `related_name`-Werten definiert.

### Serializer

- [x] Nutze `ModelSerializer` fuer CRUD-Serialisierungen.
  - Alle Board-, Task-, Comment- und User-Response-Serializer nutzen `ModelSerializer`.
  - `RegistrationSerializer` und `LoginSerializer` nutzen bewusst `Serializer`, da sie Auth-Input validieren.
- [x] Felder explizit angeben, nicht `__all__`.
  - Kein `fields = "__all__"` gefunden.
- [x] Felder in der gewuenschten Reihenfolge benennen.
  - Feldreihenfolgen passen zur API-Dokumentation und Response-Struktur.
- [x] Extra-Validierung ueber `validate_*` oder `validate`.
  - E-Mail-Duplikate, Passwort-Wiederholung, Login, Board-Zugriff und Task-Zuweisungen werden in Serializern validiert.

### Views

- [x] Verwende `ModelViewSet` fuer CRUD, `APIView` bzw. GenericAPIView fuer individuelle Endpunkte.
  - `BoardViewSet` nutzt `ModelViewSet`.
  - `TaskViewSet` nutzt `GenericViewSet` + Mixins fuer Create/Update/Delete und Custom-Listen.
  - Auth- und Comment-Endpunkte nutzen `APIView` bzw. generische DRF-Views.
- [ ] `queryset` und `serializer_class` gehoeren als Properties in die Klasse.
  - `serializer_class` ist in den meisten Views gesetzt.
  - `BoardViewSet` nutzt ausschliesslich `get_serializer_class()`.
  - Dynamische Views nutzen `get_queryset()` statt statischem `queryset`; technisch korrekt, aber formal nicht voll checklistenfest.
- [x] `get_queryset()` fuer dynamische Querysets verwenden.
  - User-/Action-spezifische Board-, Task- und Comment-Querysets sind dynamisch umgesetzt.
- [x] Permissions klar deklarieren mit `permission_classes = [...]`.
  - Alle API-Views/ViewSets deklarieren Permissions.

### URLs

- [x] API-Routen sind ressourcenorientiert, nicht aktionsbasiert.
  - Beispiele: `/api/boards/`, `/api/boards/{id}/`, `/api/tasks/{id}/`, `/api/tasks/{id}/comments/`.
  - `assigned-to-me` und `reviewing` sind dokumentierte Collection-Unterressourcen.
- [x] Jede App hat ihre eigene URL-Datei.
  - `auth_app/api/urls.py`, `kanban_app/api/urls.py`.
- [x] Hauptprojekt `core` hat zentrales Routing mit `include()`.
  - `core/urls.py` bindet beide App-URL-Dateien ein.

### Permissions & Auth

- [x] Jede App hat eigene `permissions.py`, sofern noetig.
  - `kanban_app/api/permissions.py` enthaelt Object-Permissions.
  - `auth_app/api/permissions.py` existiert; eigene Permissions sind dort aktuell nicht noetig.
- [x] Permissions logisch kombinieren.
  - Kombinationen wie `IsAuthenticated + IsBoardOwner` und `IsAuthenticated + IsTaskCreatorOrBoardOwner` sind umgesetzt.
- [x] Keine offenen Endpunkte ohne expliziten Grund/Vorgabe.
  - Global gilt TokenAuthentication + `IsAuthenticated`.
  - Offen sind nur Registrierung und Login mit `AllowAny`.

## 4. Best Practices

### Best Practices fuer Imports

- [x] Importe gruppieren und sortieren.
  - Standardbibliothek, Django/DRF/Third-party und lokale Importe sind getrennt.
  - Keine auffaelligen Import-Gruppierungsfehler gefunden.

### Klares Verantwortlichkeitsprinzip

- [x] Verantwortlichkeiten sind sauber getrennt.
  - Models: Datenstruktur.
  - Serializers: Validierung und Transformation.
  - Views: Request-/Response-Logik, Querysets und Routing-Anbindung.
  - Permissions: Zugriffskontrolle.
  - Hinweis: Einige Zugriffspruefungen fuer Kommentare liegen in der View statt in einer eigenen Permission-Klasse. Das ist funktional korrekt, koennte aber bei weiterem Wachstum ausgelagert werden.

### HTTP-Statuscodes korrekt verwenden

- [x] HTTP-Statuscodes werden korrekt verwendet und getestet.
  - `201 CREATED` fuer Registrierungen, Board-, Task- und Comment-Erstellung.
  - `204 NO CONTENT` fuer Delete-Endpunkte.
  - `400 BAD REQUEST` fuer Validierungsfehler.
  - `401 UNAUTHORIZED` fuer anonyme Zugriffe.
  - `403 FORBIDDEN` fuer fehlende Berechtigungen.
  - `404 NOT FOUND` fuer fehlende Ressourcen.
  - Statuscode-Faelle sind in `auth_app/tests.py` und `kanban_app/tests.py` abgedeckt.

## Offene Punkte vor Abgabe

- Optional: `serializer_class` und ggf. ein Basis-`queryset` bei `BoardViewSet` ergaenzen, um die View-Checkliste formal komplett zu erfuellen.
- Optional: Kommentar-Zugriffslogik in eine eigene Permission-Klasse verschieben, wenn die Trennung noch strenger bewertet wird.
