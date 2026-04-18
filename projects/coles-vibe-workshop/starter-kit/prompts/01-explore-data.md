## Step 1: Explore the Data

Before writing any code, understand what the raw data looks like.

### Prompt

Paste this into Claude Code:

```
Fetch a sample of the ABS Retail Trade API and show me the columns, data types, and 3 sample rows:
https://data.api.abs.gov.au/data/ABS,RT,1.0.0/M1.20+41+42+43+44+45.20.1+2+3+4+5+6+7+8.M?format=csv&startPeriod=2024-01&endPeriod=2024-03

Also fetch the ABS CPI Food API and show me the same:
https://data.api.abs.gov.au/data/ABS,CPI,2.0.0/1.10001+20001.10.1+2+3+4+5+6+7+8.Q?format=csv&startPeriod=2024-Q1&endPeriod=2024-Q4

For each API, show me:
1. All column names and their data types
2. 3 sample rows
3. What the coded values mean (REGION, INDUSTRY, INDEX columns)
```

### Expected Result

You should see a table of columns for each API. Key columns:
- **Retail Trade:** DATAFLOW, FREQ, MEASURE, INDUSTRY, REGION, TIME_PERIOD, OBS_VALUE
- **CPI Food:** DATAFLOW, FREQ, MEASURE, INDEX, REGION, TIME_PERIOD, OBS_VALUE

The REGION, INDUSTRY, and INDEX columns contain numeric codes (e.g., "1" for NSW).

### If It Doesn't Work

- **API timeout:** The ABS APIs can be slow. Wait 30 seconds and try again.
- **Network error:** Check you have internet access from the terminal. Try `curl -I https://data.api.abs.gov.au`.
- **Still failing:** Skip this step — you can see sample data in `starter-kit/conftest.py`.
