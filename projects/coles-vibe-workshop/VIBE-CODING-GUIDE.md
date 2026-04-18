# Vibe Coding Best Practices

**Coles x Databricks Vibe Coding Workshop -- 9:30 AM - 4:00 PM**
A Guide to Agentic Software Development with Claude

---

# Block A: How to Think

## 1. What is Vibe Coding?

> "There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists."
>
> -- Andrej Karpathy, February 2025

### Traditional vs Agentic Development

| | Traditional Development | Agentic Development |
|---|---|---|
| **Who writes code** | Human writes every line of code | Human specifies intent via tests, specs, and CLAUDE.md |
| **Implementation** | Human handles all implementation details | Agent implements code to match the specification |
| **Debugging** | Human debugs, refactors, and iterates manually | Agent self-corrects by reading test failures |
| **Speed bottleneck** | Speed limited by typing and cognitive load | Speed limited by quality of direction, not typing |

### Rule #1: Just Say What You Want

Everything else builds on this: **you literally type what you want and it happens.**

- **Want a project?** Tell Claude what you're building — it creates the CLAUDE.md, project structure, and config
- **Want behavior to change?** Say "from now on, do X" — it updates the rules
- **See a technique you like?** Paste it in — Claude reads it and adapts
- **Everything is markdown** — CLAUDE.md, skills, hooks, all of it

That's **agentic engineering**. You shape the harness through conversation, not by hand-writing config files. You don't "write" a CLAUDE.md. You have a conversation that produces one.

The progression of agentic engineering:

1. **Say it** — have a conversation, get what you want
2. **Curate it** — save the good stuff as markdown files (CLAUDE.md, skills, hooks) so you don't repeat yourself
3. **Wire up tools** — increasingly just instructions to CLI commands, not heavyweight MCP servers

### The "Brilliant New Employee"

Think of Claude as a **brilliant but brand-new employee** who just joined your team today:

1. **Deep Technical Skills** -- Knows Python, PySpark, SQL, FastAPI, React -- but has zero context on *your* norms or architecture decisions.
2. **Excels With Clear Direction** -- Given a precise spec, produces excellent code. Given a vague request, produces plausible-looking code that misses the mark.
3. **Needs Explicit Context** -- "Always PySpark, never pandas." "Snake_case for all columns." "Tests before code." Won't infer your team's standards.

**Your job shifts from WRITING code to DIRECTING an exceptionally capable engineer. Invest time in specs upfront, not in writing code.**

---

## 2. The Medallion Architecture -- What We're Building

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│     Bronze        │     │     Silver        │     │      Gold        │
│   Raw Ingestion   │ ──> │ Cleaned & Enriched│ ──> │  Analytics-Ready │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### Bronze (Raw)

- Ingest data as-is from APIs and files
- No transformations applied
- Preserves original column names and types
- Acts as an immutable audit trail
- Use `@dp.table` with data quality expectations

### Silver (Cleaned)

- Decode codes to readable names
- Handle nulls and invalid rows
- Standardize date formats and types
- Rename columns to snake_case
- Use `@dp.table` reading from bronze

### Gold (Aggregated)

- Roll up and aggregate metrics
- Join across data sources
- Calculate KPIs (YoY growth, rolling averages)
- Ready for Genie and AI/BI dashboards
- Use `@dp.materialized_view`

> **Why medallion?** Separation of concerns. Each layer has one job. Bugs are easy to trace. Silver and gold can be rebuilt from bronze at any time.

---

## 3. CLAUDE.md -- Your Team's Operating Manual

CLAUDE.md is a **persistent instruction file** that encodes your team's standards. The agent reads it automatically at the start of every session -- no need to repeat yourself.

### Three Scope Levels

| Level | Path | Purpose |
|---|---|---|
| **User-Level** | `~/.claude/CLAUDE.md` | Personal preferences, coding style, editor habits. Applies to all your projects. |
| **Repo-Level** | `./CLAUDE.md` | Team standards, tech stack, architecture decisions. Overrides user-level. Checked into git. |
| **Module-Level** | `./src/CLAUDE.md` | Module-specific rules (e.g., "all files here use `@dp.table`"). Overrides repo-level. |

