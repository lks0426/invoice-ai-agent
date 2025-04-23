from openpyxl import load_workbook

def generate_excel_from_json(template_path: str, output_path: str, data_list: list):
    wb = load_workbook(template_path)
    sheet = wb["接待費申請書"]

    food_row = 5
    travel_row = 51

    for data in data_list:
        category = data.get("カテゴリ", "").strip()

        if "飲" in category:
            row = food_row
            food_row += 1
        elif "交" in category:
            row = travel_row
            travel_row += 1
        else:
            print("⚠️ カテゴリ不明，スキップ:", category)
            continue

        sheet[f"B{row}"] = data.get("日付", "")
        sheet[f"C{row}"] = data.get("取引先名", "")
        sheet[f"D{row}"] = data.get("項目", "")
        sheet[f"E{row}"] = data.get("支出明細", "")
        amount_str = data.get("金額（JPY)", "").replace(",", "")
        amount_value = int(amount_str) if amount_str else 0
        cell = sheet[f"H{row}"]
        cell.value = amount_value
        cell.number_format = '¥#,##0'
        #sheet[f"H{row}"] = data.get("金額（JPY)", "")
        # sheet[f"I{row}"] = data.get("番号", "")
        # sheet[f"J{row}"] = data.get("備考", "")

    wb.save(output_path)
    print(f"✅ Excel保存完了: {output_path}")
