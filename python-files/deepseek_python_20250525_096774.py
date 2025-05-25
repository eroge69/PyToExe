import pandas as pd
import numpy as np

# --- 1. DEFINE SURVEY STRUCTURE AND HEADCOUNT DATA ---

# Define the structure based on 'Head Count List.pdf'
# Department: {Position: Headcount}
headcount_data = {
    "Executive Management Office Dept.": {"Manager": 2, "Frontline Staff (Junior/Senior Assistant)": 9, "Assistant Supervisor/Supervisor": 3},
    "Compliance Dept.": {"Senior Manager": 1, "Assistant Supervisor/Supervisor": 3, "Assistant Manager": 1},
    "Corporate Affairs Dept.": {"Assistant Supervisor/Supervisor": 1},
    "Government and Corporate Affairs Dept.": {"Assistant Manager/Manager/Senior Manager": 1},
    "Exploration & JV Dept.": {"Assistant Manager/Manager/Senior Manager": 3, "Assistant Supervisor/Supervisor": 1},
    "Geology & Geoscience Dept.": {"Assistant Manager/Manager/Senior Manager": 2, "Assistant Supervisor/Supervisor": 8}, # Combined the two supervisor roles
    "PPE Dept.": {"Assistant Manager/Manager/Senior Manager": 2, "Assistant Supervisor/Supervisor": 2},
    "Technical Dept.": {"Assistant Manager/Manager/Senior Manager": 2},
    "PIP Dept.": {"Assistant Manager/Manager/Senior Manager": 2, "Assistant Supervisor/Supervisor": 21},
    "IT Department": {"Assistant Manager/Manager/Senior Manager": 1, "Assistant Supervisor/Supervisor": 5},
    "Drilling Dept.": {"Assistant Manager/Manager/Senior Manager": 1},
    "CSR & Communications Dept.": {"Assistant Manager/Manager/Senior Manager": 1, "Assistant Supervisor/Supervisor": 3, "Frontline Staff (Junior/Senior Assistant)": 6},
    "HR Dept.": {"Assistant Manager/Manager/Senior Manager": 2, "Assistant Supervisor/Supervisor": 3, "Frontline Staff (Junior/Senior Assistant)": 2},
    "Reservoir Engineering Dept.": {"Assistant Manager/Manager/Senior Manager": 1, "Assistant Supervisor/Supervisor": 5}, # Interpreted 'Kyaw Soe Oo, U' as a supervisor role
    "Heath, Safety & Environmental Dept.": {"Assistant Manager/Manager/Senior Manager": 2, "Assistant Supervisor/Supervisor": 3, "Frontline Staff (Junior/Senior Assistant)": 6},
    "Design Team": {"Assistant Manager/Manager/Senior Manager": 1, "Assistant Supervisor/Supervisor": 1, "Frontline Staff (Junior/Senior Assistant)": 2},
    "Admin. & Contracts Dept.": {"Assistant Manager/Manager/Senior Manager": 1, "Assistant Supervisor/Supervisor": 1, "Frontline Staff (Junior/Senior Assistant)": 9},
    "Multimedia Team": {"Assistant Manager/Manager/Senior Manager": 1, "Assistant Supervisor/Supervisor": 1},
    "Finance Dept.": {"Assistant Manager/Manager/Senior Manager": 1, "Assistant Supervisor/Supervisor": 7, "Frontline Staff (Junior/Senior Assistant)": 7},
    "Internal Audit Dept.": {"Assistant Manager/Manager/Senior Manager": 1, "Assistant Supervisor/Supervisor": 5, "Frontline Staff (Junior/Senior Assistant)": 1},
    "Material & Logistic Dept.": {"Assistant Manager/Manager/Senior Manager": 2, "Assistant Supervisor/Supervisor": 3, "Frontline Staff (Junior/Senior Assistant)": 2}
}

# Define survey options from 'OR Questionnaires.pdf'
demographic_options = {
    "Gender": ["Male", "Female"],
    "Age (Years)": ["20-30", "30-40", "Above 40"],
    "Marital Status": ["Single", "Married", "Others (Divorced/Widowed/Separated)"],
    "Education": ["Graduated", "Master", "Doctorate"],
    "Year of Service": ["Less than 1 year", "1 to 3 years", "3 to 5 years", "Over 5 years"]
}

