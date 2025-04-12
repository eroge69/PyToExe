
import pandas as pd
from datetime import datetime
import os

MATERIALS_FILE = "materials.csv"
PRODUCTION_FILE = "production.csv"

def load_data():
    if os.path.exists(MATERIALS_FILE):
        materials_df = pd.read_csv(MATERIALS_FILE)
    else:
        materials_df = pd.DataFrame(columns=["Дата", "Материал", "Кол-во", "Цена за ед."])

    if os.path.exists(PRODUCTION_FILE):
        production_df = pd.read_csv(PRODUCTION_FILE)
    else:
        production_df = pd.DataFrame(columns=["Дата выпуска", "Товар", "Кол-во", "Материал", "Расход на ед."])

    return materials_df, production_df

def fifo_allocation(materials_df, required_qty):
    allocations = []
    remaining_qty = required_qty

    for idx, row in materials_df.iterrows():
        available = row["Кол-во"]
        if available <= 0:
            continue
        taken = min(available, remaining_qty)
        cost = taken * row["Цена за ед."]
        allocations.append({
            "Источник партии": f"{row['Дата']} (цена {row['Цена за ед.']})",
            "Кол-во списано": taken,
            "Цена за ед.": row["Цена за ед."],
            "Сумма": cost
        })
        materials_df.at[idx, "Кол-во"] -= taken
        remaining_qty -= taken
        if remaining_qty <= 0:
            break

    if remaining_qty > 0:
        raise ValueError("Недостаточно материалов для списания.")

    return allocations, materials_df

def calculate_production(materials_df, production_df):
    records = []
    for _, row in production_df.iterrows():
        qty = row["Кол-во"]
        material = row["Материал"]
        consumption = row["Расход на ед."]
        total_needed = qty * consumption

        allocations, materials_df = fifo_allocation(materials_df, total_needed)
        total_cost = sum(a["Сумма"] for a in allocations)
        cost_per_unit = round(total_cost / qty, 2)

        records.append({
            "Партия продукции": row["Дата выпуска"],
            "Кол-во": qty,
            "Себестоимость за ед.": cost_per_unit,
            "Сумма": round(total_cost, 2),
            "Источник материалов": "; ".join(f"{a['Кол-во списано']} по {a['Цена за ед.']}" for a in allocations)
        })

    return pd.DataFrame(records), materials_df

def save_to_excel(materials_df, production_df, report_df):
    with pd.ExcelWriter("fifo_costing_report.xlsx") as writer:
        materials_df.to_excel(writer, sheet_name="Остатки материалов", index=False)
        production_df.to_excel(writer, sheet_name="Производство", index=False)
        report_df.to_excel(writer, sheet_name="Готовая продукция", index=False)

def main():
    materials_df, production_df = load_data()
    report_df, updated_materials = calculate_production(materials_df.copy(), production_df)
    save_to_excel(updated_materials, production_df, report_df)
    print("Отчет успешно создан: fifo_costing_report.xlsx")

if __name__ == "__main__":
    main()
