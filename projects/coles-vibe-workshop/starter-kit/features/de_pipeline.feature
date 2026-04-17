@local @smoke
Feature: Fast local validation
  As a workshop team
  I want to validate my transformation logic locally
  So that I catch bugs before deploying to Databricks

  Scenario: Region codes decode correctly
    Given I have region code "1"
    Then the decoded state should be "New South Wales"

  Scenario: Industry codes decode correctly
    Given I have industry code "20"
    Then the decoded industry should be "Food retailing"

  Scenario: Monthly time periods parse correctly
    Given I have time period "2024-01"
    Then the parsed year should be 2024
    And the parsed month should be 1

  Scenario: Quarterly time periods parse correctly
    Given I have time period "2024-Q3"
    Then the parsed year should be 2024
    And the parsed month should be 7
