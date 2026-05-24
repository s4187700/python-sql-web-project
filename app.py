"""
Investigating Preventable Infectious Diseases
Flask web application — 6 pages (Levels 1A/1B, 2A/2B, 3A/3B).

Design rules followed throughout:
  * All computation (rates, averages, filtering, sorting, top-N, global rate)
    is done in SQL. Python only forwards form parameters and renders results.
  * Duplicate rows in fact tables are collapsed with AVG()/SUM() inside
    sub-queries before any rate calculation, so the result is correct even
    if the database later contains repeated rows for the same key.
  * Single-query design wherever possible (CTEs, sub-queries, UNION ALL).
"""
import sqlite3
from datetime import datetime, timezone
from flask import Flask, render_template, request, g, redirect, url_for

DB_PATH = "immunisation.db"
app = Flask(__name__)


def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


def query(sql, args=()):
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return rows


# Whitelisted ORDER BY fragments — never interpolate raw user text into SQL.
def safe_order(value, mapping, default_key):
    return mapping.get(value, mapping[default_key])


# ---------------- LEVEL 1 ----------------

@app.route("/")
def landing():
    """Sub-Task A — Landing page.

    All 4 headline facts (year range, total doses, total cases, country count)
    plus the disease list are produced by SQL. The 4 numeric facts are computed
    in one SQL statement using sub-queries — Python only renders them.
    """
    facts = query("""
        SELECT
            (SELECT MIN(year) FROM Vaccination)          AS year_lo,
            (SELECT MAX(year) FROM Vaccination)          AS year_hi,
            (SELECT SUM(doses) FROM Vaccination)         AS total_doses,
            (SELECT SUM(cases) FROM InfectionData)       AS total_cases,
            (SELECT COUNT(*) FROM Country)               AS n_countries
    """)[0]

    diseases = query("SELECT description FROM Infection_Type ORDER BY description")
    return render_template(
        "landing.html",
        year_lo=facts["year_lo"],
        year_hi=facts["year_hi"],
        total_doses=facts["total_doses"] or 0,
        total_cases=facts["total_cases"] or 0,
        n_countries=facts["n_countries"],
        diseases=[d["description"] for d in diseases],
    )


@app.route("/mission")
def mission():
    """Sub-Task B — Mission, personas, team. Personas and team retrieved from DB."""
    personas = query("SELECT name, role, description FROM Persona ORDER BY persona_id")
    team = query("SELECT name, student_number FROM TeamMember ORDER BY member_id")
    return render_template("mission.html", personas=personas, team=team)


# ---------------- LEVEL 2 ----------------

