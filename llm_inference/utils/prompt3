import json

# JSON response format
json_response_format = {
    "SAMPLE": "<number|null>",
    "N_MALE": "<number|null>",
    "N_FEMALE": "<number|null>", 
    "PERC_MALE": "<number|null>",
    "PERC_FEMALE": "<number|null>"
}

# Convert the response format to JSON string
json_string = json.dumps(json_response_format, indent=4)

# Prompt instructions
prompt_instruction = f"""
Extract these demographic values from scientific text:
SAMPLE: Largest initial participant count across all studies/groups
N_MALE: Total male participants across all studies/groups
N_FEMALE: Total female participants across all studies/groups
PERC_MALE: Overall male percentage (only if explicitly mentioned)
PERC_FEMALE: Overall female percentage (only if explicitly mentioned)

Core Rules:
- Two-tier counting system: Use the largest initial participant count for SAMPLE and use the demographic total explicitly associated with sex calculations.
- Only count unique human participants. Include cells/tissue only if from distinct individuals.
- Calculate implicit values when possible (e.g., if total + one sex is given, infer the other sex; if percentage + total is given, calculate count).
- Assign "null" if unclear/missing, or if a calculation is too speculative.

Special Cases:
- Pre-filtering counts should be used over post-filtering counts.
- Sum participants across all groups/cohorts and avoid double-counting.
- Use sex-specific conditions (e.g., prostate = male).
- For demographic tables with multiple groups, identify if the table uses a filtered/reduced sample. Use the total "n" for demographic calculations, unless a larger count exists. Multiply group size by sex percentages and round calculations to the nearest whole number.

Example with table from text:
Groups and n values:
- eoCAD Probands (n=422): 70.6% male
- ACS Probands (n=228): 72% male
- MI Cases (n=368): 83% male
- Controls (n=289): 43% male
- Aorta Samples (n=88): 55.2% male

Output JSON Example:
{
  "SAMPLE": 1395,
  "N_MALE": 940,
  "N_FEMALE": 455,
  "PERC_MALE": null,
  "PERC_FEMALE": null
}

Think step-by-step:
- Identify the maximum participant count.
- Extract explicit sex counts/percentages.
- Calculate any implicit values.
- Verify no double-counting.
- Format the final JSON output.
"""
