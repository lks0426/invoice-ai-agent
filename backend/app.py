from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
from typing import List
from gpt_invoice_parser import generate_excel_from_json  # ✅ 只保留 Excel 输出逻辑

app = FastAPI()

# 跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路径配置
UPLOAD_FOLDER = "D:/invoice-ai-agent/uploads"
OUTPUT_FOLDER = "D:/invoice-ai-agent/outputs"
TEMPLATE_PATH = "D:/invoice-ai-agent/sample_data/接待費申請書テンプレート.xlsx"
FINAL_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, "final_output.xlsx")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ 前端点击导出 Excel 时会调用此接口
@app.post("/generate_excel")
async def generate_excel(selected: List[dict] = Body(...)):
    generate_excel_from_json(TEMPLATE_PATH, FINAL_OUTPUT_PATH, selected)
    return {"download_url": f"/download/{os.path.basename(FINAL_OUTPUT_PATH)}"}

# ✅ Excel 文件下载
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "ファイルが見つかりません"})
    return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=filename)
