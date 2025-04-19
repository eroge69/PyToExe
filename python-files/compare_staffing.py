
import pandas as pd
import re
from rapidfuzz import process, fuzz

# === ПУТИ К ФАЙЛАМ ===
fact_file = "Укомплектованность_март.xlsx"
plan_file = "Итоговые_ставки_по_ТО.xlsx"
output_file = "Final_Comparison.xlsx"

# === ЧИСТКА НАЗВАНИЙ ===
def clean_name(name):
    name = str(name).lower().strip()
    name = re.sub(r"ф\d+", "", name)  # удаляем хвосты Ф400 и т.п.
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name

# === ЗАГРУЗКА ФАЙЛОВ ===
fact_df = pd.read_excel(fact_file)
plan_df = pd.read_excel(plan_file)

# Переименуем столбцы для читаемости
fact_df.columns = [col.strip() for col in fact_df.columns]
plan_df.columns = [col.strip() for col in plan_df.columns]

# Проверка колонок
assert "Подразделение" in fact_df.columns and "Факт март" in fact_df.columns, "Файл факта должен содержать 'Подразделение' и 'Факт март'"
assert "Подразделение" in plan_df.columns and "ШР" in plan_df.columns, "Файл плана должен содержать 'Подразделение' и 'ШР'"

# Чистим названия
fact_df["Подразделение_чисто"] = fact_df["Подразделение"].apply(clean_name)
plan_df["Подразделение_чисто"] = plan_df["Подразделение"].apply(clean_name)

# === СОВПАДЕНИЯ RAPIDFUZZ ===
fact_names = fact_df["Подразделение_чисто"].unique()
plan_names = plan_df["Подразделение_чисто"].unique()

matches = []
for fact_name in fact_names:
    result = process.extractOne(fact_name, plan_names, scorer=fuzz.token_sort_ratio)
    if result:
        match, score, _ = result
        if score >= 90:
            matches.append({
                "Подразделение_факт": fact_name,
                "Подразделение_план": match,
                "score": score
            })

matched_df = pd.DataFrame(matches)
print(f"Совпадений найдено: {len(matched_df)}")

# === ОБЪЕДИНЕНИЕ ===
merged = pd.merge(
    fact_df.merge(matched_df, left_on="Подразделение_чисто", right_on="Подразделение_факт"),
    plan_df, left_on="Подразделение_план", right_on="Подразделение_чисто",
    suffixes=("_март", "_аналитика")
)

# === ОТКЛОНЕНИЯ ===
merged["Отклонение март от аналитики"] = merged["Факт март"] - merged["ШР"]
merged["% Отклонения"] = (merged["Отклонение март от аналитики"] / merged["ШР"]) * 100
merged["% Отклонения"] = merged["% Отклонения"].round(2)

# === СОХРАНЕНИЕ ===
merged.to_excel(output_file, index=False)
print(f"Готово! Файл сохранён как: {output_file}")