### Why It Works

- **Self-correcting:** Agent re-reads it each session -- no drift
- **Searchable:** Agent can reference specific sections on demand
- **Maintainable:** One file to update, entire team benefits
- **Scoped:** Different rules for different parts of the codebase

---

## 4. CLAUDE.md -- What to Include

### Template Structure

```markdown
# CLAUDE.md -- Grocery Intelligence Platform

## Team
- Team Name: TEAM_NAME
- Schema: workshop_vibe_coding.TEAM_SCHEMA

## Project
A data platform that ingests Australian retail
and food price data through a medallion architecture.

## Tech Stack
- Data processing: PySpark (never pandas)
- Pipeline: Lakeflow Declarative Pipelines
- Web backend: FastAPI with Pydantic models
- Deployment: Databricks Asset Bundles

## Data Standards
- Architecture: Bronze -> Silver -> Gold
- Date columns: YYYY-MM-DD, stored as DATE
- Naming: snake_case for all tables/columns

## Rules
- Always use PySpark, never pandas
- Write tests BEFORE implementation
- Keep solutions minimal

## Project Structure
(directory tree)

## Data Sources
(table with API endpoints)

## Code Mappings
(region codes, industry codes)
```

### Tips for Effective CLAUDE.md

- **Keep it lean:** Aim for ~50 lines. CLAUDE.md consumes context tokens -- every line counts.
- **Be specific:** "Always PySpark, never pandas" beats "Use appropriate tools." Concrete rules get followed.
- **Include code mappings:** Region codes, industry codes, enum values -- anything the agent needs for lookups.

> **Warning:** Don't dump everything in. CLAUDE.md is not documentation. It's a set of standing orders. If a rule isn't referenced often, it belongs in a separate doc the agent can read on demand.

### What NOT to Include

- Long explanations or tutorials
- Full API documentation (link to it instead)
- Implementation details that change frequently
- Anything already in your test suite

---

## 5. TDD + Agents -- The Loop & Why It Works

> **Rule #1 connection:** You say what should happen. The agent writes the test. Because it's Given/When/Then, you can read it back and verify it captured your intent. The agent writes the code AND the tests -- your job is to check that the tests match what you actually wanted.

```
STEP 1              STEP 2              STEP 3              STEP 4
Human writes    ->  Agent implements ->  Run & iterate   ->  Human reviews
the test            code to pass         (agent self-        & accepts
                                         corrects)
```

**The Test IS the Spec.** Unlike prose specs, a test is executable, unambiguous, and either passes or fails.

### Why This Works

1. **Unambiguous Specifications** -- A test says exactly what the code must do. No room for "I thought you meant..." The agent reads the assertion and knows the target.
2. **Self-Correcting Loop** -- The agent reads failure messages, understands what went wrong, and fixes automatically. No waiting for human review on each iteration.
3. **Guardrails** -- Existing passing tests prevent the agent from rewriting working code. New code must pass new tests *without* breaking old ones.
4. **Ratchet Effect** -- Each passing test constrains the next implementation. Quality only goes up, never down. Every green test is permanent progress.

> **If you take one thing from today:** write the tests first. Always.

---

## 6. Validation Patterns -- Proving the Work is Done

### 6.1 The Core Principle

Anthropic's #1 best practice: **"Include tests, screenshots, or expected outputs so Claude can check itself. This is the single highest-leverage thing you can do."**

There is a critical difference between an agent that *thinks* it did the work and one that *proves* it did. Every prompt you write should include a way for the agent to verify its own output. If there is no verification step, the agent is guessing -- and you will not know until much later.

### 6.2 Separate Tests from Implementation

Never ask Claude to write tests AND code in the same prompt. When both are generated together, the agent writes tests that match the implementation rather than the requirements. The tests become a mirror of the code, not an independent check.

**Do this -- two separate prompts:**

```text
Prompt 1:
"Write tests for a function that decodes ABS region codes to state names.
Test: 1→NSW, 2→VIC, 99→ValueError. Do NOT implement the function."

Prompt 2:
"Now implement decode_region() to make these tests pass.
Run pytest after implementation."
```

**Not this -- one combined prompt:**