@app.route("/vaccination-rates", methods=["GET"])
def vaccination_rates():
    """Sub-Task A — Vaccination rates with herd-immunity (≥90%) summaries.

    Both result tables are built by SQL. Duplicate (antigen,country,year) rows
    are collapsed with AVG(coverage) inside an inner sub-query so the outer
    HAVING / COUNT operates on one representative value per country.
    """
    antigens = query("SELECT AntigenID, name FROM Antigen ORDER BY AntigenID")
    regions = query("SELECT RegionID, region FROM Region ORDER BY region")
    countries = query("SELECT CountryID, name FROM Country ORDER BY name")
    years = query("SELECT YearID FROM YearDate ORDER BY YearID")

    antigen = request.args.get("antigen", "MCV1")
    year = request.args.get("year", type=int, default=2020)
    region = request.args.get("region", "")
    country = request.args.get("country", "")

    sort_by = request.args.get("sort_by", "cov_desc")
    order_t1 = safe_order(sort_by, {
        "cov_desc":    "coverage DESC, country ASC",
        "cov_asc":     "coverage ASC, country ASC",
        "country_asc": "country ASC",
        "region_asc":  "region ASC, coverage DESC",
    }, "cov_desc")

    # Optional country / region filters are appended as parameterised clauses.
    extra = ""
    extra_params = []
    if region:
        extra += " AND c.region = ?"
        extra_params.append(region)
    if country:
        extra += " AND c.CountryID = ?"
        extra_params.append(country)

    # Table 1: per-country average coverage, filtered to ≥ 90%.
    sql1 = f"""
        SELECT c.name AS country,
               COALESCE(r.region, '—') AS region,
               AVG(v.coverage) AS coverage
        FROM Vaccination v
        JOIN Country c       ON c.CountryID = v.country
        LEFT JOIN Region r   ON r.RegionID  = c.region
        WHERE v.antigen = ?
          AND v.year = ?
          AND v.coverage IS NOT NULL
          {extra}
        GROUP BY c.CountryID
        HAVING AVG(v.coverage) >= 90
        ORDER BY {order_t1}
    """
    table1 = query(sql1, [antigen, year, *extra_params])

    # Table 2: per region, number of countries whose averaged coverage ≥ 90%.
    # Inner sub-query collapses duplicates before the outer COUNT runs.
    sql2 = """
        SELECT r.region AS region,
               COUNT(v.country) AS countries_meeting,
               (SELECT COUNT(*) FROM Country c2 WHERE c2.region = r.RegionID)
                   AS total_countries
        FROM Region r
        LEFT JOIN Country c ON c.region = r.RegionID
        LEFT JOIN (
            SELECT country, AVG(coverage) AS cov
            FROM Vaccination
            WHERE antigen = ? AND year = ? AND coverage IS NOT NULL
            GROUP BY country
            HAVING AVG(coverage) >= 90
        ) v ON v.country = c.CountryID
        GROUP BY r.RegionID
        ORDER BY countries_meeting DESC, r.region ASC
    """
    table2 = query(sql2, [antigen, year])

    return render_template(
        "vaccination_rates.html",
        antigens=antigens, regions=regions, countries=countries, years=years,
        antigen=antigen, year=year, region=region, country=country,
        sort_by=sort_by, table1=table1, table2=table2,
    )


@app.route("/infection-economy", methods=["GET"])
def infection_economy():
    """Sub-Task B — Infections per 100,000 per country in a chosen economic phase,
    plus a cross-economy summary that combines multiple tables in one query.
    Duplicate fact rows are collapsed with AVG()/SUM() before the rate division.
    """
    economies = query("SELECT economyID, phase FROM Economy ORDER BY economyID")
    inf_types = query("SELECT id, description FROM Infection_Type ORDER BY description")
    years = query("SELECT YearID FROM YearDate ORDER BY YearID")

    economy = request.args.get("economy", type=int, default=1)
    inf_type = request.args.get("inf_type", "MEA")
    year = request.args.get("year", type=int, default=2022)
    sort_by = request.args.get("sort_by", "rate_desc")

    order_sql = safe_order(sort_by, {
        "rate_desc":   "rate DESC NULLS LAST, country ASC",
        "rate_asc":    "rate ASC  NULLS LAST, country ASC",
        "country_asc": "country ASC",
        "country_desc":"country DESC",
        "cases_desc":  "cases DESC NULLS LAST, country ASC",
        "cases_asc":   "cases ASC  NULLS LAST, country ASC",
    }, "rate_desc")

    # Detail: country-level rate. Inner sub-queries use SUM()/AVG() so any
    # duplicate rows for the same (country,year) collapse to one value.
    sql_detail = f"""
        SELECT c.name      AS country,
               e.phase     AS economic_phase,
               it.description AS infection,
               i.cases     AS cases,
               p.population AS population,
               CASE WHEN p.population > 0
                    THEN (i.cases * 100000.0) / p.population
                    ELSE NULL END AS rate
        FROM Country c
        JOIN Economy e        ON e.economyID = c.economy
        JOIN Infection_Type it ON it.id = ?
        LEFT JOIN (
            SELECT inf_type, country, year, SUM(cases) AS cases
            FROM InfectionData
            WHERE inf_type = ? AND year = ?
            GROUP BY inf_type, country, year
        ) i ON i.country = c.CountryID
        LEFT JOIN (
            SELECT country, year, AVG(population) AS population
            FROM CountryPopulation
            WHERE year = ?
            GROUP BY country, year
        ) p ON p.country = c.CountryID
        WHERE c.economy = ?
          AND i.cases IS NOT NULL
        ORDER BY {order_sql}
    """
    detail = query(sql_detail, [inf_type, inf_type, year, year, economy])

    # Cross-table summary — total cases per economic phase for the chosen
    # infection and year. Combines InfectionData + Country + Economy.
    summary = query("""
        SELECT e.phase AS economic_phase,
               SUM(i.cases) AS total_cases,
               COUNT(DISTINCT c.CountryID) AS n_countries
        FROM InfectionData i
        JOIN Country c ON c.CountryID = i.country
        JOIN Economy e ON e.economyID = c.economy
        WHERE i.inf_type = ? AND i.year = ?
        GROUP BY e.economyID
        ORDER BY e.economyID
    """, [inf_type, year])

    # Friendly labels resolved in SQL inside the row data, but we need a
    # page-title version too — taken from the detail rows when present,
    # otherwise from Infection_Type via a tiny lookup.
    inf_name_row = query("SELECT description FROM Infection_Type WHERE id = ?", [inf_type])
    inf_name = inf_name_row[0]["description"] if inf_name_row else inf_type

    economy_name_row = query("SELECT phase FROM Economy WHERE economyID = ?", [economy])
    economy_name = economy_name_row[0]["phase"] if economy_name_row else str(economy)

    return render_template(
        "infection_economy.html",
        economies=economies, inf_types=inf_types, years=years,
        economy=economy, inf_type=inf_type, year=year, sort_by=sort_by,
        detail=detail, summary=summary,
        inf_name=inf_name, economy_name=economy_name,
    )


