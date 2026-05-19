# Presentation Script — Investigating Preventable Infectious Diseases

**Course:** COSC3107 | COSC3108 — Python Programming Studio
**Author:** Nguyen Huynh · S4187700
**Duration:** 10 minutes
**Format:** Live demo + narration

---

## Time budget

| Section | Duration | Cumulative |
| ------- | -------- | ---------- |
| 1. Opening — the problem & who it's for | 1:00 | 1:00 |
| 2. Personas — the people I designed for | 1:30 | 2:30 |
| 3. Level 1 demo — Big Picture (Landing + Mission) | 1:30 | 4:00 |
| 4. Level 2 demo — Shallow Glance (Vaccination Rates + Infections × Economy) | 2:00 | 6:00 |
| 5. Level 3 demo — Deep Dive (Biggest Improvement + Above-Average) | 2:00 | 8:00 |
| 6. Tech stack & engineering decisions | 1:30 | 9:30 |
| 7. Closing | 0:30 | 10:00 |

---

## 1 · Opening — the problem & who it's for *(1:00)*

> "Vaccination is one of humanity's most effective public-health interventions
> — yet the conversation around it is full of strong opinions and very few
> shared facts.
>
> The World Health Organization publishes 25 years of immunisation data
> covering 217 countries, but for most people that data is locked behind
> spreadsheets and technical reports.
>
> The challenge of this studio project was to build a web application that
> lets very different kinds of users — a researcher, a parent, a student, an
> NGO worker — explore that same dataset and walk away better informed,
> without anyone telling them what to think.
>
> That is what I have built."

**On screen:** the landing page.

---

## 2 · Personas — the people I designed for *(1:30)*

This is the centre of the project. Every design decision flows from these
four personas, all stored in the database and retrieved by the Mission page.

> "Before I wrote any SQL, I defined four personas. Each one needs the same
> dataset, but they read it for completely different reasons."

| Persona | What they need from the site |
| ------- | --------------------------------- |
| **Dr. Anna Pham** — Public Health Researcher | Cross-country comparisons, trends over decades, ability to drill from regional summaries into country detail. |
| **Mark Tran** — Parent / Concerned Citizen | Clear, unbiased high-level facts. He does not want to write SQL — he wants honest numbers presented respectfully. |
| **Linh Nguyen** — University Student | Structured filters, sortable tables, the ability to compare a country to its region or its economic peers. |
| **Sara Okafor** — NGO Field Officer | Identify the worst-affected countries quickly. Where is the gap? Who is above the global average? |

> "The User-Centered Design process started with one question for each
> persona: 'what does success look like for you on this site?' Those four
> answers drove the six pages of the application."

**On screen:** click "Mission" — show the four personas reading from the
database. Mention that the team member (myself) is also stored in the
database, satisfying that part of the brief.

---

## 3 · Level 1 demo — Big Picture *(1:30)*

> "Level 1 is the first thing every persona sees. It has one job: build trust
> in 5 seconds."

### Landing (Sub-task A)

**On screen:** scroll through landing.

> "Four cards, four facts — pulled from the database in a single SQL
> statement. The timeframe, the total doses, the total reported cases, and
> the number of countries.
>
> Below that is the list of every disease the site covers, then a short
> 'how to navigate' guide.
>
> This is for Mark Tran — the parent. He doesn't need to filter anything
> yet. He just needs to know what this site is and decide whether to keep
> reading."

### Mission (Sub-task B)

**On screen:** scroll Mission.

> "Mission is where I'm transparent with the user about who this site is
> for. Four personas, the team behind the project — and crucially, both of
> those are *read from the database*, not hardcoded in HTML."

---

## 4 · Level 2 demo — Shallow Glance *(2:00)*

> "Level 2 is where the user moves from passive reading to active
> exploration. Here I'm designing for Dr. Pham and Linh — they want to
> filter."

### Vaccination Rates (Sub-task A)

**On screen:** open Vaccination Rates, default to MCV1 / 2020.

> "Two tables. Table 1 lists every country at or above the WHO 90 % herd-
> immunity benchmark for a chosen antigen and year. Table 2 aggregates that
> same data — for each region, how many countries hit 90 %?
>
> The filters let me narrow by region, country, or sort by coverage, country
> or region. Every filter is server-side SQL — no JavaScript filtering,
> nothing post-processed in Python."

**Demonstrate:** change antigen to MCV2, change year to 2010, change sort
order. Show the table-row reveal animation.

> "Notice the subtle reveals — they are not decoration. When a researcher
> changes a filter, the loading bar at the top and the skeleton placeholders
> in the table cells give immediate feedback that the system is working.
> That is a deliberate UX choice from the persona for Dr. Pham, who is
> sceptical when a tool feels frozen."

### Infections × Economy (Sub-task B)

**On screen:** open Infections × Economy.

> "This page answers a different question: does economic phase correlate
> with disease burden? I pick an economic phase, an infection type and a
> year. The first table is country-level — cases per 100,000 inside that
> phase. The second is the cross-phase summary, joining InfectionData,
> Country and Economy in a single query.
>
> This page is for Sara Okafor — the NGO officer. She is looking for the
> low-income, high-burden combinations that need help most."

**Demonstrate:** Measles, Low Income, 2022 → sort by Rate descending.

---

## 5 · Level 3 demo — Deep Dive *(2:00)*

> "Level 3 is where the SQL gets serious. The brief explicitly says: use
> the result of one query to find another sub-dataset, do it in a single
> efficient query, sort in SQL, do not post-process in Python.
>
> I want to walk through how I did that on both pages."

### Biggest Improvement (Sub-task A)

**On screen:** open Biggest Improvement, MCV1, 2000 → 2024, Top 10.