```text
"Write a function that decodes region codes and write tests for it."
```

When the test exists before the code, it acts as a genuine constraint. When both are written together, the test becomes a rubber stamp.

### 6.3 Data Quality Expectations (Declarative Validation)

For Lakeflow pipelines, embed validation directly in the table definition using `@dp.expect`. These checks run automatically every time the pipeline executes -- not a separate manual step.

```python
import dlt as dp

@dp.table
@dp.expect("turnover_not_null", "turnover IS NOT NULL")
@dp.expect_or_fail("no_negative_values", "turnover >= 0")
@dp.expect("valid_state_code", "state_code BETWEEN 1 AND 8")
def bronze_retail_trade():
    return (
        spark.read.format("json")
        .load("/Volumes/workshop/raw/abs_retail/")
    )
```

- `@dp.expect` logs violations but lets rows through (monitoring).
- `@dp.expect_or_fail` halts the pipeline on violation (hard stop).

These are validation patterns baked into the pipeline itself. The agent does not need to remember to run checks -- they execute every time.

### 6.4 API Schema Contracts

Tests that validate the exact response structure, not just "returns 200". Every field, every type, every boundary.

```python
def test_metrics_schema(client):
    """Gold metrics endpoint returns correct structure and value ranges."""
    response = client.get("/api/metrics")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    for record in data:
        # Exact field set -- no extra, no missing
        assert set(record.keys()) == {"state", "turnover", "yoy_growth"}

        # Type checks
        assert isinstance(record["state"], str)
        assert isinstance(record["turnover"], (int, float))
        assert isinstance(record["yoy_growth"], (int, float))

        # Boundary checks -- catch nonsense values
        assert record["state"] in ("NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT")
        assert 0 < record["turnover"] < 50000
        assert -100 < record["yoy_growth"] < 500
```

This test does not just check that the endpoint works. It proves the data contract is correct. If the agent adds a field, removes a field, or returns a value outside the expected range, this test fails immediately.

### 6.5 Regression Testing (The Ratchet)

After every new test passes, run the **full** test suite:

```bash
pytest tests/ -x --no-header -q
```

This proves new code did not break existing functionality. The `-x` flag stops at the first failure -- you want to know immediately.

Each green test is permanent progress. The suite is a ratchet: quality only goes up, never down. If the agent adds a new silver transformation and breaks a bronze test, the full suite catches it before you move on.

### 6.6 Negative Case Testing

Prove error handling works. Happy-path tests are necessary but insufficient -- you need to verify the system fails gracefully.

```python
def test_invalid_date_returns_error(client):
    """Invalid date format returns 400/422, not a server crash."""
    response = client.get("/api/metrics?start_date=2024/13/45")
    assert response.status_code in (400, 422)
    assert "error" in response.json()


def test_unknown_state_raises(spark):
    """Decoding an invalid state code raises ValueError."""
    from src.silver.transforms import decode_region
    import pytest

    with pytest.raises(ValueError, match="Unknown region code"):
        decode_region(99)


def test_empty_dataframe_handled(spark):
    """Silver transform handles empty input without crashing."""
    empty_df = spark.createDataFrame([], "date STRING, turnover DOUBLE, state STRING")
    result = clean_retail_data(empty_df)
    assert result.count() == 0
```

Negative tests are how you prove the agent built something robust, not just something that works on the happy path.

### 6.7 Diff-Based Validation

After changes, ask the agent to show `git diff` and verify only the intended files changed. This catches hidden side effects -- the agent reformatting a file it should not have touched, or silently modifying a passing test.

```text
"Show me git diff. Only src/silver/transforms.py should have changed.
If any other files were modified, revert them."
```

This is especially important after the agent has been running for several iterations. Context window pressure can cause it to make broader changes than intended.

### 6.8 The Prompt Checklist

Before every prompt, ask yourself these four questions:

| Question | If "No"... |
|---|---|
| Can Claude run something to prove this worked? (test, command, query) | Add a verification step: "Run pytest after" or "Query the table and show row count" |
| Is the success criterion binary? (pass/fail, not "looks good") | Rewrite with a concrete assertion: exact count, specific value, schema match |
| Can it run in under 30 seconds? | Break into smaller pieces. Long-running validation wastes context on waiting. |
| Is it separate from the implementation? (not self-grading) | Write the test first in a separate prompt. Never let the agent grade its own work. |