# ---------------- LEVEL 3 ----------------

@app.route("/biggest-improvement", methods=["GET"])
def biggest_improvement():
    """Sub-Task A — Top-N countries by vaccination-rate jump over a period.

    Rate = doses / population × 100. SUM(doses) and AVG(population) inside the
    sub-queries are defensive against duplicate fact rows. Top-N selection and
    ordering are done entirely in SQL.
    """
    antigens = query("SELECT AntigenID, name FROM Antigen ORDER BY AntigenID")
    years = query("SELECT YearID FROM YearDate ORDER BY YearID")

    start_year = request.args.get("start_year", type=int, default=2000)
    end_year   = request.args.get("end_year", type=int, default=2024)
    antigen    = request.args.get("antigen", "MCV1")
    top_n_raw  = request.args.get("top_n", type=int, default=10)
    sort_by    = request.args.get("sort_by", "imp_desc")

    # Clamp top_n into a sane range — guards the LIMIT clause.
    top_n = max(1, min(50, top_n_raw or 10))

    order_sql = safe_order(sort_by, {
        "imp_desc":    "improvement DESC, country ASC",
        "imp_asc":     "improvement ASC,  country ASC",
        "country_asc": "country ASC",
        "end_desc":    "end_rate DESC, country ASC",
    }, "imp_desc")

    results = []
    valid_range = start_year < end_year
    if valid_range:
        sql = f"""
            WITH start_rate AS (
                SELECT v.country AS country,
                       (SUM(v.doses) * 100.0) / AVG(p.population) AS rate
                FROM Vaccination v
                JOIN CountryPopulation p
                  ON p.country = v.country AND p.year = v.year
                WHERE v.antigen = ?
                  AND v.year = ?
                  AND v.doses IS NOT NULL
                  AND p.population > 0
                GROUP BY v.country
            ),
            end_rate AS (
                SELECT v.country AS country,
                       (SUM(v.doses) * 100.0) / AVG(p.population) AS rate
                FROM Vaccination v
                JOIN CountryPopulation p
                  ON p.country = v.country AND p.year = v.year
                WHERE v.antigen = ?
                  AND v.year = ?
                  AND v.doses IS NOT NULL
                  AND p.population > 0
                GROUP BY v.country
            )
            SELECT c.name        AS country,
                   s.rate        AS start_rate,
                   e.rate        AS end_rate,
                   (e.rate - s.rate) AS improvement
            FROM start_rate s
            JOIN end_rate e ON e.country = s.country
            JOIN Country c  ON c.CountryID = s.country
            ORDER BY {order_sql}
            LIMIT ?
        """
        results = query(sql, [antigen, start_year, antigen, end_year, top_n])

    return render_template(
        "biggest_improvement.html",
        antigens=antigens, years=years,
        start_year=start_year, end_year=end_year,
        antigen=antigen, top_n=top_n, sort_by=sort_by,
        results=results, valid_range=valid_range,
    )