> "The vaccination rate at the start year and the end year, the difference,
> and the Top-N — all of that is one query with two CTEs and a LIMIT clause.
>
> The 'Visual' you saw in earlier versions was deliberately removed because
> some rates legitimately exceed 100 % when doses outpace population
> estimates. I trust the user to read the number, not a clipped bar."

**Demonstrate:** change to DTPCV3, change Top N to 5, change sort to
"End rate (high → low)".

> "Every sort option is mapped to a whitelisted ORDER BY fragment — no raw
> user input ever touches the SQL. That is both a security and a
> top-marks-criterion concern."

### Above-Average Infection (Sub-task B)

**On screen:** open Above-Average, Measles, 2020.

> "This page computes the *global* infection rate per 100,000 people and
> every country that exceeds it — all in one SQL statement.
>
> The Global row anchors the table because the brief asked for it at the
> top of the result table. I used a UNION ALL inside a CTE so SQLite
> handles the ordering, not Python.
>
> And I added a 'Closest to global rate' sort — that's the similarity sort
> the brief mentions. SQL `ABS(rate - global_rate)` does the work."

**Demonstrate:** switch sort to "Closest to global rate" — show the
similarity ranking.

> "This page is for Dr. Pham again — she wants to know which countries are
> outliers, and how far out they are. The ×N column tells her how many
> times the global rate a country sits at."

---

## 6 · Tech stack & engineering decisions *(1:30)*

> "I want to spend a minute on the engineering. Three deliberate choices."

### Choice 1 — Flask + raw SQL, no ORM

> "I did not use SQLAlchemy or any ORM. The brief explicitly rewards
> writing efficient JOINs, GROUP BYs, sub-queries and CTEs. An ORM would
> have hidden those — and I would have lost the marks. So the stack is:
>
> - **Python 3 + Flask** for routing and templating
> - **SQLite** — the database provided with the brief
> - **Jinja2** for server-rendered HTML
> - **HTML, CSS, JavaScript** — no frontend framework"

### Choice 2 — Every calculation lives in SQL

> "Filtering, sorting, rate calculation, top-N, global averages — they are
> all SQL. Python only forwards form parameters into prepared statements
> and renders the result rows. That is a direct response to the brief's
> requirement to avoid post-processing in Python.
>
> I also defensively wrap aggregations in `AVG()` and `SUM()` inside
> sub-queries so that if the database ever contains duplicate fact rows,
> the rate calculations stay correct."

### Choice 3 — Design system with progressive enhancement

> "The CSS is a self-contained design system — variables for colour,
> spacing, typography. Animations use `IntersectionObserver` for scroll
> reveals and CSS keyframes for stagger effects, but the site is fully
> usable without JavaScript and respects `prefers-reduced-motion` for
> accessibility.
>
> That is the design-pattern thinking from earlier in the semester:
> separate concerns, degrade gracefully, never block the data on the
> presentation."

---

## 7 · Closing *(0:30)*

> "Six pages, four personas, one database, one consistent design language.
>
> Every Level-3 query is a single statement. Every persona has at least one
> page that exists specifically for them. Every filter you saw is SQL, not
> Python.
>
> This is what the studio brief asked for, and this is what I built. Thank
> you — happy to take questions."

---

## Live-demo checklist *(run through before the presentation)*

- [ ] `python app.py` running, browser open at `http://127.0.0.1:5000/`
- [ ] Browser zoom set to 110 % so the room can read tables
- [ ] All six pages cached (visit each once before starting)
- [ ] DevTools closed
- [ ] Notifications, Slack, email muted
- [ ] Backup screenshots saved in case Wi-Fi fails

## Sample filter values to demo *(rehearsed combinations)*

| Page | Filter values | What it shows |
| ---- | ------------- | ------------- |
| Vaccination Rates | MCV1, 2020, all regions, sort Coverage ↓ | Strong herd-immunity countries |
| Vaccination Rates | MCV2, 2010, Western/Europe, sort Region | Regional pattern |
| Infections × Economy | Low Income, Measles, 2022, sort Rate ↓ | NGO persona use case |
| Infections × Economy | High Income, Rubella, 2010, sort Cases ↓ | Counter-intuitive economy story |
| Biggest Improvement | MCV1, 2000 → 2024, Top 10, sort Improvement ↓ | Sierra Leone, South Sudan etc. |
| Biggest Improvement | DTPCV3, 2010 → 2024, Top 5, sort End rate | High-performers today |
| Above-Average | Measles, 2020, sort Rate ↓ | DRC at the top |
| Above-Average | Measles, 2020, sort similarity | Closest to global benchmark |

## Likely questions & prepared answers

**Q: Why SQLite instead of PostgreSQL or MySQL?**
A: The brief provided the dataset as a SQLite file. Using anything else
would mean migrating the data and arguing that the migration was lossless —
that is wasted effort. SQLite supports every SQL feature the brief
required: CTEs, window functions, sub-queries, UNION, AGGREGATE.

**Q: How do you handle duplicate rows in the dataset?**
A: Inside every rate calculation I collapse the fact table with `AVG()` or
`SUM()` in a sub-query before the division. The current database has no
duplicates, but the code stays correct if duplicates appear later.

**Q: How do you prevent SQL injection?**
A: Every dynamic value goes through a parameterised placeholder. The only
strings I concatenate into SQL are ORDER BY fragments, and those come from
a hard-coded whitelist — never directly from form input.

**Q: Why did you remove the bar charts?**
A: Some vaccination rates legitimately exceed 100 % in the dataset (doses
administered to non-resident populations, or population estimate lag). A
clipped bar would either mislead or confuse. The number is honest; the
number stays.

**Q: Is this a multi-person project?**
A: No — single-author. Both my name and student number are stored in the
TeamMember table and rendered on the Mission page from the database, in
line with the brief.