If the answer to any of these is "no," stop and add a verification step before sending the prompt.

---

## 7. Context Windows -- Your Agent's RAM

### What Are Tokens?

A **token** is the basic unit of text for an LLM -- roughly 3/4 of a word. Everything the agent reads and writes is measured in tokens.

| Content | Approximate Tokens |
|---|---|
| Your CLAUDE.md (~50 lines) | ~500 tokens |
| 200-line Python file | ~2,500 tokens |
| Claude's context window | 200,000 tokens |

Context window = RAM. When it fills up, older context gets evicted and the agent may forget earlier decisions.

### Four Strategies

1. **Keep CLAUDE.md Lean** -- ~50 lines. Every line consumes tokens every session. Put verbose docs elsewhere.
2. **Be Specific** -- "Fix the test in test_pipeline.py::test_silver" not "write some code." Target files, not vague asks.
3. **Plan Before Building** -- Use `/plan` mode. Alignment upfront prevents expensive rework that wastes context.
4. **New Sessions for New Tasks** -- Context is RAM. When switching tasks, start fresh with `/clear` or a new session.

---

# Block B: Lab 0 -- Hands-On Together

## 8. Writing Your CLAUDE.md (10 min)

Open your Coding Agents terminal and paste the prompt below. Replace `<team_schema>` with your assigned schema name.

```text
Create a CLAUDE.md for a grocery intelligence platform.

Tech stack: PySpark, Lakeflow Declarative Pipelines, FastAPI + React,
Databricks Asset Bundles (DABs).

Data sources: ABS SDMX APIs, FSANZ web scraping, ACCC PDF ingestion
via UC Volumes.

Unity Catalog namespace: workshop_vibe_coding.<team_schema>.

Include:
- Team name and schema
- Tech stack with explicit constraints (PySpark not pandas)
- Data standards (medallion architecture, date formats, naming)
- Rules (TDD, minimal solutions, don't change passing tests)
- Project structure (src/bronze, src/silver, src/gold, tests/, app/)
- Data sources table with API endpoints
- Code mappings for region and industry codes
```

**This is the most important 10 minutes of the workshop -- everything else builds on this.**

> **After generating:** Read through the CLAUDE.md and edit anything that doesn't match your team's preferences. Add your team's chosen angle (Retail Performance, Food Inflation, etc.) to the Project section.

---

## 9. Writing Your First Test (10 min)

### Given -- When -- Then

```python
def test_bronze_ingest_retail(spark):
    # GIVEN: Raw ABS retail trade data
    raw_data = spark.createDataFrame([
        ("2024-01-15", 1000, "NSW"),
        ("2024-01-16", None, "VIC"),
        ("invalid",    2000, "QLD"),
        ("2024-01-17", 1500, "NSW"),
        ("2024-01-18", 900,  "VIC"),
        ("2024-01-19", 1100, "QLD"),
        ("2024-01-20", 1300, "NSW"),
        ("2024-01-21", None, "SA"),
        ("2024-01-22", 800,  "WA"),
        ("2024-01-23", 1200, "TAS"),
    ], ["date", "price", "state"])

    # WHEN: Clean function applied
    result = clean_transactions(raw_data)

    # THEN: Invalid rows removed
    assert result.count() == 8
    assert result.filter("price IS NULL").count() == 0
```

### Key Principles

- **Concrete Values** -- Use real data: actual state codes, valid dates, realistic dollar amounts. Not mocks or abstract placeholders.
- **Small Datasets** -- 5-10 rows per test. Enough to cover happy path + edge cases. Easy to reason about.
- **Descriptive Names** -- `test_bronze_ingest_retail` not `test_transform`. The name tells the agent what to build.
- **Multiple Assertions** -- Check row count, column names, specific values, and null handling. Each assertion is a constraint.

---

## 10. Building Bronze Ingest (20 min)

Now let the agent build the implementation to pass your test. Paste the prompt below into Claude Code.