@app.route("/above-average", methods=["GET"])
def above_average():
    """Sub-Task B — Countries whose infection rate per 100,000 exceeds the
    global rate. The global rate is the first row of the result table
    (UNION ALL), so display ordering is also handled in SQL.

    Duplicate fact rows are collapsed with SUM()/AVG() inside sub-queries
    before the rate division. Sorting is parameterised via a whitelist.
    """
    inf_types = query("SELECT id, description FROM Infection_Type ORDER BY description")
    years = query("SELECT YearID FROM YearDate ORDER BY YearID")

    inf_type = request.args.get("inf_type", "MEA")
    year     = request.args.get("year", type=int, default=2020)
    sort_by  = request.args.get("sort_by", "rate_desc")

    # The "Global" row must always appear first; sort_priority forces that.
    # Country rows then sort by the user-chosen criterion.
    # "similarity" sorts by |rate - global_rate| — distance from the global mean.
    order_sql = safe_order(sort_by, {
        "rate_desc":    "sort_priority ASC, rate DESC, country ASC",
        "rate_asc":     "sort_priority ASC, rate ASC,  country ASC",
        "country_asc":  "sort_priority ASC, country ASC",
        "similarity":   "sort_priority ASC, ABS(rate - global_rate) ASC, country ASC",
    }, "rate_desc")

    # Single statement:
    #   * one CTE collapses duplicate population rows
    #   * one CTE collapses duplicate infection rows
    #   * one CTE computes the global rate (sum-of-cases / sum-of-population)
    #   * the final SELECT UNIONs the Global row with the above-average countries
    sql = f"""
        WITH pop AS (
            SELECT country, year, AVG(population) AS population
            FROM CountryPopulation
            WHERE year = ?
            GROUP BY country, year
        ),
        inf AS (
            SELECT inf_type, country, year, SUM(cases) AS cases
            FROM InfectionData
            WHERE inf_type = ? AND year = ?
            GROUP BY inf_type, country, year
        ),
        joined AS (
            SELECT c.CountryID AS country_id,
                   c.name      AS country,
                   inf.cases   AS cases,
                   pop.population AS population,
                   (inf.cases * 100000.0) / pop.population AS rate
            FROM Country c
            JOIN inf ON inf.country = c.CountryID
            JOIN pop ON pop.country = c.CountryID
            WHERE pop.population > 0
        ),
        global_rate_cte AS (
            SELECT (SUM(cases) * 100000.0) / SUM(population) AS global_rate
            FROM joined
        ),
        combined AS (
            SELECT 0 AS sort_priority,
                   'Global' AS country,
                   NULL AS cases,
                   NULL AS population,
                   g.global_rate AS rate,
                   g.global_rate AS global_rate
            FROM global_rate_cte g
            UNION ALL
            SELECT 1 AS sort_priority,
                   j.country,
                   j.cases,
                   j.population,
                   j.rate,
                   g.global_rate
            FROM joined j, global_rate_cte g
            WHERE j.rate > g.global_rate
        )
        SELECT * FROM combined
        ORDER BY {order_sql}
    """
    rows = query(sql, [year, inf_type, year])

    # Pull the global rate out for the page header / empty-state messaging.
    global_rate = rows[0]["rate"] if rows else None

    inf_name_row = query("SELECT description FROM Infection_Type WHERE id = ?", [inf_type])
    inf_name = inf_name_row[0]["description"] if inf_name_row else inf_type

    return render_template(
        "above_average.html",
        inf_types=inf_types, years=years,
        inf_type=inf_type, year=year, sort_by=sort_by,
        rows=rows, global_rate=global_rate, inf_name=inf_name,
    )


# ============================================================
#  USABILITY SURVEY
# ============================================================
#
# Questions are defined once here and drive the form, the storage,
# the summary statistics, and the detail view. Each question has:
#   id     – stable key stored in SurveyAnswer.question_id
#   text   – the prompt shown to the participant
#   type   – "likert" (1-5), "choice" (radio), or "open" (free text)
#   options– choices for "choice" type
#   section– grouping label for the form

LIKERT_LABELS = {
    "1": "Strongly disagree", "2": "Disagree", "3": "Neutral",
    "4": "Agree", "5": "Strongly agree",
}

