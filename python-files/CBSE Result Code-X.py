import re
import csv

def parse_results(filename):
    results = []

    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Updated regex to capture any number of subject codes after "COMP" result
        match = re.match(
            r"^(\d{8})\s+([MF])\s+([A-Z .]+?)\s+((?:\d{3}\s+)+)(?:[A1-E2 ]+)?\s+(PASS|ABST|ESSENTIAL REPEAT|COMP)\s*(.*)$",
            line
        )

        if match:
            roll_no = match.group(1)
            gender = match.group(2)
            name = match.group(3).strip()
            subject_codes = re.findall(r"\d{3}", match.group(4))
            result_status = match.group(5)
            comp_raw = match.group(6).strip()
            comp_subs = re.findall(r"\d{3}", comp_raw) if result_status == "COMP" else []

            i += 1
            subjects = []
            if i < len(lines):
                mark_line = lines[i].strip()
                marks_grades = re.findall(r"(\d{2,3}|AB)\s+([A-E1-2]{1,2})", mark_line)

                for idx, code in enumerate(subject_codes):
                    if idx < len(marks_grades):
                        marks, grade = marks_grades[idx]
                        subjects.append((code, marks, grade))

            results.append({
                'roll_no': roll_no,
                'gender': gender,
                'name': name,
                'subjects': subjects,
                'result': result_status,
                'comp_subs': comp_subs
            })

        i += 1

    return results

def export_to_csv(data, output_file):
    max_subjects = max(len(entry['subjects']) for entry in data)

    headers = ['Roll No', 'Gender', 'Name']
    for i in range(1, max_subjects + 1):
        headers += [f'Sub{i} Code', f'Sub{i} Marks', f'Sub{i} Grade']
    headers += ['Result', 'Comp Subjects']

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for entry in data:
            row = [entry['roll_no'], entry['gender'], entry['name']]
            for subj in entry['subjects']:
                row.extend(subj)
            while len(row) < len(headers) - 2:
                row.extend(['', '', ''])
            row.append(entry['result'])
            row.append(', '.join(entry.get('comp_subs', [])))
            writer.writerow(row)

# --- Run the full process ---
filen = input("Enter File Name=")
filename = filen + ".TXT"
parsed_data = parse_results(filename)
export_to_csv(parsed_data, filen + '_results.csv')

print('Exported to ' + filen + '_results.csv with all compartment subjects included.')