```text
Read CLAUDE.md and tests/test_pipeline.py. Implement the bronze
ingest function in src/bronze/ to make the failing test pass.

Rules:
- Use PySpark, not pandas
- Use @dp.table decorator for Lakeflow Declarative Pipelines
- Read data from the ABS Retail Trade SDMX API
- Store raw data with original column names
- Add _ingested_at timestamp column
- Run pytest tests/test_pipeline.py -k "bronze" -x after implementation
```

### What to Watch For

- **Does the agent read CLAUDE.md first?** If not, tell it: "Read CLAUDE.md first, then try again."
- **Does it use PySpark?** If it reaches for pandas, steer it back.
- **Does it run the test?** The agent should run pytest automatically and iterate until green.

### Expected Outcome

After ~15 minutes you should see:

- [ ] `src/bronze/ingest.py` -- Bronze ingest function
- [ ] `tests/test_pipeline.py` -- Passing bronze test
- [ ] pytest output showing green

> **Stuck?** Tell the agent: "Read the test failure message carefully and fix only the failing assertion."

---

## 11. Lab 0 Checkpoint (5 min)

**Before moving on, verify your team has all three pieces in place:**

### 1. CLAUDE.md

- [ ] Team name and schema present
- [ ] Tech stack with PySpark constraint
- [ ] Data standards section
- [ ] Rules section (TDD, minimal)
- [ ] Project structure defined

### 2. Passing Test

- [ ] Test uses Given-When-Then structure
- [ ] Concrete values (real state codes, dates)
- [ ] Multiple assertions (count, nulls)
- [ ] Descriptive test name
- [ ] `pytest -k "bronze" -x` passes

### 3. Bronze Ingest

- [ ] Uses PySpark (not pandas)
- [ ] Has @dp.table decorator
- [ ] Reads from data source
- [ ] Adds _ingested_at timestamp
- [ ] All bronze tests green

> **Falling behind?** No shame in using checkpoints. Tell the agent: "Copy the checkpoint tables from `workshop_vibe_coding.checkpoints` into my schema `workshop_vibe_coding.<team_schema>`"

**You've just completed the full TDD cycle: spec (CLAUDE.md) -> test -> implementation -> green. This is the pattern for the rest of the day.**

---

# Block C: Tools for the Labs

## 12. Skills -- Slash Commands

Skills are **reusable agent capabilities** triggered by slash commands. They encode domain knowledge and multi-step workflows into a single invocation.

### How Skills Work

A skill is a Markdown file that defines a multi-step workflow. When you type `/commit`, the agent:

1. Reads git status and diff
2. Analyzes changes and drafts a commit message
3. Stages files and creates the commit
4. Runs git status to verify success

### Built-In Examples

```bash
# Common skills
/commit     # Smart git commit with message
/review-pr  # Review a pull request
/test       # Run tests intelligently

# Custom skills you can create
/deploy-dab # Validate + deploy DABs bundle
/check-data # Query tables, verify counts
```

### Why Skills Matter

- **Automate Repetitive Patterns** -- Workflows you do 10x/day become one command. No re-explaining each time.
- **Encode Team Conventions** -- Your team's commit message format, deploy steps, and review checklist -- codified once, used by everyone.
- **Reduce Context Usage** -- A skill runs a pre-defined workflow without you needing to type out multi-step instructions each time.

> **Workshop tip:** You can create custom skills during the labs. Think about which multi-step workflows you repeat most often.

---

## 13. MCP -- "USB-C for AI"

**Model Context Protocol (MCP)** is a standard protocol for connecting AI agents to external tools and data sources. One protocol, every tool connects -- like USB-C for AI.

### Three Types of MCP Servers

**Managed (Built-In)**
Zero config -- pre-integrated with Databricks:
- Unity Catalog tables & volumes
- Vector Search indexes
- Genie spaces (NL -> SQL)
- DBSQL warehouses

**External (via Proxies)**
Community & vendor integrations:
- GitHub (PRs, issues, repos)
- Slack (messages, channels)
- Glean (internal search)
- JIRA (tickets, sprints)
- Databricks Docs

**Custom (Org-Specific)**
Build your own for internal tools:
- Wrap internal REST APIs
- Data quality workflows
- Monitoring & alerting
- Host on Databricks Apps

