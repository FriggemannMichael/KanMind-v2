# KanMind – API-Endpunkt-Katalog (Abnahmeprotokoll)

Quelle: [Endpoint-Dokumentation (Developer Akademie)](https://cdn.developerakademie.com/courses/Backend/EndpointDoku/index.html?name=kanmind)

Basis-URL aller Endpunkte: `/api/`
Authentifizierung: Token-basiert (DRF Token Auth). Sofern nicht anders angegeben, muss der Benutzer angemeldet sein.

## Übersicht

| # | Methode | Pfad | Zweck | Auth |
| --- | --- | --- | --- | --- |
| 1 | POST | `/api/registration/` | Benutzer registrieren | Nein |
| 2 | POST | `/api/login/` | Anmelden, Token erhalten | Nein |
| 3 | GET | `/api/boards/` | Eigene/zugängliche Boards auflisten | Ja |
| 4 | POST | `/api/boards/` | Board erstellen | Ja |
| 5 | GET | `/api/boards/{board_id}/` | Board-Details inkl. Tasks | Mitglied/Owner |
| 6 | PATCH | `/api/boards/{board_id}/` | Board (Titel/Mitglieder) aktualisieren | Mitglied/Owner |
| 7 | DELETE | `/api/boards/{board_id}/` | Board löschen | Owner |
| 8 | GET | `/api/email-check/` | E-Mail-Existenz prüfen | Ja |
| 9 | GET | `/api/tasks/assigned-to-me/` | Mir zugewiesene Tasks | Ja |
| 10 | GET | `/api/tasks/reviewing/` | Tasks, die ich prüfe | Ja |
| 11 | POST | `/api/tasks/` | Task erstellen | Board-Mitglied |
| 12 | PATCH | `/api/tasks/{task_id}/` | Task aktualisieren | Board-Mitglied |
| 13 | DELETE | `/api/tasks/{task_id}/` | Task löschen | Ersteller/Board-Owner |
| 14 | GET | `/api/tasks/{task_id}/comments/` | Kommentare einer Task auflisten | Board-Mitglied |
| 15 | POST | `/api/tasks/{task_id}/comments/` | Kommentar erstellen | Board-Mitglied |
| 16 | DELETE | `/api/tasks/{task_id}/comments/{comment_id}/` | Kommentar löschen | Kommentar-Ersteller |

---

## 1. Authentication

Login und Registrierung

### 1.1 POST `/api/registration/`

**Beschreibung:** Erstellt einen neuen Benutzer.

**URL-Parameter:** keine
**Query-Parameter:** keine

**Request-Beschreibung:** Beachte, dass der `fullname` nicht einem `username` von Django entspricht – dieser muss im Zweifel daraus gebaut werden.

Request Body:

```json
{
  "fullname": "Example Username",
  "email": "example@mail.de",
  "password": "examplePassword",
  "repeated_password": "examplePassword"
}
```

**Response-Beschreibung:** Bei erfolgreicher Erstellung gibt dies ein Token sowie die Benutzerinformationen zurück, inklusive der einzigartigen Nutzer-ID.

Response:

```json
{
  "token": "83bf098723b08f7b23429u0fv8274",
  "fullname": "Example Username",
  "email": "example@mail.de",
  "user_id": 123
}
```

Statuscodes:

- `201` – Der Benutzer wurde erfolgreich erstellt.
- `400` – Ungültige Anfragedaten.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** keine (öffentlich)
**Extra Information:** –

---

### 1.2 POST `/api/login/`

**Beschreibung:** Authentifiziert einen Benutzer und liefert ein Authentifizierungs-Token zurück, das für weitere API-Anfragen genutzt wird.

**URL-Parameter:** keine
**Query-Parameter:** keine

**Request-Beschreibung:** –

Request Body:

```json
{
  "email": "example@mail.de",
  "password": "examplePassword"
}
```

**Response-Beschreibung:** Erfolgreiche Authentifizierung gibt ein Token sowie Benutzerinformationen zurück.

Response:

```json
{
  "token": "83bf098723b08f7b23429u0fv8274",
  "fullname": "Example Username",
  "email": "example@mail.de",
  "user_id": 123
}
```

Statuscodes:

- `200` – Erfolgreiche Anmeldung.
- `400` – Ungültige Anfragedaten.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** keine (öffentlich)
**Extra Information:** –

---

## 2. Boards

Alles zur Bearbeitung, Erstellung und Abruf von Boards

### 2.1 GET `/api/boards/`

**Beschreibung:** Ruft eine Liste von Boards ab, die der angemeldete Benutzer entweder erstellt hat oder zu denen er Mitglied ist.

**URL-Parameter:** keine
**Query-Parameter:** keine

**Request-Beschreibung:** Es werden keine Anfrageparameter benötigt.

**Request Body:** –

**Response-Beschreibung:** Die Antwort enthält eine Liste der Boards mit den grundlegenden Informationen: Titel, ID des Eigentümers, Anzahl der Mitglieder, die generelle Tasks-Anzahl und die Anzahl der Tasks in `to-do` und mit Priorität `high`.

Response:

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
  },
  {
    "id": 1,
    "title": "Projekt Y",
    "member_count": 12,
    "ticket_count": 43,
    "tasks_to_do_count": 12,
    "tasks_high_prio_count": 1,
    "owner_id": 3
  }
]
```

Statuscodes:

- `200` – Erfolgreich. Gibt eine Liste der Boards zurück.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss Mitglied eines der Boards oder der Eigentümer eines Boards sein, um es anzuzeigen.
**Extra Information:** Die Liste der Boards enthält nur die Boards, zu denen der authentifizierte Benutzer Zugriff hat.

---

### 2.2 POST `/api/boards/`

**Beschreibung:** Erstellt ein neues Board und fügt Mitglieder hinzu. Der Benutzer wird automatisch als `owner` erstellt und kann sich selbst als `member` hinzufügen.

**URL-Parameter:** keine
**Query-Parameter:** keine

**Request-Beschreibung:** Die Anfrage erfordert den Titel des Boards und eine Liste von Benutzer-IDs, die als Mitglieder hinzugefügt werden sollen.

Request Body:

```json
{
  "title": "Neues Projekt",
  "members": [12, 5, 54, 2]
}
```

**Response-Beschreibung:** Die Antwort enthält das neu erstellte Board mit grundlegenden Informationen.

Response:

```json
{
  "id": 18,
  "title": "neu",
  "member_count": 4,
  "ticket_count": 0,
  "tasks_to_do_count": 0,
  "tasks_high_prio_count": 0,
  "owner_id": 2
}
```

Statuscodes:

- `201` – Das Board wurde erfolgreich erstellt.
- `400` – Ungültige Anfragedaten. Möglicherweise sind einige Benutzer-Email-Adressen ungültig.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss angemeldet sein, um ein neues Board zu erstellen.
**Extra Information:** –

---

### 2.3 GET `/api/boards/{board_id}/`

**Beschreibung:** Ruft die Informationen eines bestimmten Boards ab, zusammen mit den zugehörigen Tasks.

URL-Parameter:

- `board_id` (erforderlich) – Die ID des Boards, dessen Informationen und zugewiesene Tasks abgerufen werden sollen.

**Query-Parameter:** keine

**Request-Beschreibung:** Es sind keine Anfrageparameter erforderlich.

**Request Body:** `{}`

**Response-Beschreibung:** Die Antwort enthält die Board-Informationen (Titel, Mitglieder) sowie die Tasks, die dem Board zugewiesen sind.

Response:

```json
{
  "id": 1,
  "title": "Projekt X",
  "owner_id": 12,
  "members": [
    { "id": 1, "email": "max.mustermann@example.com", "fullname": "Max Mustermann" },
    { "id": 54, "email": "max.musterfrau@example.com", "fullname": "Maxi Musterfrau" }
  ],
  "tasks": [
    {
      "id": 5,
      "title": "API-Dokumentation schreiben",
      "description": "Die API-Dokumentation für das Backend vervollständigen",
      "status": "to-do",
      "priority": "high",
      "assignee": null,
      "reviewer": { "id": 1, "email": "max.mustermann@example.com", "fullname": "Max Mustermann" },
      "due_date": "2025-02-25",
      "comments_count": 0
    },
    {
      "id": 8,
      "title": "Code-Review durchführen",
      "description": "Den neuen PR für das Feature X überprüfen",
      "status": "review",
      "priority": "medium",
      "assignee": { "id": 1, "email": "max.mustermann@example.com", "fullname": "Max Mustermann" },
      "reviewer": null,
      "due_date": "2025-02-27",
      "comments_count": 0
    }
  ]
}
```

Statuscodes:

- `200` – Erfolgreich. Gibt das Board mit den zugehörigen Tasks zurück.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein, um auf die Ressource zuzugreifen.
- `403` – Verboten. Der Benutzer muss entweder Mitglied des Boards oder der Eigentümer des Boards sein.
- `404` – Board nicht gefunden. Die angegebene Board-ID existiert nicht.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss entweder Mitglied des Boards oder der Eigentümer des Boards sein, um die Informationen und Tasks abzurufen.
**Extra Information:** Die Antwort enthält das Board mit allen Mitgliedern sowie die zugehörigen Tasks.

---

### 2.4 PATCH `/api/boards/{board_id}/`

**Beschreibung:** Aktualisiert die Mitglieder eines bestehenden Boards. Mitglieder können hinzugefügt oder entfernt werden. Der Benutzer, der die Anfrage stellt, muss entweder der Eigentümer des Boards oder ein Mitglied des Boards sein. **Dieser Endpoint ist nicht zum Ändern der Tasks gedacht!**

URL-Parameter:

- `board_id` (erforderlich) – Die ID des Boards, dessen Mitglieder aktualisiert werden sollen.

**Query-Parameter:** keine

**Request-Beschreibung:** Die Anfrage erfordert eine vollständige Liste der Mitglieder-IDs des Boards. Alle nicht in der Liste enthaltenen Mitglieder werden entfernt, während neue hinzugefügt werden.

Request Body:

```json
{
  "title": "Changed title",
  "members": [1, 54]
}
```

**Response-Beschreibung:** Die Antwort enthält das aktualisierte Board mit den neuen Mitgliedern und entfernt nicht benannte Mitglieder.

Response:

```json
{
  "id": 3,
  "title": "Changed title",
  "owner_data": { "id": 1, "email": "max.mustermann@example.com", "fullname": "Max Mustermann" },
  "members_data": [
    { "id": 1, "email": "max.mustermann@example.com", "fullname": "Max Mustermann" },
    { "id": 54, "email": "max.musterfrau@example.com", "fullname": "Maxi Musterfrau" }
  ]
}
```

Statuscodes:

- `200` – Das Board wurde erfolgreich aktualisiert. Mitglieder wurden hinzugefügt und/oder entfernt.
- `400` – Ungültige Anfragedaten. Möglicherweise sind einige Benutzer ungültig.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein, um auf die Ressource zuzugreifen.
- `403` – Verboten. Der Benutzer muss entweder der Eigentümer oder ein Mitglied des Boards sein.
- `404` – Board nicht gefunden. Die angegebene Board-ID existiert nicht.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss entweder der Eigentümer oder ein Mitglied des Boards sein, um Mitglieder hinzuzufügen oder zu entfernen.
**Extra Information:** –

---

### 2.5 DELETE `/api/boards/{board_id}/`

**Beschreibung:** Löscht ein Board. Nur der Eigentümer (Owner) des Boards hat die Berechtigung, das Board zu löschen.

URL-Parameter:

- `board_id` (erforderlich) – Die ID des Boards, das gelöscht werden soll.

**Query-Parameter:** keine

**Request-Beschreibung:** Es sind keine Anfrageparameter erforderlich. Der Benutzer, der das Board löschen möchte, muss der Eigentümer des Boards sein.

**Request Body:** `{}`

**Response-Beschreibung:** Die Antwort bestätigt, dass das Board erfolgreich gelöscht wurde.

**Response:** `null` (kein Inhalt)

Statuscodes:

- `204` – Das Board wurde erfolgreich gelöscht.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein, um auf die Ressource zuzugreifen.
- `403` – Verboten. Der Benutzer muss der Eigentümer des Boards sein, um es zu löschen.
- `404` – Board nicht gefunden. Die angegebene Board-ID existiert nicht.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss der Eigentümer des Boards sein, um es zu löschen.
**Extra Information:** Das Löschen eines Boards entfernt alle zugehörigen Tasks und Kommentare.

---

### 2.6 GET `/api/email-check/`

**Beschreibung:** Prüft, ob eine bestimmte E-Mail-Adresse bereits einem registrierten Benutzer zugeordnet ist.

**URL-Parameter:** keine

Query-Parameter:

- `email` (Typ `email`) – Die E-Mail-Adresse, die überprüft werden soll.

**Request-Beschreibung:** Die E-Mail-Adresse muss als Query-Parameter übergeben werden.

**Request Body:** `{}`

**Response-Beschreibung:** Die Antwort gibt den User zurück, falls dieser existiert.

Response:

```json
{
  "id": 1,
  "email": "max.mustermann@example.com",
  "fullname": "Max Mustermann"
}
```

Statuscodes:

- `200` – Erfolgreich. Gibt zurück, ob die E-Mail existiert.
- `400` – Ungültige Anfrage. Die E-Mail-Adresse fehlt oder hat ein falsches Format.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein.
- `404` – Email nicht gefunden. Die Email existiert nicht.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss angemeldet sein.
**Extra Information:** –

---

## 3. Tasks

Alles zur Bearbeitung, Erstellung und Abruf von Tasks

Erlaubte Werte (gelten für alle Task-Endpunkte):

- **status:** `to-do`, `in-progress`, `review`, `done`
- **priority:** `low`, `medium`, `high`

### 3.1 GET `/api/tasks/assigned-to-me/`

**Beschreibung:** Ruft alle Tasks ab, die dem aktuell authentifizierten Benutzer als Bearbeiter (`assignee`) zugewiesen sind. Der Benutzer muss eingeloggt sein, um auf diese Tasks zuzugreifen.

**URL-Parameter:** keine
**Query-Parameter:** keine

**Request-Beschreibung:** Es sind keine Anfrageparameter erforderlich. Der Benutzer erhält alle Tasks, bei denen er Bearbeiter ist.

**Request Body:** `{}`

**Response-Beschreibung:** Die Antwort enthält eine Liste der Tasks, die dem aktuell authentifizierten Benutzer zugewiesen wurden. Jede Task enthält grundlegende Informationen wie Titel, Status, Priorität und Fälligkeitsdatum.

Response:

```json
[
  {
    "id": 1,
    "board": 1,
    "title": "Task 1",
    "description": "Beschreibung der Task 1",
    "status": "to-do",
    "priority": "high",
    "assignee": { "id": 13, "email": "marie.musterfraun@example.com", "fullname": "Marie Musterfrau" },
    "reviewer": { "id": 1, "email": "max.mustermann@example.com", "fullname": "Max Mustermann" },
    "due_date": "2025-02-25",
    "comments_count": 0
  },
  {
    "id": 2,
    "board": 12,
    "title": "Task 2",
    "description": "Beschreibung der Task 2",
    "status": "in-progress",
    "priority": "medium",
    "assignee": { "id": 13, "email": "marie.musterfraun@example.com", "fullname": "Marie Musterfrau" },
    "reviewer": null,
    "due_date": "2025-02-20",
    "comments_count": 0
  }
]
```

Statuscodes:

- `200` – Erfolgreich. Gibt eine Liste der Tasks zurück, die dem aktuell authentifizierten Benutzer als Bearbeiter zugewiesen sind.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein, um auf diese Tasks zugreifen zu können.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss eingeloggt und authentifiziert sein, um auf die Tasks zuzugreifen, die ihm als Bearbeiter (`assignee`) zugewiesen sind.
**Extra Information:** –

---

### 3.2 GET `/api/tasks/reviewing/`

**Beschreibung:** Ruft alle Tasks ab, bei denen der aktuell authentifizierte Benutzer als Prüfer (`reviewer`) eingetragen ist. Der Benutzer muss eingeloggt sein, um auf diese Tasks zuzugreifen.

**URL-Parameter:** keine
**Query-Parameter:** keine

**Request-Beschreibung:** Es sind keine Anfrageparameter erforderlich. Der Benutzer erhält alle Tasks, bei denen er als Prüfer (`reviewer`) eingetragen ist.

**Request Body:** `{}`

**Response-Beschreibung:** Die Antwort enthält eine Liste der Tasks, die dem authentifizierten Benutzer zur Überprüfung zugewiesen wurden. Jede Task enthält grundlegende Informationen wie Titel, Status, Priorität und Fälligkeitsdatum.

Response:

```json
[
  {
    "id": 1,
    "board": 1,
    "title": "Task 1",
    "description": "Beschreibung der Task 1",
    "status": "to-do",
    "priority": "high",
    "assignee": null,
    "reviewer": { "id": 1, "email": "max.mustermann@example.com", "fullname": "Max Mustermann" },
    "due_date": "2025-02-25",
    "comments_count": 0
  },
  {
    "id": 2,
    "board": 12,
    "title": "Task 2",
    "description": "Beschreibung der Task 2",
    "status": "in-progress",
    "priority": "medium",
    "assignee": { "id": 13, "email": "marie.musterfraun@example.com", "fullname": "Marie Musterfrau" },
    "reviewer": { "id": 1, "email": "max.mustermann@example.com", "fullname": "Max Mustermann" },
    "due_date": "2025-02-20",
    "comments_count": 0
  }
]
```

Statuscodes:

- `200` – Erfolgreich. Gibt eine Liste der Tasks zurück, bei denen der Benutzer als Prüfer (`reviewer`) eingetragen ist.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein, um auf diese Tasks zugreifen zu können.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss eingeloggt und authentifiziert sein, um auf die Tasks zuzugreifen, die ihm als Prüfer (`reviewer`) zugewiesen sind.
**Extra Information:** –

---

### 3.3 POST `/api/tasks/`

**Beschreibung:** Erstellt eine neue Task innerhalb eines Boards. Der Benutzer muss einen der folgenden Werte für den Status nutzen: `to-do`, `in-progress`, `review` oder `done` und einen der folgenden Werte für die Priority: `low`, `medium` oder `high`.

**URL-Parameter:** keine
**Query-Parameter:** keine

**Request-Beschreibung:** Die Anfrage erfordert den Titel der Task, eine optionale Beschreibung, Status, Priorität, Fälligkeitsdatum sowie den zugewiesenen Bearbeiter (`assignee`) und den Prüfer (`reviewer`).

Request Body:

```json
{
  "board": 12,
  "title": "Code-Review durchführen",
  "description": "Den neuen PR für das Feature X überprüfen",
  "status": "review",
  "priority": "medium",
  "assignee_id": 13,
  "reviewer_id": 1,
  "due_date": "2025-02-27"
}
```

**Response-Beschreibung:** Die Antwort enthält die erstellte Task mit allen zugehörigen Informationen.

Response:

```json
{
  "id": 10,
  "board": 12,
  "title": "Code-Review durchführen",
  "description": "Den neuen PR für das Feature X überprüfen",
  "status": "review",
  "priority": "medium",
  "assignee": { "id": 13, "email": "marie.musterfraun@example.com", "fullname": "Marie Musterfrau" },
  "reviewer": { "id": 1, "email": "max.mustermann@example.com", "fullname": "Max Mustermann" },
  "due_date": "2025-02-27",
  "comments_count": 0
}
```

Statuscodes:

- `201` – Die Task wurde erfolgreich erstellt.
- `400` – Ungültige Anfragedaten. Möglicherweise fehlen erforderliche Felder oder enthalten ungültige Werte.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein.
- `403` – Verboten. Der Benutzer muss Mitglied des Boards sein, um eine Task zu erstellen.
- `404` – Board nicht gefunden. Die angegebene Board-ID existiert nicht.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss Mitglied des Boards sein, um eine Task zu erstellen.
**Extra Information:** Sowohl `assignee` als auch `reviewer` müssen Mitglieder des Boards sein. Falls kein `assignee` oder `reviewer` angegeben wird, bleibt das Feld leer.

---

### 3.4 PATCH `/api/tasks/{task_id}/`

**Beschreibung:** Aktualisiert eine bestehende Task. Nur Mitglieder des Boards, zu dem die Task gehört, können sie bearbeiten.

URL-Parameter:

- `task_id` (erforderlich) – Die ID der zu aktualisierenden Task.

**Query-Parameter:** keine

**Request-Beschreibung:** Die Anfrage kann einen oder mehrere der folgenden Parameter enthalten: Titel, Beschreibung, Status, Priorität, Fälligkeitsdatum, Bearbeiter (`assignee`) und Prüfer (`reviewer`).

Request Body:

```json
{
  "title": "Code-Review abschließen",
  "description": "Den PR fertig prüfen und Feedback geben",
  "status": "done",
  "priority": "high",
  "assignee_id": 13,
  "reviewer_id": 1,
  "due_date": "2025-02-28"
}
```

**Response-Beschreibung:** Die Antwort enthält die aktualisierte Task mit allen geänderten Werten.

Response:

```json
{
  "id": 10,
  "title": "Code-Review abschließen",
  "description": "Den PR fertig prüfen und Feedback geben",
  "status": "done",
  "priority": "high",
  "assignee": { "id": 13, "email": "marie.musterfraun@example.com", "fullname": "Marie Musterfrau" },
  "reviewer": { "id": 1, "email": "max.mustermann@example.com", "fullname": "Max Mustermann" },
  "due_date": "2025-02-28"
}
```

Statuscodes:

- `200` – Die Task wurde erfolgreich aktualisiert.
- `400` – Ungültige Anfragedaten. Möglicherweise sind einige Werte ungültig oder nicht erlaubt.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein.
- `403` – Verboten. Der Benutzer muss Mitglied des Boards sein, zu dem die Task gehört.
- `404` – Task nicht gefunden. Die angegebene Task-ID existiert nicht.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss Mitglied des Boards sein, um eine Task zu aktualisieren. Das Ändern der Board-ID (`board`) ist nicht erlaubt!
**Extra Information:** Felder, die nicht aktualisiert werden sollen, können weggelassen werden. `assignee` und `reviewer` müssen weiterhin Mitglieder des Boards sein.

---

### 3.5 DELETE `/api/tasks/{task_id}/`

**Beschreibung:** Löscht eine bestehende Task. Nur der Ersteller der Task oder der Eigentümer des Boards kann die Task löschen.

URL-Parameter:

- `task_id` (erforderlich) – Die ID der zu löschenden Task.

**Query-Parameter:** keine

**Request-Beschreibung:** Es sind keine Anfrageparameter erforderlich.

**Request Body:** `{}`

**Response-Beschreibung:** Wenn die Task erfolgreich gelöscht wurde, wird eine Bestätigung ohne Inhalt zurückgegeben.

**Response:** `null` (kein Inhalt)

Statuscodes:

- `204` – Die Task wurde erfolgreich gelöscht.
- `400` – Ungültige Anfragedaten. Die übermittelte Task-ID ist fehlerhaft.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein.
- `403` – Verboten. Nur der Ersteller der Task oder der Board-Eigentümer kann die Task löschen.
- `404` – Task nicht gefunden. Die angegebene Task-ID existiert nicht.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Nur der Ersteller der Task oder der Eigentümer des Boards kann eine Task löschen.
**Extra Information:** Die Löschung ist dauerhaft und kann nicht rückgängig gemacht werden.

---

### 3.6 GET `/api/tasks/{task_id}/comments/`

**Beschreibung:** Ruft alle Kommentare ab, die einer bestimmten Task zugeordnet sind.

URL-Parameter:

- `task_id` (erforderlich) – Die ID der Task, zu der die Kommentare abgerufen werden sollen.

**Query-Parameter:** keine

**Request-Beschreibung:** Es sind keine Anfrageparameter erforderlich.

**Request Body:** `{}`

**Response-Beschreibung:** Die Antwort enthält eine Liste aller Kommentare zur angegebenen Task. Jeder Kommentar enthält das Erstellungsdatum, den vollständigen Namen des Autors und den Inhalt.

Response:

```json
[
  {
    "id": 1,
    "created_at": "2025-02-20T14:30:00Z",
    "author": "Max Mustermann",
    "content": "Das ist ein Kommentar zur Task."
  },
  {
    "id": 2,
    "created_at": "2025-02-21T09:15:00Z",
    "author": "Erika Musterfrau",
    "content": "Ein weiterer Kommentar zur Diskussion."
  }
]
```

Statuscodes:

- `200` – Erfolgreich. Gibt eine Liste der Kommentare zurück.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein.
- `403` – Verboten. Der Benutzer muss Mitglied des Boards sein, zu dem die Task gehört.
- `404` – Task nicht gefunden. Die angegebene Task-ID existiert nicht.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss Mitglied des Boards sein, zu dem die Task gehört.
**Extra Information:** Die Kommentare sind chronologisch nach Erstellungsdatum sortiert.

---

### 3.7 POST `/api/tasks/{task_id}/comments/`

**Beschreibung:** Erstellt einen neuen Kommentar zu einer bestimmten Task. Der Autor wird automatisch anhand der Authentifizierung bestimmt.

URL-Parameter:

- `task_id` (erforderlich) – Die ID der Task, zu der der Kommentar hinzugefügt werden soll.

**Query-Parameter:** keine

**Request-Beschreibung:** Die Anfrage erfordert den Inhalt (`content`) des Kommentars. Der Ersteller wird automatisch aus der Authentifizierung übernommen.

Request Body:

```json
{
  "content": "Das ist ein neuer Kommentar zur Task."
}
```

**Response-Beschreibung:** Die Antwort enthält die erstellte Kommentarinstanz mit ID, Erstellungsdatum, vollständigem Namen des Autors und dem Inhalt.

Response:

```json
{
  "id": 15,
  "created_at": "2025-02-20T15:00:00Z",
  "author": "Max Mustermann",
  "content": "Das ist ein neuer Kommentar zur Task."
}
```

Statuscodes:

- `201` – Der Kommentar wurde erfolgreich erstellt.
- `400` – Ungültige Anfragedaten. Möglicherweise ist der `content`-Wert leer.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein.
- `403` – Verboten. Der Benutzer muss Mitglied des Boards sein, zu dem die Task gehört.
- `404` – Task nicht gefunden. Die angegebene Task-ID existiert nicht.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Der Benutzer muss Mitglied des Boards sein, zu dem die Task gehört.
**Extra Information:** Der Autor des Kommentars wird aus der Authentifizierung des aktuellen Benutzers bestimmt.

---

### 3.8 DELETE `/api/tasks/{task_id}/comments/{comment_id}/`

**Beschreibung:** Löscht einen Kommentar einer bestimmten Task. Nur der Ersteller des Kommentars kann ihn löschen.

URL-Parameter:

- `task_id` (erforderlich) – Die ID der Task, zu der der Kommentar gehört.
- `comment_id` (erforderlich) – Die ID des zu löschenden Kommentars.

**Query-Parameter:** keine

**Request-Beschreibung:** Es sind keine zusätzlichen Anfrageparameter erforderlich.

**Request Body:** `{}`

**Response-Beschreibung:** Bei erfolgreicher Löschung wird eine leere Antwort mit Statuscode `204` zurückgegeben.

**Response:** `null` (kein Inhalt)

Statuscodes:

- `204` – Der Kommentar wurde erfolgreich gelöscht.
- `400` – Ungültige Anfragedaten.
- `401` – Nicht autorisiert. Der Benutzer muss eingeloggt sein.
- `403` – Verboten. Nur der Ersteller des Kommentars darf ihn löschen.
- `404` – Kommentar oder Task nicht gefunden.
- `500` – Interner Serverfehler.

**Rate Limits:** Kein Limit
**Permissions:** Nur der Benutzer, der den Kommentar erstellt hat, darf ihn löschen.
**Extra Information:** Falls der Kommentar oder die Task nicht existiert, wird ein `404`-Fehler zurückgegeben.
