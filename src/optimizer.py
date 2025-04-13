import pandas as pd
from pulp import *

def load_data(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

def optimize_courses(vectorized_df, requirement_counts,
                     excluded_departments=None,
                     excluded_course_codes=None,
                     excluded_keywords=None,
                     max_solutions=1):
    # Handle default arguments
    if excluded_departments is None:
        excluded_departments = []
    if excluded_course_codes is None:
        excluded_course_codes = []
    if excluded_keywords is None:
        excluded_keywords = []

    # Apply filters
    vectorized_df = vectorized_df[
        ~vectorized_df['Course Code'].str.extract(r'[A-Z]+\s+([A-Z]+)', expand=False).isin(excluded_depts_exact) &
        ~vectorized_df['Course Code'].str.extract(r'([A-Z]+)', expand=False).isin(excluded_departments) &
        ~vectorized_df['Course Code'].isin(excluded_course_codes) &
        ~vectorized_df['Course Title'].str.contains('|'.join(excluded_keywords), case=False, na=False)
    ].reset_index(drop=True)



    # Setup
    hub_columns = [col for col in vectorized_df.columns if col in requirement_counts]
    A = vectorized_df[hub_columns].values
    b = [requirement_counts[col] for col in hub_columns]
    courses = vectorized_df["Course Code"] + " - " + vectorized_df["Course Title"]

    # Unique course code tracking
    vectorized_df["Course Key"] = vectorized_df["Course Code"].str.extract(r'([A-Z]+\s+\w+)', expand=False)
    course_keys = vectorized_df["Course Key"]
    course_key_to_indices = {}
    for idx, key in enumerate(course_keys):
        course_key_to_indices.setdefault(key, []).append(idx)

    # Create decision variables
    x = [LpVariable(f"x_{i}", cat=LpBinary) for i in range(len(courses))]

    # Define ILP
    prob = LpProblem("BU_Hub_Course_Selection", LpMinimize)
    prob += lpSum(x)

    for j, req in enumerate(hub_columns):
        prob += lpSum(A[i][j] * x[i] for i in range(len(courses))) >= b[j], f"Requirement_{req}"

    for key, indices in course_key_to_indices.items():
        if len(indices) > 1:
            prob += lpSum(x[i] for i in indices) <= 1, f"Unique_{key}"

    # Store all solutions
    found_solutions = []

    for _ in range(max_solutions):
        prob.solve(PULP_CBC_CMD(msg=0))

        if LpStatus[prob.status] != 'Optimal':
            break

        solution = set(i for i in range(len(courses)) if x[i].varValue == 1)
        found_solutions.append([courses[i] for i in solution])

        # Exclude this solution from next solve
        prob += lpSum([x[i] for i in solution]) <= len(solution) - 1

    return found_solutions


if __name__ == "__main__":
    # Load course data
    df = load_data("data/Vectorized_BU_Hub_Courses.csv")

    # Example requirement (edit this)
    requirement_counts = {
    'Philosophical Inquiry and Life’s Meanings': 1,
    'Aesthetic Exploration': 1,
    'Historical Consciousness': 1,
    'Social Inquiry I': 0,
    'Social Inquiry II': 0,
    'Scientific Inquiry I': 0,
    'Scientific Inquiry II': 0,
    'Quantitative Reasoning I': 0,
    'Quantitative Reasoning II': 0,
    'First-Year Writing Seminar': 0,
    'Writing-Intensive Course': 1,
    'Writing, Research, and Inquiry': 0,
    'Oral and/or Signed Communication': 0,
    'Digital/Multimedia Expression': 0,
    'Critical Thinking': 0,
    'Research and Information Literacy': 0,
    'Teamwork / Collaboration': 1,
    'Creativity / Innovation': 0,
    'The Individual in Community': 1,
    'Global Citizenship and Intercultural Literacy': 1,
    'Ethical Reasoning': 1
    }

    # Run optimizer
    solutions = optimize_courses(
        vectorized_df=df,
        requirement_counts=requirement_counts,
        # Example filters (edit this)
        excluded_departments=['SAR', 'QST'],
        excluded_depts_exact=['BI', 'PY'], 
        excluded_course_codes=['CAS WR 153E'],
        excluded_keywords=['Summer', 'Analysis'],
        max_solutions=5
    )

    # Print results
    for idx, sol in enumerate(solutions, start=1):
        print(f"\nSolution {idx}:")
        for course in sol:
            print("-", course)