> **Key benefit:** Agents access ANY tool through a standard protocol. Credentials stay secure in Unity Catalog -- the agent never sees raw tokens or passwords.

---

## 14. Extending Claude Code for Your Organisation

Out of the box, Claude Code is a general-purpose agent. The real power comes from **customising it for your team's specific tools, data, and workflows**. Three mechanisms make this possible.

### Custom Skills -- Your Team's Playbooks

Skills are Markdown files that encode multi-step workflows. Any team can create them:

```markdown
# /deploy-pipeline
1. Run `databricks bundle validate`
2. Fix any validation errors
3. Run `databricks bundle deploy -t dev`
4. Run the pipeline and verify row counts
5. Commit with message "deploy: pipeline updated"
```

Save this as a skill, and every team member gets a one-command deploy workflow. No tribal knowledge required.

**Where to start:** Identify the 3 workflows your team repeats most often. Write them as skills. Share them in a team repo.

> **How powerful is a markdown skill?** [deathbyclawd.com](https://deathbyclawd.com/) scans which SaaS products can be replaced by one.

### Unity Catalog MCP Servers -- Connecting to Your Data

Databricks provides **managed MCP servers** that connect Claude Code directly to your data platform:

| MCP Server | What It Does |
|---|---|
| **Unity Catalog** | Browse tables, schemas, and volumes. Agent can read metadata without SQL. |
| **Genie Spaces** | Natural language queries on your gold tables, powered by your Genie configuration. |
| **SQL Warehouses** | Execute SQL queries directly. Agent reads results and iterates. |
| **Vector Search** | Semantic search over documents and embeddings stored in UC. |

These run inside Databricks -- credentials are managed by Unity Catalog, not stored in config files. The agent never sees raw tokens.

**Custom MCP servers** can wrap any REST API your org uses. Host them on Databricks Apps and register them in Unity Catalog for secure, governed access.

### Plugin Marketplaces -- Scaling Across Teams

As your organisation builds skills, agents, and MCP integrations, you need a way to **share and discover** them. A plugin marketplace solves this:

- **Plugins** group related skills and agents (e.g., a "Data Quality" plugin with skills for profiling, validation, and monitoring)
- **A marketplace** lets teams browse, install, and contribute plugins
- **Versioning** ensures updates don't break existing workflows

This is how you go from one team using Claude Code effectively to an entire organisation benefiting from shared automation. The pattern: start with 3-5 skills for your team, package them as a plugin, publish to a shared marketplace.

> **The key insight:** Claude Code is not a fixed product -- it's an extensible platform. The teams that invest in customisation get compounding returns as every new skill makes the agent more capable for everyone.

---

## 15. Genie & AI/BI Dashboards

### Genie: Natural Language on Your Data

Business users ask questions in plain English. Genie generates SQL, runs it, and returns results with visualizations.

```sql
-- User asks:
-- "Which state had the highest food retail turnover in 2024?"

-- Genie generates:
SELECT state,
       SUM(turnover_millions) AS total
FROM gold.retail_summary
WHERE year = 2024
GROUP BY state
ORDER BY total DESC
LIMIT 1
```

**How to set up:** Point Genie at your gold tables, add column descriptions, and provide example queries in the instructions.

### AI/BI Dashboards

Auto-generated dashboards that understand your data. Describe a visualization in natural language and it generates the chart.

- "Show monthly revenue by state as a line chart"
- "Compare food CPI across states as a bar chart"
- "Display year-over-year growth as a heatmap"

**How they complement each other:**
- **Dashboards** = recurring views, standard KPIs, shared with stakeholders
- **Genie** = ad-hoc questions, exploration, self-serve analytics

Both feed from the same **gold tables** -- the output of your data pipeline. Good gold tables = good Genie + dashboards.

---

# Block D: Reference

## 16. Anthropic's Two Core Practices

### #1: Give Claude a Way to Verify Its Work

The agent needs a **feedback loop** -- a way to check if its output is correct without asking you.

- **Tests:** pytest, unit tests, integration tests
- **Screenshots:** visual verification of UI changes
- **Expected outputs:** "this query should return 42"
- **Diff comparisons:** "output should match this template"

> **Self-correcting:** Agent reads failure, fixes, re-runs. Scales without human review bottleneck for each iteration.

### #2: Explore First, Plan, Then Code

Don't ask the agent to implement immediately. Follow a three-phase approach:

1. **Explore:** Read relevant code, understand existing patterns, check what's already there
2. **Plan:** Use `/plan` mode or `ultrathink` to align on approach before writing code
3. **Code:** Implement with full context -- agent knows what exists, what to change, what to preserve

> **Why this works:** Prevents over-engineering and hallucinations. The agent builds on what exists rather than speculating about what might exist.

---

## 17. Steering Your Agent -- Pitfalls & Phrases

### Common Pitfalls & Fixes

**Overengineering**
- **Symptom:** Asked for one function, got an entire module with abstract base classes.
- **Fix:** "Keep it minimal. One function, not a framework. No extra features."

**Hallucinations**
- **Symptom:** Agent used a column name that doesn't exist in the data.
- **Fix:** "Never speculate about code you have not opened. Read the file first."

**Going Off-Rails**
- **Symptom:** Looked away for 5 minutes, agent rewrote half the project.
- **Fix:** Check in every 2-3 tool calls. "Don't change functions that already pass tests."

### Steering Phrases Cheatsheet

| When the agent... | Say this |
|---|---|
| **Uses pandas** | "Rewrite using PySpark. We never use pandas." |
| **Ignores CLAUDE.md** | "Read CLAUDE.md first, then try again." |
| **Rewrites working code** | "Don't change functions that already pass tests." |
| **Writes code before tests** | "Stop. Write the tests first, then implement." |
| **Too complex** | "Simplify. I just need [specific thing]." |
| **Stuck in a loop** | "Stop. Let's try a different approach." |
| **Speculates** | "Read the file first. Don't guess." |
| **Hasn't planned** | "Stop. Use /plan first. Interview me about what I need." |
| **Claims it works** | "Prove it. Show me the git diff. Grill me on these changes." |
| **First attempt is mediocre** | "Knowing everything you know now, scrap this and implement the elegant solution." |

**Healthy cadence:** Agent makes 2-3 tool calls -> You review -> Steer if needed -> Continue

### Commit as Checkpoints

Commit every 15-20 minutes during the labs. Commits are your safety net:

- **Before big changes:** `/commit` to save what works
- **If the agent goes off-rails:** Press `Esc` twice to cancel, then `git checkout` to revert
- **Why it matters:** You can always get back to a known-good state. Don't let 30 minutes of work ride on a single uncommitted session.

---

## 18. Workshop Quick Reference

### Key Commands

```bash
# Check environment
databricks auth status
claude --version

# Run tests (always use -x for fail-fast)
pytest tests/ -x
pytest tests/test_pipeline.py -k "bronze" -x
pytest tests/test_pipeline.py -k "silver" -x
pytest tests/test_app.py -x

# Deploy with Databricks Asset Bundles
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run grocery-intelligence-TEAM -t dev

# Deploy web app
cd app && databricks apps deploy \
  --name grocery-app-TEAM \
  --source-code-path ./
```

### Key Files

| File | Purpose |
|---|---|
| `CLAUDE.md` | Agent instructions (team standards) |
| `tests/conftest.py` | PySpark test fixtures |
| `src/bronze/` | Raw data ingestion |
| `src/silver/` | Cleaned transformations |
| `src/gold/` | Aggregated analytics |
| `app/app.py` | FastAPI web application |
| `databricks.yml` | DABs deployment config |

### Workshop Schedule

| Time | Session |
|---|---|
| 9:30 AM | Block A: How to Think (theory) |
| 10:45 AM | Lab 0: Guided Hands-On (all together) |
| 11:30 AM | Block C: Tools for the Labs (theory) |
| 12:00 PM | Lab 1: Track-specific lab |
| 1:00 PM | Lunch break |
| 2:00 PM | Lab 2: Track-specific lab |
| 3:30 PM | Demos & wrap-up |

### Checkpoint Recovery

No shame in using checkpoints -- the goal is a working demo!

Tell the agent:

```text
Copy the checkpoint tables from workshop_vibe_coding.checkpoints
into my schema workshop_vibe_coding.<team_schema>
```

---

## 19. Advanced -- Self-Improving CLAUDE.md

Your CLAUDE.md is static by default. You write it once, the agent follows it, and mistakes repeat across sessions. This technique turns it into a **living document** that gets smarter every time you use it.

### The Reflection Prompt

When Claude makes a mistake, say:

```text
Reflect on this mistake. Abstract and generalize the learning.
Write it to CLAUDE.md.
```

That one sentence triggers the agent to:

1. **Reflect** -- Analyse what went wrong while full context is still in memory
2. **Abstract** -- Extract the general pattern, not the specific instance
3. **Generalize** -- Create a reusable rule for similar future situations
4. **Document** -- Write it to CLAUDE.md following the meta-rules below

### The Session Review Prompt

At the end of a session, ask:

```text
Review this session. Did you make any mistakes I should capture?
Did I ask you to do anything three or more times that you should
do automatically? Draft the rules and add them to CLAUDE.md.
```

The agent identifies patterns like *"You corrected me on PySpark three times"* and drafts a standing rule. Over time, corrections you give once become permanent.

### Meta-Rules -- Teaching the Agent to Write Good Rules

Add this section to your CLAUDE.md to control how rules get written:

```markdown
## META -- Maintaining This Document

When adding rules to this file:
1. Use absolute directives -- Start with "NEVER" or "ALWAYS"
2. Lead with why -- Explain the problem before the solution (1-3 bullets max)
3. Be concrete -- Include actual commands or code, not vague guidance
4. One rule per entry -- No compound rules that mix concerns
5. Keep it under 80 lines total -- If it's longer, move detail to a separate doc
```

**Why meta-rules matter:** Without them, the agent writes verbose paragraphs with examples and caveats. With them, every rule is terse and actionable. CLAUDE.md stays lean.

### Anti-Bloat: When NOT to Add a Rule

Not every correction deserves a permanent rule. Before adding to CLAUDE.md, ask:

| Question | If "No"... |
|---|---|
| Will this mistake happen again without the rule? | Don't add it -- one-off fixes don't need rules |
| Is this specific to my project, not general knowledge? | Don't add it -- the agent already knows general best practices |
| Does it affect more than one file or function? | Don't add it -- local fixes stay local |

### The Compounding Effect

- **Session 1** -- Agent makes basic mistakes. You capture 3 rules (5 seconds each).
- **Session 2** -- Those mistakes vanish. New, more sophisticated ones surface.
- **Session 3** -- You're discussing architecture instead of fighting over import order.

Each rule is permanent progress. Like your test suite, CLAUDE.md is a ratchet -- quality only goes up.

> **Monday morning action #2:** After your first real session with Claude Code, run the session review prompt. Capture the top 3 corrections as rules. Within a week, your CLAUDE.md will be more valuable than any style guide your team has written.

---

## 20. Key Takeaways

1. **Write clear specs** -- CLAUDE.md, tests, and PRDs define what "done" looks like. The agent can only be as good as your specification.
2. **Use tests as executable specs (TDD)** -- Tests are unambiguous. They pass or they fail. No interpretation required. Write them first, always.
3. **Give agents verification mechanisms** -- Tests, screenshots, expected outputs. The agent needs a feedback loop to self-correct without human intervention.
4. **Manage context windows** -- Keep CLAUDE.md lean (~50 lines), be specific with requests, use new sessions for new tasks.
5. **Steer early and often** -- Review every 2-3 tool calls. Short feedback loops produce better results than long unsupervised runs.
6. **Make CLAUDE.md self-improving** -- Capture mistakes as rules. Run session reviews. Your agent gets smarter every day without extra effort.

**Think of yourself as a director, not a typist.**

> **Monday morning action:** Create a CLAUDE.md for your team's main repository. Start with tech stack, coding standards, and 5 rules. After your first real session, run the reflection prompt and capture what you learned. Iterate from there.

> **The discipline transfers:** These practices work with Claude Code, Cursor, Windsurf, GitHub Copilot, and any agentic coding tool. The discipline is the differentiator, not the tool.