SURVEY_QUESTIONS = [
    # Part A — Usability (Likert)
    {"id": "q1",  "section": "Usability", "type": "likert",
     "text": "I understood what the website was about within the first minute."},
    {"id": "q2",  "section": "Usability", "type": "likert",
     "text": "It was easy to navigate between the different pages."},
    {"id": "q3",  "section": "Usability", "type": "likert",
     "text": "The filters (antigen, year, region, economic phase) were easy to find and use."},
    {"id": "q4",  "section": "Usability", "type": "likert",
     "text": "The data in the tables was clear and easy to read."},
    {"id": "q5",  "section": "Usability", "type": "likert",
     "text": "I understood what the numbers meant (e.g. \"coverage %\", \"cases per 100,000\")."},
    {"id": "q6",  "section": "Usability", "type": "likert",
     "text": "The sorting options worked the way I expected."},
    {"id": "q7",  "section": "Usability", "type": "likert",
     "text": "I always knew where I was on the website."},
    {"id": "q8",  "section": "Usability", "type": "likert",
     "text": "The visual design (colours, layout, text size) made the information easy to take in."},
    # Part B — Satisfaction (Likert)
    {"id": "q9",  "section": "Satisfaction", "type": "likert",
     "text": "Overall, I found the website easy to use."},
    {"id": "q10", "section": "Satisfaction", "type": "likert",
     "text": "I felt confident completing the tasks."},
    {"id": "q11", "section": "Satisfaction", "type": "likert",
     "text": "I would trust this website as a source of vaccination information."},
    {"id": "q12", "section": "Satisfaction", "type": "likert",
     "text": "I would recommend this website to someone wanting to learn about immunisation data."},
    {"id": "q13", "section": "Satisfaction", "type": "choice",
     "text": "Overall, how would you rate your experience using the website?",
     "options": ["Very poor", "Poor", "Average", "Good", "Excellent"]},
    # Part C — Open-ended
    {"id": "q14", "section": "Open feedback", "type": "open",
     "text": "What did you like most about the website?"},
    {"id": "q15", "section": "Open feedback", "type": "open",
     "text": "What did you find most confusing or frustrating, if anything?"},
    {"id": "q16", "section": "Open feedback", "type": "open",
     "text": "Was there any task where you weren't sure what to do next? Which one, and why?"},
    {"id": "q17", "section": "Open feedback", "type": "open",
     "text": "Was there anything you expected to be able to do but couldn't?"},
    {"id": "q18", "section": "Open feedback", "type": "open",
     "text": "If you could change or add ONE thing to improve the website, what would it be?"},
    {"id": "q19", "section": "Open feedback", "type": "open",
     "text": "Any other comments?"},
    # Part D — Context
    {"id": "q20", "section": "Context", "type": "choice",
     "text": "How comfortable are you, in general, with using data-heavy websites and dashboards?",
     "options": ["Not at all", "Slightly", "Moderately", "Very", "Extremely"]},
]

# Convenience lookups
QUESTION_BY_ID = {q["id"]: q for q in SURVEY_QUESTIONS}
LIKERT_IDS = [q["id"] for q in SURVEY_QUESTIONS if q["type"] == "likert"]


def survey_sections():
    """Group questions by section, preserving order."""
    sections = []
    seen = {}
    for q in SURVEY_QUESTIONS:
        if q["section"] not in seen:
            seen[q["section"]] = []
            sections.append((q["section"], seen[q["section"]]))
        seen[q["section"]].append(q)
    return sections


@app.route("/survey", methods=["GET"])
def survey():
    """Render the usability survey form."""
    submitted = request.args.get("submitted")
    return render_template(
        "survey.html",
        sections=survey_sections(),
        likert_labels=LIKERT_LABELS,
        submitted=submitted,
    )


@app.route("/survey", methods=["POST"])
def survey_submit():
    """Persist a survey submission and its answers, then redirect."""
    db = get_db()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    code = (request.form.get("participant_code") or "").strip() or None

    cur = db.execute(
        "INSERT INTO SurveySubmission (participant_code, submitted_at) VALUES (?, ?)",
        (code, now),
    )
    submission_id = cur.lastrowid

    # Store one row per answered question (skip blanks).
    for q in SURVEY_QUESTIONS:
        value = (request.form.get(q["id"]) or "").strip()
        if value:
            db.execute(
                "INSERT INTO SurveyAnswer (submission_id, question_id, answer_value) "
                "VALUES (?, ?, ?)",
                (submission_id, q["id"], value),
            )
    db.commit()
    return redirect(url_for("survey", submitted=1))


