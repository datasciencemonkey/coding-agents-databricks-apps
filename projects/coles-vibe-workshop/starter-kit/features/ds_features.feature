@ds @local
Feature: Feature Engineering for Retail Forecasting
  As a data scientist
  I need lag, seasonal, and growth features
  So that my model can learn temporal patterns in retail turnover

  Background:
    Given a time series of monthly retail turnover data
    And the data covers at least 24 months

  @lag
  Scenario: Lag features capture past values
    When I create lag features with windows 1, 3, 6, and 12 months
    Then lag_1m equals the previous month value
    And lag_12m equals the same month last year
    And the first 12 rows have null lag_12m

  @seasonal
  Scenario: Seasonal indicators decompose dates
    When I extract seasonal features from the date column
    Then month_of_year ranges from 1 to 12
    And quarter ranges from 1 to 4
    And is_december is true only for month 12
    And is_q4 is true only for months 10, 11, 12

  @growth
  Scenario: Growth rates measure change
    Given turnover this month is 4600 and last month was 4500
    And turnover 12 months ago was 4200
    When I calculate growth features
    Then MoM growth is approximately 2.22 percent
    And YoY growth is approximately 9.52 percent

  @schema
  Scenario: Feature table has all required columns
    When I assemble a complete feature row
    Then the row contains state, industry, month, turnover_millions
    And the row contains turnover_lag_1m, turnover_lag_3m, turnover_lag_6m, turnover_lag_12m
    And the row contains month_of_year, quarter, is_december, is_q4
    And the row contains turnover_mom_growth, turnover_yoy_growth, cpi_yoy_change

  @nulls
  Scenario: Key columns never have nulls
    When I assemble a feature row with valid inputs
    Then state is not null
    And industry is not null
    And month is not null
    And turnover_millions is not null
