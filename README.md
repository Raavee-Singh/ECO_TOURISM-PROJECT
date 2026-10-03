# Eco-Tourism Management Portal for Karnataka

A FastAPI web application for discovering Karnataka destinations, planning trip
budgets, booking tourism services, and managing visitor feedback. It also
provides authorized staff with a data-entry page for aggregate environmental
observations. The interface uses server-rendered Jinja2 templates and a
responsive, nature-inspired CSS design.

## Features

### Visitor accounts

- Register as a visitor, sign in, and sign out.
- Passwords are stored as bcrypt hashes; authentication uses a JWT in an
  HTTP-only cookie.
- View and update profile name and phone number, and change the account
  password.
- Access a personal dashboard with bookings, saved destinations, and reviews.

### Destination discovery and management

- Browse approved destinations and search by name, location, district, or
  description.
- Filter the destination list by category and district.
- View destination details including location, description, entry fee, visiting
  hours, best season, eco rating, map coordinates (when supplied), reviews,
  stays, guides, and activities.
- Signed-in users can submit destination suggestions. Suggestions from
  non-admin users remain pending until reviewed.
- Admins can approve, reject, or delete destinations.
- Signed-in visitors can save approved destinations to their wishlist.

### Stays, guides, activities, and bookings

- Browse available stays, local guides, and destination activities.
- Place authenticated bookings for a stay, guide, or activity.
- Booking prices are calculated on the server from the selected service and
  booking dates, guest count, or room count; submitted totals are not trusted.
- Booking validation checks dates, destination and service association,
  availability, room quantity, and activity group limits.
- View personal bookings and cancel bookings. Admins can cancel any booking.
- Each booking receives a unique reference code and starts with pending status.
- No payment processing or live inventory integration is currently provided.

### Reviews and complaints

- Signed-in visitors can submit destination reviews with a star rating, title,
  and comment.
- Browse recent reviews and filter them by rating.
- A reviewer can delete their own review; admins can delete any review.
- Signed-in visitors can submit complaints and view their own complaint history.
- Admins can view all complaints, post a response, and resolve a complaint.

### Budget planning

- Estimate trip expenses for accommodation, entry fees, food, transport, guides,
  activities, and other costs.
- View a live-updating total in the browser.
- Signed-in users can save budget plans and view their saved plans.

### Environmental observations (admin only)

- Authorized admins can submit destination-linked observations with a timestamp
  and optional trail or zone.
- Available fields cover aggregate visitor activity, waste generation and
  collection, water use and availability, transport, environmental conditions,
  wildlife observations or disturbance reports, and local participation and
  revenue.
- Each observation is labeled as measured, estimated, or mixed. Numeric ranges
  and required fields are validated before saving.
- Admins can browse up to 100 recent records and filter the history by
  destination.
- Records are aggregate; the form is not intended to collect visitor names or
  contact information.
- These observations support research and are not validated ecological
  standards, automated access decisions, or proof of causal relationships.

### Interface, backgrounds, and accessibility

- Responsive pages for the home page, destinations, destination details,
  registration and login, profile, dashboard, reviews, bookings, stays, guides,
  activities, complaints, budget planning, and environmental monitoring.
- A responsive, editorial visual design with local wildlife photography in the
  hero, page backdrops, and the journey section, alongside category navigation,
  destination cards, forms, and tables.
- A sticky translucent header that becomes a light frosted bar while scrolling,
  plus an accessible small-screen navigation menu.
- A Wildlife picker for Auto, Elephants, and Lion-tailed macaque scenes. Manual
  choices are stored in browser local storage; Auto cross-fades between the
  local photographs, with a pause/play control on immersive pages.
- Slow camera-drift motion and image cross-fades add depth without requiring
  video downloads; reduced-motion preferences disable these effects.
- Respect for reduced-motion preferences, visible keyboard focus, a
  skip-to-content link, descriptive image alternatives, and lazy loading for
  destination images.
- Manrope body text and DM Serif Display headings use system font fallbacks.
  Wildlife photos are served locally, not hotlinked.

### Seeded Karnataka nature destinations