@app.route("/survey/results")
def survey_results():
    """Summary statistics across all submissions + a list of submissions."""
    total = query("SELECT COUNT(*) AS c FROM SurveySubmission")[0]["c"]

    # Per-Likert-question average + count, computed in SQL.
    likert_stats = {}
    if LIKERT_IDS:
        placeholders = ",".join("?" * len(LIKERT_IDS))
        rows = query(
            f"""
            SELECT question_id,
                   AVG(CAST(answer_value AS REAL)) AS avg_score,
                   COUNT(*) AS n
            FROM SurveyAnswer
            WHERE question_id IN ({placeholders})
            GROUP BY question_id
            """,
            LIKERT_IDS,
        )
        likert_stats = {r["question_id"]: r for r in rows}

    # Build an ordered list of likert summaries for the template.
    likert_summary = []
    for qid in LIKERT_IDS:
        q = QUESTION_BY_ID[qid]
        stat = likert_stats.get(qid)
        likert_summary.append({
            "id": qid,
            "text": q["text"],
            "section": q["section"],
            "avg": stat["avg_score"] if stat else None,
            "n": stat["n"] if stat else 0,
        })

    # Overall averages by section (Usability vs Satisfaction).
    overall_avg = None
    if likert_summary:
        scored = [s["avg"] for s in likert_summary if s["avg"] is not None]
        overall_avg = sum(scored) / len(scored) if scored else None

    # Distribution for the "overall rating" choice question (q13).
    rating_dist = query(
        """
        SELECT answer_value AS label, COUNT(*) AS n
        FROM SurveyAnswer
        WHERE question_id = 'q13'
        GROUP BY answer_value
        """
    )
    rating_map = {r["label"]: r["n"] for r in rating_dist}

    # List of submissions (newest first) with an answered-question count.
    submissions = query(
        """
        SELECT s.submission_id,
               s.participant_code,
               s.submitted_at,
               COUNT(a.answer_id) AS answered
        FROM SurveySubmission s
        LEFT JOIN SurveyAnswer a ON a.submission_id = s.submission_id
        GROUP BY s.submission_id
        ORDER BY s.submission_id DESC
        """
    )

    return render_template(
        "survey_results.html",
        total=total,
        likert_summary=likert_summary,
        overall_avg=overall_avg,
        rating_options=QUESTION_BY_ID["q13"]["options"],
        rating_map=rating_map,
        submissions=submissions,
    )


@app.route("/survey/results/<int:submission_id>")
def survey_detail(submission_id):
    """Full answers for a single submission."""
    sub = query(
        "SELECT submission_id, participant_code, submitted_at "
        "FROM SurveySubmission WHERE submission_id = ?",
        [submission_id],
    )
    if not sub:
        return render_template("survey_detail.html", submission=None,
                               answers=[], sections=[]), 404

    raw = query(
        "SELECT question_id, answer_value FROM SurveyAnswer WHERE submission_id = ?",
        [submission_id],
    )
    answer_map = {r["question_id"]: r["answer_value"] for r in raw}

    # Build per-section answer lists in question order, resolving Likert labels.
    detail_sections = []
    for section_name, questions in survey_sections():
        items = []
        for q in questions:
            val = answer_map.get(q["id"])
            display = val
            if q["type"] == "likert" and val in LIKERT_LABELS:
                display = f"{val} — {LIKERT_LABELS[val]}"
            items.append({
                "text": q["text"], "type": q["type"],
                "value": val, "display": display,
            })
        detail_sections.append((section_name, items))

    return render_template(
        "survey_detail.html",
        submission=sub[0],
        sections=detail_sections,
    )


# Jinja filter for number formatting
@app.template_filter("num")
def num_filter(v, digits=0):
    if v is None:
        return "—"
    try:
        if digits == 0:
            return f"{int(round(float(v))):,}"
        return f"{float(v):,.{digits}f}"
    except (ValueError, TypeError):
        return str(v)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
