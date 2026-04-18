@pipeline @smoke
Feature: Grocery Intelligence Pipeline
  As a data engineer
  I want a medallion pipeline that ingests ABS retail and CPI data
  So that gold tables are ready for the workshop demo app

  Background:
    Given a connection to the Databricks workspace
    And the catalog "workshop_vibe_coding" exists
    And the schema "demo" exists

  Scenario: Bronze retail table has data from ABS
    When I query "workshop_vibe_coding.demo.bronze_abs_retail_trade"
    Then the table should have more than 8000 rows
    And the table should have columns "REGION, INDUSTRY, TIME_PERIOD, OBS_VALUE"

  Scenario: Bronze CPI table has data from ABS
    When I query "workshop_vibe_coding.demo.bronze_abs_cpi_food"
    Then the table should have more than 400 rows
    And the table should have columns "REGION, INDEX, TIME_PERIOD, OBS_VALUE"

  Scenario: Silver retail turnover has decoded states
    When I query "workshop_vibe_coding.demo.silver_retail_turnover"
    Then the table should have more than 7000 rows
    And the column "state" should contain "New South Wales"
    And the column "state" should not contain "1"
    And there should be 8 distinct values in "state"

  Scenario: Silver retail turnover has no nulls
    When I query "workshop_vibe_coding.demo.silver_retail_turnover"
    Then the column "date" should have zero nulls
    And the column "turnover_millions" should have zero nulls
    And all values in "turnover_millions" should be greater than 0

  Scenario: Silver food price index has quarterly dates
    When I query "workshop_vibe_coding.demo.silver_food_price_index"
    Then the table should have more than 400 rows
    And the column "state" should contain "Victoria"
    And the column "cpi_index" should have zero nulls

  Scenario: Gold retail summary has rolling averages and YoY growth
    When I query "workshop_vibe_coding.demo.gold_retail_summary"
    Then the table should have more than 1000 rows
    And the table should have columns "state, date, total_turnover, turnover_3m_avg, turnover_12m_avg, yoy_growth_pct"
    And there should be 8 distinct values in "state"
    And the column "turnover_3m_avg" should have zero nulls

  Scenario: Gold retail summary date range spans 2010 to 2025
    When I query "workshop_vibe_coding.demo.gold_retail_summary"
    Then the minimum value in "date" should be before "2010-06-01"
    And the maximum value in "date" should be after "2025-01-01"

  Scenario: Gold food inflation has YoY change percentages
    When I query "workshop_vibe_coding.demo.gold_food_inflation_yoy"
    Then the table should have more than 400 rows
    And the table should have columns "state, date, cpi_index, yoy_change_pct"
    And all values in "yoy_change_pct" should be between -50 and 100

  Scenario: NSW has the highest total retail turnover
    When I run SQL "SELECT state, SUM(total_turnover) as total FROM workshop_vibe_coding.demo.gold_retail_summary GROUP BY state ORDER BY total DESC LIMIT 1"
    Then the first row "state" should be "New South Wales"
