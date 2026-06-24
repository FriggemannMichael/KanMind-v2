# KanMind Projektanforderungen

Quelle: <https://cdn.developerakademie.com/courses/Backend/EndpointDoku/index.html?name=kanmind>

## Projektziel

KanMind ist ein Backend fuer ein Kanban-/Task-Management-System. Das Backend stellt eine REST API bereit, ueber die Benutzer sich registrieren und anmelden, Boards verwalten, Tasks erstellen und bearbeiten sowie Kommentare zu Tasks pflegen koennen.

## Authentifizierung

Die API nutzt Token-basierte Authentifizierung. Geschuetzte Endpunkte duerfen nur von angemeldeten Benutzern verwendet werden.

### `POST /api/registration/`

Erstellt einen neuen Benutzer.

Request:

```json
{
  "fullname": "Example Username",
  "email": "example@mail.de",
  "password": "examplePassword",
  "repeated_password": "examplePassword"
}
```

Response `201`:

```json
{
  "token": "83bf098723b08f7b23429u0fv8274",
  "fullname": "Example Username",
  "email": "example@mail.de",
  "user_id": 123
}
```

Statuscodes: `201`, `400`, `500`.

Hinweis: `fullname` ist kein Django-`username`; falls noetig muss ein interner Username daraus abgeleitet werden.

### `POST /api/login/`

Authentifiziert einen Benutzer und gibt Token plus Benutzerdaten zurueck.

Request:

```json
{
  "email": "example@mail.de",
  "password": "examplePassword"
}
```

Response `200`:

```json
{
  "token": "83bf098723b08f7b23429u0fv8274",
  "fullname": "Example Username",
  "email": "example@mail.de",
  "user_id": 123
}
```

Statuscodes: `200`, `400`, `500`.

## Boards

Boards haben einen Owner und Mitglieder. Ein Benutzer sieht nur Boards, die er besitzt oder bei denen er Mitglied ist.

### `GET /api/boards/`

Gibt alle Boards zurueck, auf die der aktuelle Benutzer Zugriff hat.

Response `200`:

```json
[
  {
    "id": 1,
    "title": "Projekt X",
    "member_count": 2,
    "ticket_count": 5,
    "tasks_to_do_count": 2,
    "tasks_high_prio_count": 1,
    "owner_id": 12
  }
]
```

Statuscodes: `200`, `401`, `500`.

### `POST /api/boards/`

Erstellt ein Board. Der angemeldete Benutzer wird Owner. Mitglieder werden ueber Benutzer-IDs gesetzt.

Request:

```json
{
  "title": "Neues Projekt",
  "members": [12, 5, 54, 2]
}
```

Response `201` enthaelt Board-ID, Titel, Zaehler und `owner_id`.

Statuscodes: `201`, `400`, `401`, `500`.

### `GET /api/boards/{board_id}/`

Gibt Board-Details inklusive Owner, Mitglieder und Tasks zurueck.

Response `200` enthaelt:

- `id`, `title`, `owner_id`
- `members` mit `id`, `email`, `fullname`
- `tasks` mit `id`, `title`, `description`, `status`, `priority`, `assignee`, `reviewer`, `due_date`, `comments_count`

Statuscodes: `200`, `401`, `403`, `404`, `500`.

Zugriff: Nur Owner oder Board-Mitglieder.

### `PATCH /api/boards/{board_id}/`

Aktualisiert Titel und die vollstaendige Mitgliederliste eines Boards. Dieser Endpunkt ist nicht fuer Task-Aenderungen gedacht.

Request:

```json
{
  "title": "Changed title",
  "members": [1, 54]
}
```

Response `200` enthaelt `id`, `title`, `owner_data` und `members_data`.

Statuscodes: `200`, `400`, `401`, `403`, `404`, `500`.

Zugriff: Owner oder Board-Mitglied.

### `DELETE /api/boards/{board_id}/`

Loescht ein Board. Nur der Owner darf ein Board loeschen.

