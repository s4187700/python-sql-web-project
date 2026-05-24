# Investigating Preventable Infectious Diseases

A web application that explores 25 years of World Health Organization (WHO)
immunisation data, built to make global vaccination and infection statistics
accessible, unbiased, and easy to interpret for a diverse range of users.

This project is submitted as the **Studio Project** for **COSC3107 | COSC3108
— Python Programming Studio** at RMIT University.

---

## Author

| Name           | Student number |
| -------------- | -------------- |
| Nguyen Huynh   | S4187700       |

This is a **single-author submission**. All six pages (sub-tasks A and B
across Levels 1, 2 and 3) are designed, implemented, and documented by the
author named above.

---

## About the project

The "Preventable Infectious Diseases" challenge asks students to build a web
application that lets a wide range of stakeholders — public-health
researchers, parents, students, NGO field officers — explore vaccination and
infection data in a respectful, unbiased, and informative way.

The application is organised into six pages, corresponding to the six
sub-tasks defined in the studio specification:

| Level | Page                     | Sub-task | Purpose                                                                                |
| ----- | ------------------------ | -------- | -------------------------------------------------------------------------------------- |
| 1     | Landing                  | A        | Capture user attention with four high-level facts and the list of tracked diseases.    |
| 1     | Mission                  | B        | Present the site's purpose, the personas it targets, and the project author.           |
| 2     | Vaccination Rates        | A        | Filter coverage by antigen, year, region and country; surface countries at ≥ 90 %.     |
| 2     | Infections × Economy     | B        | Compare disease burden across economic phases and aggregate cases per phase.           |
| 3     | Biggest Improvement      | A        | Rank the top N countries by vaccination-rate jump over a user-selected period.         |
| 3     | Above-Average Infection  | B        | Compute the global infection rate and list countries that exceed it.                   |

### Personas

The application is designed to serve the following four target users, stored
in and retrieved from the database:

- **Public Health Researcher** — analyses global trends to advise policy.
- **Parent / Concerned Citizen** — seeks clear, unbiased facts before making
  decisions for the family.
- **University Student** — studies epidemiology and needs structured data to
  compare countries and regions.
- **NGO Field Officer** — plans immunisation drives in low-income regions
  and needs to identify gaps and at-risk populations.

---

## Technology stack

- **Python 3** with **Flask** — application framework and routing.
- **SQLite** — the WHO immunisation database (`immunisation.db`) provided
  with the studio brief.
- **Jinja2** — server-rendered HTML templates.
- **HTML, CSS, JavaScript** — front-end presentation, animations, and
  scroll-triggered reveals. No front-end framework is used.

All filtering, sorting, aggregation, rate calculation, top-N selection and
global-average computation is performed inside SQL queries. Python is used
only to forward form parameters into prepared statements and to render the
result rows in the templates. Data anomalies such as duplicate rows are
handled defensively in SQL using `AVG()` and `SUM()` inside sub-queries so
that any future duplicate values do not distort calculated rates.

---

## Project structure

```
nguyenhuynh/
├── app.py                                       # Flask application, six routes, all SQL queries
├── immunisation.db                              # WHO immunisation SQLite database
├── ps_milestone_immunization_metadata.xlsx      # Provided database metadata
├── Studio Project Requirements Document.docx    # Provided requirements document
├── templates/
│   ├── base.html                                # Shared layout: header, navigation, footer
│   ├── landing.html                             # Level 1 · Sub-task A
│   ├── mission.html                             # Level 1 · Sub-task B
│   ├── vaccination_rates.html                   # Level 2 · Sub-task A
│   ├── infection_economy.html                   # Level 2 · Sub-task B
│   ├── biggest_improvement.html                 # Level 3 · Sub-task A
│   ├── above_average.html                       # Level 3 · Sub-task B
│   ├── survey.html                              # Usability survey form
│   ├── survey_results.html                      # Survey results summary + submission list
│   └── survey_detail.html                       # Single survey submission detail
├── static/
│   ├── style.css                                # Design system, animations, skeleton loader
│   └── app.js                                   # Scroll-reveal observer and form loading state
├── usability-testing/                           # Usability test materials (PIF, plan, script, survey)
├── .gitignore
└── README.md
```

