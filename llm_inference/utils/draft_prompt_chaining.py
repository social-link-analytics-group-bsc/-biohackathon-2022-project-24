import json

def get_completion(prompt):
    # This function would call your AI model to get the completion
    # For the purpose of this example, we will simulate responses
    if "sex demographic information" in prompt:
        return "Yes#####Table#####sex percentages are mentioned in text but detailed counts are in tables."
    elif "extract demographic values from the table" in prompt:
        # Simulated response for demographic extraction from a table
        return """{
            "TOTAL": 1395,
            "SAMPLE": 1395,
            "N_MALE": 940,
            "N_FEMALE": 455,
            "PERC_MALE": 67.38,
            "PERC_FEMALE": 32.62
        }"""
    elif "extract demographic values from the text" in prompt:
        # Simulated response for demographic extraction from text
        return """{
            "SAMPLE": 120,
            "N_MALE": 50,
            "N_FEMALE": 70,
            "PERC_MALE": 41.67,
            "PERC_FEMALE": 58.33
        }"""

def first_prompt(text):
    prompt_1 = f"""
    Does the text include sex demographic information (i.e., male and female participant counts or percentages)? 
    Answer 'Yes' or 'No'. If 'Yes', indicate whether this information is primarily presented in text or table format, 
    or in both. If both formats are present, prioritize tables for extraction unless explicitly instructed otherwise. 
    Indicate the format: 'Text', 'Table', or 'Both'.

    <text>
    {text}
    </text>
    """
    response = get_completion(prompt_1)
    
    # Process the response
    response_parts = response.split('#####')
    demographic_info = response_parts[0].strip()
    format_choice = response_parts[1].strip() if len(response_parts) > 1 else None
    justification = response_parts[2].strip() if len(response_parts) > 2 else None

    return demographic_info, format_choice, justification

def second_prompt_table():
    prompt_2 = f"""
    Extract the following demographic values from the table:
    
    SAMPLE: Largest initial participant count across all studies/groups
    N_MALE: Total male participants across all studies/groups
    N_FEMALE: Total female participants across all studies/groups
    PERC_MALE: Overall male percentage (only if explicitly mentioned)
    PERC_FEMALE: Overall female percentage (only if explicitly mentioned)

    Use the table's total n for demographic calculations, but do not use the table’s n for SAMPLE if a larger count exists elsewhere. 
    Multiply each group size by sex percentages, round to whole numbers, and sum the male/female counts across groups. 
    Return values in JSON format.
    
    Example: Variable | eoCAD Probands | ACS Probands | MI Cases | Controls | Aorta Samples --------|----------------|--------------|----------|----------|--------------- n | 422 | 228 | 368 | 289 | 88 Sex: Male | 70.6% | 72% | 83% | 43.0% | 55.2%
    Explanation: Let’s think step by step. The table provides data on five groups. I start by calculating the explicit total sample size, which is 422 + 228 + 368 + 289 + 88 = 1395. The total number of males is also explicit and calculated for each group as follows: 422 * 0.706 = 298 males, 228 * 0.72 = 164 males, 368 * 0.83 = 305 males, 289 * 0.43 = 124 males, and 88 * 0.552 = 49 males. This results in a total of 298 + 164 + 305 + 124 + 49 = 940 males. Since the number of females is implicit, it is calculated as 1395 - 940 = 455 females. The percentages are 67.38% males and 32.62% females. So the answer is:  { "TOTAL": 1395,"SAMPLE": 1395,  "N_MALE": 940,  "N_FEMALE": 455, "PERC_MALE": 67.38,   "PERC_FEMALE": 32.62}

    Example: Table 1Subject characteristics at baseline1VLCARBVLFHUFmales/females4/205/173/18BMI kg/m232.5 \u00b1 3.132.6 \u00b1 4.033.4 \u00b1 3.6AGE y48.4 \u00b1 8.050.7 \u00b1 10.346.1 \u00b1 9.5Total Cholesterol mmol/L5.8 \u00b1 1.05.6 \u00b1 1.16.0 \u00b1 1.1LDL-C mmol/L3.8 \u00b1 0.83.6 \u00b1 1.14.0 \u00b1 1.1HDL-C mmol/L1.2 \u00b1 0.21.3 \u00b1 0.31.2 \u00b1 0.2Triacylglycerols mmol/L1.8 \u00b1 0.91.5 \u00b1 0.61.6 \u00b1 0.51 Data are Mean \u00b1 SD. VLCARB = very low carbohydrate diet (n = 24) VLF = very low fat diet (n = 22) HUF = high unsaturated fat (n = 21)
    Explanation: Let’s think step by step. The table presents subject characteristics at baseline. I start by extracting the explicit values for males and females: Males/Females = 4/20, 5/17, 3/18. To find the total number of males and females, I sum the values for each group: total males = 4 + 5 + 3 = 12 males, and total females = 20 + 17 + 18 = 55 females. The overall number of participants is 12 males + 55 females = 67. So the answer is:  { "TOTAL": 67, "SAMPLE": 67, "N_MALE": 12, "N_FEMALE": 55, "PERC_MALE": null, "PERC_FEMALE": null }
    """
    
    response = get_completion(prompt_2)
    return json.loads(response)

def second_prompt_text():
    prompt_3 = f"""
    Extract the following demographic values from the text:
    
    SAMPLE: Largest initial participant count across all studies/groups
    N_MALE: Total male participants across all studies/groups
    N_FEMALE: Total female participants across all studies/groups
    PERC_MALE: Overall male percentage (only if explicitly mentioned)
    PERC_FEMALE: Overall female percentage (only if explicitly mentioned)

    Use the largest initial participant count for SAMPLE. Use specifically reported demographic totals for sex calculations. 
    If only total and one sex count is provided, infer the other sex. If percentages and total are given, calculate the counts. 
    Use the total explicitly associated with sex demographics for these calculations. Return values in JSON format.
    """
    
    response = get_completion(prompt_3)
    return json.loads(response)

def run_linear_pipeline(text):
    # Step 1: Check for demographic information
    demographic_info, format_choice, justification = first_prompt(text)

    if demographic_info == "No":
        print("There is no sex demographic information in the text.")
        return None
    else:
        print(f"Demographic Info: {demographic_info}")
        print(f"Format Choice: {format_choice}")
        print(f"Justification: {justification}")

        # Step 2: Handle based on format choice
        if format_choice.lower() == 'table':
            demographic_data = second_prompt_table()
        elif format_choice.lower() == 'text':
            demographic_data = second_prompt_text()
        else:
            print("Invalid format choice. Please enter 'Text', 'Table', or 'Both'.")
            return None

        # Output the result in JSON format
        print(json.dumps(demographic_data, indent=2))
        return demographic_data

# Sample text for demonstration
text = """
In a study of 200 participants, 120 were male and 80 were female. The percentages of male participants were 
60% and female participants were 40%. Data presented in Table 1 showed similar demographic breakdowns.
"""

# Run the pipeline
run_linear_pipeline(text)
