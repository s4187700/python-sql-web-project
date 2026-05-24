# Usability Test Plan

**Project:** Investigating Preventable Infectious Diseases — WHO Immunisation Data Explorer
**Course:** COSC3107 | COSC3108 — Python Programming Studio
**Researcher:** Nguyen Huynh (S4187700)

---

## 1. Overview

This document defines the tasks participants will perform during in-class
usability testing, the scenarios that frame those tasks, and the objectives
and success criteria used to evaluate the results. The tasks cover the
**Level 1** (Big Picture) and **Level 2** (Shallow Glance) sub-tasks of the
application.

## 2. Goals of the test

1. Determine whether new users can understand the purpose of the site within
   the first minute (Level 1).
2. Determine whether users can locate and interpret the four headline facts
   and the personas (Level 1).
3. Determine whether users can successfully filter, sort, and read
   vaccination-coverage data by antigen, year, region, and country
   (Level 2A).
4. Determine whether users can compare infection burden across economic
   phases and read cases per 100,000 (Level 2B).
5. Identify points of confusion, hesitation, or error in navigation,
   filtering, and reading results.

## 3. Test environment

- **Device:** Laptop / desktop browser (Chrome or Edge recommended).
- **URL:** `http://127.0.0.1:5000/` (running locally on the moderator's machine).
- **Session length:** 10–15 minutes of tasks + 3–5 minutes survey.
- **Method:** Moderated, think-aloud protocol. The moderator observes and
  records task completion, time, errors, and verbal comments.

## 4. Participant profile

Participants are fellow students in the cohort, acting as proxies for the
application's target personas. No prior knowledge of the dataset is assumed.

The personas this test represents:

- **Mark Tran** — Parent / Concerned Citizen — needs clear high-level facts
  (Level 1).
- **Linh Nguyen** — University Student — needs to filter and sort structured
  data (Level 2A).
- **Sara Okafor** — NGO Field Officer — needs to find high-burden,
  low-income countries (Level 2B).

---

## 5. Context scenarios and Key Path scenarios

> A **context scenario** describes the user's real-world goal and situation.
> The **Key Path scenario** describes the ideal click path through the
> interface to achieve that goal. The tasks below are derived from these.

### Scenario A — "What is this site?" (Level 1A · Persona: Mark Tran)

**Context:** Mark has heard conflicting claims about vaccination online. He
opens the site for the first time wanting honest, plain facts before forming
an opinion.

**Key Path:** Landing page → read the four fact cards → read the disease
list → understand the timeframe and scope without using any controls.

### Scenario B — "Who is this for, and who built it?" (Level 1B · Persona: Mark Tran)

**Context:** Mark wants to know whether the site is trustworthy and unbiased
before he relies on it.

**Key Path:** Click **Mission** → read the mission statement → identify the
target personas → find the author and student number.

### Scenario C — "Which countries are well-vaccinated?" (Level 2A · Persona: Linh Nguyen)

**Context:** Linh is writing an epidemiology assignment comparing measles
vaccination coverage between regions for a recent year.

**Key Path:** Click **Vaccination Rates** → select antigen MCV1 → select year
2020 → apply filters → read Table 1 (countries ≥ 90 %) → read Table 2
(per-region summary) → change sort order to compare.

### Scenario D — "Does poverty correlate with disease?" (Level 2B · Persona: Sara Okafor)

**Context:** Sara plans an immunisation drive and wants to know which
low-income countries had the highest measles burden in a recent year.

**Key Path:** Click **Infections × Economy** → select economic phase "Low
Income" → select infection "Measles" → select year 2022 → apply → read cases
per 100,000 → sort by Rate (high → low) → review the cross-phase summary.

---

## 6. Tasks, objectives, and success criteria

> Participants are given the **scenario** verbally, not the click path. The
> click path is the moderator's reference for what "success" looks like.

### Task 1 — Understand the site at a glance *(Level 1A)*

- **Scenario given:** "You've just opened this site for the first time. Take
  a look at the home page and tell me, out loud, what this site is about and
  what data it covers."
- **Objective:** Confirm the landing page communicates purpose and scope
  without interaction.
- **Success criteria:**
  - Participant correctly states the topic (global vaccination / infectious
    disease data).
  - Participant identifies at least **2 of the 4** headline facts (timeframe,
    doses, cases, countries).
  - Completed without asking the moderator what the site is for.
- **Metrics:** task completion (yes/no), time to first correct statement,
  number of facts identified.

### Task 2 — Find who the site is for and who built it *(Level 1B)*

- **Scenario given:** "You want to know who this website is designed for, and
  who created it. Find that information."
- **Objective:** Confirm users can navigate to Mission and locate personas +
  author.
- **Success criteria:**
  - Participant navigates to the Mission page unaided.
  - Participant identifies at least **2** target personas.
  - Participant finds the author's name and student number.
- **Metrics:** task completion, navigation errors (wrong clicks),
  time on task.

### Task 3 — Filter vaccination coverage by antigen and year *(Level 2A)*

- **Scenario given:** "You want to see which countries reached at least 90 %
  coverage for the MCV1 vaccine in the year 2020."
- **Objective:** Confirm users can operate the filter controls and interpret
  the ≥ 90 % table.
- **Success criteria:**
  - Participant sets antigen = MCV1 and year = 2020 and applies the filter.
  - Participant correctly identifies that Table 1 lists countries at or above
    90 % coverage.
  - Participant can name at least one country from the result.
- **Metrics:** task completion, time on task, number of filter mistakes,
  whether they found the "Apply" action without prompting.

### Task 4 — Compare regions using sort *(Level 2A)*

- **Scenario given:** "Now you want to see, for each region, how many of its
  countries reached the 90 % benchmark — and order the regions from most to
  fewest."
- **Objective:** Confirm users can read Table 2 and use the sort control.
- **Success criteria:**
  - Participant reads Table 2 (per-region summary) correctly.
  - Participant successfully changes the sort order.
  - Participant identifies the top-performing region.
- **Metrics:** task completion, whether sorting was discovered unaided,
  time on task.

### Task 5 — Find high-burden low-income countries *(Level 2B)*

- **Scenario given:** "You're planning a measles immunisation campaign. Find
  the measles cases per 100,000 people for low-income countries in 2022, and
  tell me which country was worst affected."
- **Objective:** Confirm users can operate the economy/infection/year filters
  and interpret the per-100,000 rate.
- **Success criteria:**
  - Participant sets economy = Low Income, infection = Measles, year = 2022.
  - Participant sorts by Rate (high → low) and identifies the top country.
  - Participant understands the "cases per 100,000" column.
- **Metrics:** task completion, time on task, filter errors, whether the
  rate column was understood without explanation.

### Task 6 — Read the cross-phase summary *(Level 2B)*

- **Scenario given:** "Using the same page, tell me which economic phase had
  the most total measles cases in 2022."
- **Objective:** Confirm users can locate and read the summary table that
  aggregates across all economic phases.
- **Success criteria:**
  - Participant locates the summary table below the detail table.
  - Participant correctly identifies the phase with the highest total.
- **Metrics:** task completion, whether the summary table was noticed unaided.

---

## 7. Overall success measures

| Measure | Target |
| ------- | ------ |
| Task completion rate (all tasks) | ≥ 80 % of participants complete each task |
| Critical navigation errors | ≤ 1 per participant on average |
| Tasks completed without moderator help | ≥ 4 of 6 |
| Average post-test satisfaction (survey, 5-point Likert) | ≥ 4.0 |

## 8. Data captured per task

For each participant × task the moderator records:

- Completed? (Yes / Partial / No)
- Time on task (seconds)
- Number of errors / wrong clicks
- Required moderator assistance? (Yes / No)
- Notable verbal comments (think-aloud quotes)

## 9. Roles

- **Moderator** — reads the script, presents scenarios, observes, keeps time.
- **Note-taker** (if available) — records metrics and quotes so the moderator
  can focus on the participant. If testing solo, the moderator does both.