In addition to the tables provided in the WHO dataset, a few small tables are
created in the same SQLite database to support the application.

Level 1 Sub-task B (Mission page):

- **`Persona`** — stores the four target personas displayed on the Mission
  page.
- **`TeamMember`** — stores the author's name and student number.

Both tables are read from the database at render time, satisfying the
specification that personas and team members must be stored in and retrieved
from the database.

Usability survey (collected during in-class usability testing):

- **`SurveySubmission`** — one row per participant submission (optional
  participant code and a timestamp).
- **`SurveyAnswer`** — one row per answered question, linked to a submission.

The survey is served at `/survey`, an aggregated summary at
`/survey/results`, and each individual submission at
`/survey/results/<id>`.

---

## Running the application

### Prerequisites

- Python 3.10 or newer
- The `flask` package

Install Flask if it is not already available:

```bash
pip install flask
```

### Start the development server

From the project root directory:

```bash
python app.py
```

The application starts on `http://127.0.0.1:5000/`. Open that URL in a web
browser to use the site.

The Flask development server runs in debug mode and will reload
automatically when template or source changes are saved.

---

## How to use the site

1. **Home** — opens the landing page with the four headline facts and the
   list of tracked diseases.
2. **Mission** — presents the project's purpose, the four target personas,
   and the author of the project, all retrieved from the database.
3. **Vaccination Rates** — choose an antigen, year, region and country, then
   apply filters to see countries meeting the WHO ≥ 90 % benchmark and a
   per-region summary.
4. **Infections × Economy** — choose an economic phase, infection type and
   year to view country-level cases per 100,000 inside that phase, plus a
   cross-phase total cases summary.
5. **Biggest Improvement** — choose a start year, end year, antigen and
   Top-N to rank the countries with the largest vaccination-rate jump.
6. **Above-Average** — choose an infection type and year to display the
   global infection rate per 100,000 alongside every country that exceeds
   it. The Global rate anchors the top of the result table.
7. **Survey** — a usability-test feedback form. Responses are stored in the
   database; an aggregated summary is available at `/survey/results`, and
   each individual submission can be viewed in full.

Every results table supports sorting through the **Sort by** filter, with
the ordering performed in SQL.

---

## Database notes

The `immunisation.db` file provided in this repository is the original WHO
immunisation database supplied with the studio brief, extended with the
small `Persona`, `TeamMember`, `SurveySubmission` and `SurveyAnswer` tables
described above. No other modifications have been made to the original schema
or data.

If those tables are missing for any reason, they can be re-created by running
the following snippet once against the database:

```python
import sqlite3
conn = sqlite3.connect("immunisation.db")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS Persona (
    persona_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT,
    description TEXT
)""")
cur.execute("""CREATE TABLE IF NOT EXISTS TeamMember (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    student_number TEXT NOT NULL
)""")
cur.execute("""CREATE TABLE IF NOT EXISTS SurveySubmission (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_code TEXT,
    submitted_at TEXT NOT NULL
)""")
cur.execute("""CREATE TABLE IF NOT EXISTS SurveyAnswer (
    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    question_id TEXT NOT NULL,
    answer_value TEXT,
    FOREIGN KEY (submission_id) REFERENCES SurveySubmission(submission_id)
)""")
conn.commit()
conn.close()
```

The `Persona` rows and the single `TeamMember` row are then inserted with
ordinary `INSERT INTO` statements.

---

## Acknowledgements

- Data source: World Health Organization — Immunization Analysis and
  Insights.
- Course: COSC3107 | COSC3108 — Python Programming Studio, RMIT University.
- Requirements document and provided database: course teaching team.