The seed catalogue now contains 22 nature-focused entries: the named trails
published by [Karnataka Eco Tourism](https://karnatakaecotourism.com/treks)
(Anthargange, Bidarakatte, Chinaga Betta, Devarayanadurga, Dhamane-Tilari,
Halasagara, Kada View Point, Kaiwara Betta, Makalidurga, Ramadevara Betta,
Sarvodaya, Savandurga, Siddara Betta, Skandagiri, and Tilari Backwater), plus
Bandipur, Bhadra, Biligiri Rangaswamy, Kali, Nagarahole, and Kudremukh forest
destinations and Jog Falls. The official trail details include descriptions for
individual routes; access may change, and Halasagara's page has said "Coming
Soon." This is a researched selection, not a claim to list every forest,
sanctuary, or place open for tourism in Karnataka.

The former Mysore Palace sample record is archived rather than repurposed as a
different place, preserving any historical references while removing it from
the public catalogue. Nagarahole is seeded as its own destination. The catalog
does not invent current prices, opening hours, map coordinates, or
eco-certification: where these are unverified, visitors are directed to check
current official notices. The project seed is upserted on startup, so existing
local databases receive the new destination names without resetting user
accounts.

Research sources:

- [Karnataka Eco Tourism trail catalogue](https://karnatakaecotourism.com/treks)
- [Karnataka Eco Tourism trail listing: Anthargange](https://karnatakaecotourism.com/treks/anthargange)
- [Karnataka Eco Tourism trail listing: Bidarakatte](https://karnatakaecotourism.com/treks/bidarakatte)
- [Karnataka Eco Tourism trail listing: Devarayanadurga](https://karnatakaecotourism.com/treks/devarayanadurga)
- [Karnataka Eco Tourism trail listing: Savandurga](https://karnatakaecotourism.com/treks/savanadurga)
- [Karnataka Eco Tourism trail listing: Siddara Betta](https://karnatakaecotourism.com/treks/siddarabetta)
- [Karnataka Eco Tourism trail listing: Skandagiri](https://karnatakaecotourism.com/treks/skandagiri)
- [National Tiger Conservation Authority](https://ntca.gov.in/tiger-reserves/)

## Roles

| Role | Capabilities |
| --- | --- |
| Visitor | Browse destinations; maintain a profile; save places; book services; create budget plans; submit reviews and complaints. |
| Guide | Uses the account and booking features available to signed-in users; guide listings can be shown for destinations. |
| Admin | Visitor capabilities plus destination moderation, complaint responses, and environmental observation entry and history. |

## Technology

- **Backend:** FastAPI
- **Database and models:** SQLModel with SQLite by default
- **Templates:** Jinja2 server-rendered HTML
- **Frontend:** Plain modular CSS and vanilla JavaScript
- **Authentication:** HTTP-only JWT cookie and bcrypt password hashing
- **Tests:** pytest with FastAPI `TestClient`

## Quick start

Requirements: Python and pip.

1. From the project root, create a virtual environment and activate it:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   On macOS or Linux:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`. Set a unique, high-entropy `SECRET_KEY` before
   using the application beyond local development. The default database URL
   uses SQLite:

   ```dotenv
   DATABASE_URL=sqlite:///./eco_tourism.db
   SECRET_KEY=replace-with-a-long-random-secret
   ALGORITHM=HS256
   APP_NAME=Eco Tourism Management Portal
   ```

4. Start the development server:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open <http://127.0.0.1:8000>.

On startup, the application creates its database tables and inserts demo data
if the seeded admin account is not already present.

## Demo accounts

These credentials are intended only for a local demo. Change or remove seeded
accounts and use a secure `SECRET_KEY` before deploying the application.

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@ecotourism.in` | `admin123` |
| Visitor | `visitor@ecotourism.in` | `visitor123` |
| Guide | `guide@ecotourism.in` | `guide123` |

## Main pages and routes

| Page or action | Route |
| --- | --- |
| Home | `GET /` |
| Register / create account | `GET /register`, `POST /register` |
| Sign in / sign out | `GET /login`, `POST /login`, `POST /logout` |
| Profile / update profile / change password | `GET /profile`, `POST /profile`, `POST /change-password` |
| Destinations / details / suggest a destination | `GET /places`, `GET /places/{place_id}`, `GET /places/add`, `POST /places/add` |
| Save a destination | `POST /places/{place_id}/save` |
| Admin destination moderation | `POST /places/{place_id}/approve`, `/reject`, `/delete` |
| Stays, guides, and activities | `GET /stays`, `GET /guides`, `GET /activities` |
| Create, list, or cancel bookings | `POST /bookings/create`, `GET /bookings`, `POST /bookings/{booking_id}/cancel` |
| Reviews | `GET /reviews`, `POST /places/{place_id}/reviews`, `POST /reviews/{review_id}/delete` |
| Complaints and admin response | `GET /complaints`, `POST /complaints`, `POST /complaints/{complaint_id}/respond` |
| Budget planner | `GET /budget`, `POST /budget` |
| Dashboard | `GET /dashboard` |
| Environmental monitoring (admin only) | `GET /environmental`, `POST /environmental/observations` |

## Project structure

```text
app/
  main.py                 FastAPI app, authentication, shared pages, startup
  config.py               Environment-backed settings
  database.py             SQLModel engine and database initialization
  dependencies.py         Authentication dependencies
  models.py               Database models
  schemas.py              Validated request data
  seed.py                 Local demonstration data
  routers/                Destination, booking, review, complaint, and other routes
  services/               Shared business logic, including booking pricing
  templates/              Jinja2 pages and partials
  static/
    css/                  Modular design system and background styles
    js/                   Browser interactions
    media/                Local scene-media instructions and credits
    images/places/        Locally supplied destination photographs
tests/
  test_smoke.py           Core flow and regression tests
```

## Running tests

From the project root:

```bash
python -m pytest tests/test_smoke.py -q
```

The smoke tests exercise the core rendered pages and workflows, including
registration and login, booking price calculation and validation, admin
complaint responses, environmental observation entry and history, and static
asset delivery.

## Frontend media and credits

The interface uses two locally served wildlife images under
`app/static/media/`: an elephant family near Kabini and a lion-tailed macaque
at Agumbe. They cross-fade in the homepage hero and journey section and appear
as a softened backdrop on interior pages. A slow camera drift and the
pauseable Auto scene rotation add movement; reduced-motion preferences disable
the effects. No background video is bundled.

See [app/static/media/README.md](./app/static/media/README.md) for usage and
[app/static/media/CREDITS.md](./app/static/media/CREDITS.md) for creators,
source pages, download date, and licences.

Add destination files as
`app/static/images/places/<lowercase-name-with-hyphens>.jpg`. Missing photos
fall back to a designed landscape treatment. Keep a creator, source URL,
licence/terms, and download date for every installed stock asset in
[app/static/media/CREDITS.md](./app/static/media/CREDITS.md) and
`app/static/images/places/CREDITS.md`.

The public credits document is available at
[/static/media/credits.html](http://127.0.0.1:8000/static/media/credits.html).
It is served as a static asset so the backend route table remains unchanged.

## Current scope and limitations

- The 22 seeded destinations are a researched selection, not an exhaustive
  government directory or an assurance that every listed trail is currently
  open. Check Forest Department / Karnataka Eco Tourism notices for access,
  permits, fees and operating conditions.
- Destination-specific locally licensed photographs have not yet been added;
  cards use their designed fallback treatment until credited local images are
  supplied.
- The wildlife experience uses local still photographs with cross-fades and a
  subtle camera drift; moving video scenes are not included.
- The `/credits` application route is not added because this frontend/media
  task keeps the FastAPI route table unchanged. Use the static credits page
  linked in the footer for now.
- Environmental collection and history are implemented; sustainability
  dashboards, a calculated Environmental Pressure Index, analytics reports,
  carrying-capacity assessments, and machine-learning predictions are not
  implemented yet.
- The database is initialized with `create_all`; there is no migration system
  for modifying existing tables.
- This project is a functional development/demo portal, not an integrated
  government service. Production deployment would require additional security,
  privacy, operational, accessibility, and data-governance review.
