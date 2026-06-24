# Technische Vorgaben und Definition of Done

Quelle: `docs/Checkliste Django_DRF-Projekte.md`

## Allgemeine Abnahmekriterien

- Alle Endpunkte muessen gemaess Endpoint-Dokumentation umgesetzt werden.
- Das Projekt muss bei Abgabe durch die PM-Tests mindestens 95 Prozent Test-Coverage erreichen.
- Es muss eine aussagekraeftige `README.md` existieren.
- Die `README.md` soll auf Englisch verfasst sein und alles enthalten, was zum Starten des Projekts noetig ist.
- Besonderheiten des Projekts muessen in der `README.md` dokumentiert werden.
- Das Backend wird ohne Frontend in einem eigenen Repository abgegeben.
- Eine vollstaendige `requirements.txt` muss vorhanden sein.
- Die Datenbank darf nicht in das Repository committed werden.

## Projektstruktur

- Das Django-Projekt heisst `core`.
- Der Ordner mit `settings.py`, `urls.py`, `wsgi.py` usw. heisst dadurch ebenfalls `core`.
- Apps erhalten sprechende Namen mit Praefix oder Suffix, zum Beispiel `auth_app` oder `kanban_app`.
- Jede App enthaelt einen `api/`-Ordner fuer API-spezifische Dateien.
- Typische Dateien im `api/`-Ordner sind `serializers.py`, `views.py`, `urls.py` und bei Bedarf `permissions.py`.
- Jede App hat eine eigene URL-Datei.
- Das zentrale Routing liegt in `core/urls.py` und included die App-URLs.
- Die Django-Admin-Oberflaeche muss nutzbar sein.

## Codequalitaet

- Eine Funktion oder Methode hat genau eine Aufgabe.
- Eine Funktion oder Methode soll maximal 14 Zeilen lang sein.
- Es duerfen kein auskommentierter Code und keine `print()`-Debug-Ausgaben im Projekt verbleiben.
- Der Code muss PEP8-konform sein.
- Der Code muss sinnvoll dokumentiert oder kommentiert sein.
- Kommentare sollen erklaeren, warum etwas noetig ist, nicht offensichtliche Codezeilen wiederholen.

## Import-Konventionen

Importe werden gruppiert und sortiert:

```python
# 1. Standardbibliothek
import os
from datetime import datetime

# 2. Drittanbieter
from django.db import models
from rest_framework import serializers

# 3. Lokale Importe
from .models import Project
from .services.project_logic import create_project_with_tasks
```

## Verantwortlichkeiten

- Models beschreiben die Datenstruktur.
- Serializers uebernehmen Validierung und Transformation.
- Views enthalten API-Logik und verbinden Request/Response mit Serializers und Querysets.
- Permissions regeln Zugriffskontrolle.
- Business-Logik gehoert nicht in Models.

## Models

- Model-Klassen verwenden `PascalCase`, zum Beispiel `UserProfile`.
- Felder verwenden `snake_case`, zum Beispiel `first_name` oder `is_active`.
- Models sollen eine sinnvolle `__str__`-Methode haben.
- Bei Bedarf werden `verbose_name`, `verbose_name_plural` und `ordering` in `Meta` gesetzt.
- Beziehungen muessen klare `related_name`-Werte und passende `on_delete`-Strategien definieren.

Beispiel:

```python
user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="projects",
)
```

## Serializer

- Fuer CRUD-Serialisierungen werden `ModelSerializer` verwendet.
- Felder werden explizit angegeben.
- `fields = "__all__"` wird nicht verwendet.
- Felder stehen in der gewuenschten Ausgabe-Reihenfolge.
- Feldvalidierung erfolgt mit Methoden wie `validate_title(self, value)`.
- Objektuebergreifende Validierung erfolgt mit `validate(self, attrs)`.

## Views

- Fuer CRUD-Endpunkte werden `ModelViewSet` oder passende DRF-Generics verwendet.
- Fuer individuelle Endpunkte werden `APIView` oder `GenericAPIView` verwendet.
- `queryset` und `serializer_class` stehen als Klassenattribute in der View.
- Dynamische Querysets werden ueber `get_queryset()` umgesetzt.
- Permissions werden explizit mit `permission_classes = [...]` deklariert.

## URLs

- API-Routen sind ressourcenorientiert.
- Beispiel: `/api/boards/42/` statt `/api/getProjectById/`.
- App-URLs werden in den jeweiligen Apps gepflegt.
- Das zentrale Routing in `core/urls.py` bindet die App-URLs ein.

## Permissions und Authentifizierung

- Keine offenen Endpunkte ohne expliziten Grund oder Vorgabe.
- Jede App enthaelt bei Bedarf eine eigene `permissions.py`.
- Permissions werden klar und logisch kombiniert, zum Beispiel `IsAuthenticated` mit Owner- oder Membership-Pruefungen.
- Geschuetzte KanMind-Endpunkte muessen den Zugriff nach Board-Mitgliedschaft, Owner-Rolle oder Autorenschaft pruefen.

## HTTP-Statuscodes

DRF-Standardverhalten soll nicht unnoetig ueberschrieben werden. Die API muss die dokumentierten Statuscodes korrekt liefern.

| Zweck | Statuscode |
| --- | --- |
| Objekt erfolgreich erstellt | `201 CREATED` |
| Kein Inhalt zurueckgegeben | `204 NO CONTENT` |
| Validierungsfehler | `400 BAD REQUEST` |
| Nicht authentifiziert | `401 UNAUTHORIZED` |
| Berechtigung fehlt | `403 FORBIDDEN` |
| Objekt nicht gefunden | `404 NOT FOUND` |

## Technische Zielarchitektur

Empfohlene App-Aufteilung:

- `auth_app` fuer Registrierung, Login und Benutzerabfragen.
- `kanban_app` fuer Boards, Tasks und Kommentare.

Erwartete Kernmodelle:

- User, vorzugsweise Django-User oder kompatibles Custom-User-Modell.
- Board mit `title`, `owner` und `members`.
- Task mit `board`, `title`, `description`, `status`, `priority`, `assignee`, `reviewer`, `due_date` und Ersteller-Referenz.
- Comment mit `task`, `author`, `content` und `created_at`.

Wichtige Validierungsregeln:

- Board-Listen duerfen nur Boards des aktuellen Benutzers enthalten.
- Board-Details sind nur fuer Owner oder Mitglieder sichtbar.
- Board-Loeschung ist nur fuer Owner erlaubt.
- Task-Erstellung und Task-Bearbeitung ist nur fuer Board-Mitglieder erlaubt.
- `assignee` und `reviewer` muessen Mitglieder des Boards sein.
- Eine Task darf per `PATCH` nicht in ein anderes Board verschoben werden.
- Task-Loeschung ist nur fuer Task-Ersteller oder Board-Owner erlaubt.
- Kommentare sind nur fuer Mitglieder des Task-Boards sichtbar und erstellbar.
- Kommentare duerfen nur vom jeweiligen Kommentar-Ersteller geloescht werden.
