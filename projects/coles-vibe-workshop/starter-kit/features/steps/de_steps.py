from behave import given, then

REGIONS = {
    "1": "New South Wales", "2": "Victoria", "3": "Queensland",
    "4": "South Australia", "5": "Western Australia", "6": "Tasmania",
    "7": "Northern Territory", "8": "Australian Capital Territory",
}
INDUSTRIES = {
    "20": "Food retailing", "41": "Clothing, footwear and personal accessories",
    "42": "Department stores", "43": "Other retailing",
    "44": "Cafes, restaurants and takeaway", "45": "Household goods retailing",
}

@given('I have region code "{code}"')
def step_region_code(context, code):
    context.region_code = code

@then('the decoded state should be "{state}"')
def step_decoded_state(context, state):
    actual = REGIONS.get(context.region_code, "Unknown")
    assert actual == state, f"Expected '{state}', got '{actual}'"

@given('I have industry code "{code}"')
def step_industry_code(context, code):
    context.industry_code = code

@then('the decoded industry should be "{name}"')
def step_decoded_industry(context, name):
    actual = INDUSTRIES.get(context.industry_code, "Unknown")
    assert actual == name, f"Expected '{name}', got '{actual}'"

@given('I have time period "{tp}"')
def step_time_period(context, tp):
    context.time_period = tp
    if "-Q" in tp:
        year, q = tp.split("-Q")
        context.parsed_year = int(year)
        context.parsed_month = (int(q) - 1) * 3 + 1
    else:
        parts = tp.split("-")
        context.parsed_year = int(parts[0])
        context.parsed_month = int(parts[1])

@then('the parsed year should be {year:d}')
def step_parsed_year(context, year):
    assert context.parsed_year == year

@then('the parsed month should be {month:d}')
def step_parsed_month(context, month):
    assert context.parsed_month == month