Statuscodes: `204`, `401`, `403`, `404`, `500`.

Konsequenz: Zugehoerige Tasks und Kommentare werden ebenfalls entfernt.

### `GET /api/email-check/?email={email}`

Prueft, ob eine E-Mail-Adresse zu einem registrierten Benutzer gehoert.

Response `200`:

```json
{
  "id": 1,
  "email": "max.mustermann@example.com",
  "fullname": "Max Mustermann"
}
```

Statuscodes: `200`, `400`, `401`, `404`, `500`.

Zugriff: Nur angemeldete Benutzer.

## Tasks

Tasks gehoeren zu einem Board. Erlaubte Statuswerte sind `to-do`, `in-progress`, `review`, `done`. Erlaubte Prioritaeten sind `low`, `medium`, `high`.

### `GET /api/tasks/assigned-to-me/`

Gibt alle Tasks zurueck, bei denen der aktuelle Benutzer `assignee` ist.

Statuscodes: `200`, `401`, `500`.

### `GET /api/tasks/reviewing/`

Gibt alle Tasks zurueck, bei denen der aktuelle Benutzer `reviewer` ist.

Statuscodes: `200`, `401`, `500`.

### `POST /api/tasks/`

Erstellt eine Task in einem Board.

Request:

```json
{
  "board": 12,
  "title": "Code-Review durchfuehren",
  "description": "Den neuen PR fuer das Feature X ueberpruefen",
  "status": "review",
  "priority": "medium",
  "assignee_id": 13,
  "reviewer_id": 1,
  "due_date": "2025-02-27"
}
```

Response `201` enthaelt die erstellte Task mit aufgeloesten `assignee`- und `reviewer`-Objekten.

Statuscodes: `201`, `400`, `401`, `403`, `404`, `500`.

Regeln:

- Der Benutzer muss Mitglied des Boards sein.
- `assignee` und `reviewer` muessen Board-Mitglieder sein.
- `assignee` und `reviewer` duerfen leer bleiben.

### `PATCH /api/tasks/{task_id}/`

Aktualisiert eine bestehende Task. Die Board-ID darf nicht geaendert werden.

Request-Felder koennen einzeln uebergeben werden:

- `title`
- `description`
- `status`
- `priority`
- `assignee_id`
- `reviewer_id`
- `due_date`

Statuscodes: `200`, `400`, `401`, `403`, `404`, `500`.

Zugriff: Nur Board-Mitglieder.

### `DELETE /api/tasks/{task_id}/`

Loescht eine Task.

Statuscodes: `204`, `400`, `401`, `403`, `404`, `500`.

Zugriff: Nur Task-Ersteller oder Board-Owner.

## Kommentare

Kommentare gehoeren zu einer Task. Der Autor wird aus dem authentifizierten Benutzer bestimmt.

### `GET /api/tasks/{task_id}/comments/`

Gibt alle Kommentare einer Task chronologisch nach Erstellungsdatum zurueck.

Response `200`:

```json
[
  {
    "id": 1,
    "created_at": "2025-02-20T14:30:00Z",
    "author": "Max Mustermann",
    "content": "Das ist ein Kommentar zur Task."
  }
]
```

Statuscodes: `200`, `401`, `403`, `404`, `500`.

Zugriff: Nur Mitglieder des zugehoerigen Boards.

### `POST /api/tasks/{task_id}/comments/`

Erstellt einen Kommentar zu einer Task.

Request:

```json
{
  "content": "Das ist ein neuer Kommentar zur Task."
}
```

Response `201` enthaelt `id`, `created_at`, `author` und `content`.

Statuscodes: `201`, `400`, `401`, `403`, `404`, `500`.

Zugriff: Nur Mitglieder des zugehoerigen Boards.

### `DELETE /api/tasks/{task_id}/comments/{comment_id}/`

Loescht einen Kommentar.

Statuscodes: `204`, `400`, `401`, `403`, `404`, `500`.

Zugriff: Nur der Kommentar-Ersteller.