# Define the Likert scale questions from Section B
likert_questions = {
    "RF1": "Regulatory requirements are clearly communicated to employees.",
    "RF2": "Regulatory framework positively impacts safety and environmental standards.",
    "RF3": "Regulatory changes are promptly addressed by the company.",
    "RF4": "Company provides adequate training on regulatory compliance.",
    "RF5": "Company balances regulatory compliance with operational flexibility.",
    "RF6": "Compliance with regulations enhances operational efficiency.",
    "SC1": "Employees are adequately trained to perform their tasks.",
    "SC2": "Staff capacity impacts the company's operational excellence.",
    "SC3": "Training programs align with the operational needs of the organization.",
    "SC4": "Company provides sufficient opportunities for skill development.",
    "SC5": "Employees have access to the necessary resources to perform their duties.",
    "SC6": "Retention strategies for high-performing employees are effectively implemented.",
    "FC1": "Company's leadership style supports operational excellence.",
    "FC2": "Organizational structure facilitates effective decision-making.",
    "FC3": "Company encourages cross-departmental collaboration.",
    "FC4": "Organizational culture promotes innovation and continuous improvement.",
    "FC5": "Departmental goals align with the overall objectives of the company.",
    "FC6": "Company adapts to external market and regulatory changes.",
    "IT1": "Company utilize technology to enhance operational efficiency.",
    "IT2": "IT systems are well-integrated across all departments to enhance operation.",
    "IT3": "Investments in modern IT infrastructure are adequate.",
    "IT4": "Technology adoption has improved operation transparency.",
    "IT5": "Technology improves decision-making processes for operation.",
    "IT6": "Adoption of IT systems improve staff capacity through operational excellence.",
    "OE1": "Company achieves its production and performance targets.",
    "OE2": "Operational processes are highly efficient.",
    "OE3": "Safety standards during operations are maintained.",
    "OE4": "Cost-effective measures are implemented for operation.",
    "OE5": "Continuous improvement is encouraged and supported for operation.",
    "OE6": "Company follows regulatory and environmental standards.",
    "OE7": "Productivity levels are consistently high across all departments.",
    "OE8": "Company is responsive to operational and market challenges."
}

# --- 2. PREPARE RESPONDENT LIST BASED ON HEADCOUNT ---

total_employees = sum(sum(d.values()) for d in headcount_data.values())
target_respondents = 130

employee_list = []
for dept, positions in headcount_data.items():
    for pos, count in positions.items():
        num_respondents = int(round(count / total_employees * target_respondents))
        for _ in range(num_respondents):
            employee_list.append({"Department": dept, "Employment Position": pos})

# Adjust if rounding caused a mismatch, ensuring we have exactly 130
while len(employee_list) < target_respondents:
    # Add from the largest departments if list is short
    dept = max(headcount_data, key=lambda k: sum(headcount_data[k].values()))
    pos = max(headcount_data[dept], key=headcount_data[dept].get)
    employee_list.append({"Department": dept, "Employment Position": pos})

employee_list = employee_list[:target_respondents]
np.random.shuffle(employee_list) # Shuffle to randomize the order

# --- 3. GENERATE SURVEY RESPONSES ---

survey_data = []

for employee in employee_list:
    response = employee.copy()
    pos = response["Employment Position"]

    # Generate correlated demographic data
    if "Manager" in pos or "Director" in pos:
        age = np.random.choice(["30-40", "Above 40"], p=[0.4, 0.6])
        service = np.random.choice(["3 to 5 years", "Over 5 years"], p=[0.3, 0.7])
        education = np.random.choice(["Graduated", "Master", "Doctorate"], p=[0.2, 0.6, 0.2])
        marital = np.random.choice(["Single", "Married", "Others (Divorced/Widowed/Separated)"], p=[0.1, 0.8, 0.1])
    elif "Supervisor" in pos:
        age = np.random.choice(["30-40", "Above 40"], p=[0.6, 0.4])
        service = np.random.choice(["1 to 3 years", "3 to 5 years", "Over 5 years"], p=[0.3, 0.5, 0.2])
        education = np.random.choice(["Graduated", "Master"], p=[0.6, 0.4])
        marital = np.random.choice(["Single", "Married", "Others (Divorced/Widowed/Separated)"], p=[0.3, 0.6, 0.1])
    else: # Frontline Staff
        age = np.random.choice(["20-30", "30-40"], p=[0.7, 0.3])
        service = np.random.choice(["Less than 1 year", "1 to 3 years", "3 to 5 years"], p=[0.4, 0.5, 0.1])
        education = np.random.choice(["Graduated", "Master"], p=[0.9, 0.1])
        marital = np.random.choice(["Single", "Married"], p=[0.6, 0.4])

    response["Gender"] = np.random.choice(demographic_options["Gender"])
    response["Age (Years)"] = age
    response["Marital Status"] = marital
    response["Education"] = education
    response["Year of Service"] = service

    # Generate positively-biased Likert scale answers
    # Scale: 1=SD, 2=D, 3=N, 4=A, 5=SA
    # Probability is skewed towards 4 (Agree) and 5 (Strongly Agree)
    for q_code, q_text in likert_questions.items():
        response[q_text] = np.random.choice(
            [1, 2, 3, 4, 5],
            p=[0.02, 0.03, 0.15, 0.50, 0.30] # 80% chance of 4 or 5
        )

    survey_data.append(response)

# --- 4. CREATE AND SAVE THE EXCEL FILE ---

# Create a DataFrame from the list of response dictionaries
df = pd.DataFrame(survey_data)

# Reorder columns to match the questionnaire flow
column_order = [
    "Gender", "Age (Years)", "Marital Status", "Education",
    "Employment Position", "Department", "Year of Service"
] + list(likert_questions.values())
df = df[column_order]

# Define the output filename
output_filename = "Generated_Survey_Responses_130.xlsx"

# Save the DataFrame to an Excel file
df.to_excel(output_filename, index=False)

print(f"Successfully generated the survey data for 130 respondents and saved it as '{output_filename}'")