from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
from typing import List
from gpt_invoice_parser import generate_excel_from_json  # ✅ Excel处理逻辑

app = FastAPI()

# ✅ 跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 安全环境下可以限制为 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 路径设置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

UPLOAD_FOLDER = os.path.join(ROOT_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(ROOT_DIR, "outputs")
TEMPLATE_PATH = os.path.join(ROOT_DIR, "sample_data", "接待費申請書テンプレート.xlsx")
FINAL_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, "final_output.xlsx")

# ✅ 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ Excel导出接口
@app.post("/generate_excel")
async def generate_excel(selected: List[dict] = Body(...)):
    print("✅ /generate_excel 接口被调用")
    print(f"📌 TEMPLATE_PATH: {TEMPLATE_PATH}")
    print(f"📌 FINAL_OUTPUT_PATH: {FINAL_OUTPUT_PATH}")
    print(f"📥 接收到的数据: {selected}")

    try:
        generate_excel_from_json(TEMPLATE_PATH, FINAL_OUTPUT_PATH, selected)
        return {"download_url": f"/download/{os.path.basename(FINAL_OUTPUT_PATH)}"}
    except Exception as e:
        print(f"❌ Excel生成失败: {e}")
        return JSONResponse(status_code=500, content={"error": "Excel生成失败", "detail": str(e)})

# ✅ Excel文件下载接口
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    print(f"📁 请求下载文件路径: {file_path}")

    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "ファイルが見つかりません"})
    return FileResponse(
        file_path,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=filename
    )
