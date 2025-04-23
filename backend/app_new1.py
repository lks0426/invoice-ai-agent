# app.py (FastAPI 实现，将所有结果合并到一个 Excel 文件)
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
from typing import List
import json

# 假设原 OCR 部分保留：可以替换为你实际使用的 OCR 模块
#from gpt_invoice_parser import ask_gpt4_vision_about_invoice, generate_excel_from_json
from gpt_invoice_parser import generate_excel_from_json  # 如果 OCR 已经改为 Agentify，那么这个函数也可调整

# 替换为调用 Agentify 接口的同步版本
from utils import agentify_sync

app = FastAPI()

# CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 文件路径设置（请根据实际环境修改）
UPLOAD_FOLDER = "D:/invoice-ai-agent/uploads"
OUTPUT_FOLDER = "D:/invoice-ai-agent/outputs"
TEMPLATE_PATH = "D:/invoice-ai-agent/sample_data/接待費申請書テンプレート.xlsx"
FINAL_OUTPUT_PATH = "D:/invoice-ai-agent/outputs/final_output.xlsx"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.post("/parse")
async def parse_invoice(images: List[UploadFile] = File(...)):
    
    print('---------------')
    
    results = []

    for idx, image in enumerate(images):
        filename = image.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(await image.read())

        print(f"📄 処理中: {filename}")

        # ----- 使用 Agentify 接口解析文本 -----
        # 假设你有一个 OCR 模块取得图片中的文本，此处用 read_text_from_image 代替
        # 如果你仍需要调用 ask_gpt4_vision_about_invoice，可按需替换
        ocr_text = ""   # 此处请放置实际 OCR 处理代码，得到文本内容
        # 例如：ocr_text = read_text_from_image(filepath)

        # 使用 Agentify 接口对 OCR 得到的文本进行结构化解析
        try:
            result_json_str = await agentify_sync(ocr_text)
            # 尝试将 JSON 字符串转换为字典
            result_data = json.loads(result_json_str)
        except Exception as e:
            result_data = {"error": str(e)}
        
        results.append({
            "filename": filename,
            "result": result_data
        })

    return JSONResponse({
        "results": results
    })

@app.post("/generate_excel")
async def generate_excel(selected: List[dict] = Body(...)):
    # 将传入的 selected 数据（JSON 格式）写入 Excel
    generate_excel_from_json(TEMPLATE_PATH, FINAL_OUTPUT_PATH, selected, start_row=5)
    
    print('----------------TEMPLATE_PATH------------------')
    print(TEMPLATE_PATH)
    
    print('----------------FINAL_OUTPUT_PATH------------------')
    print(FINAL_OUTPUT_PATH)
    
    return {"download_url": f"/download/{os.path.basename(FINAL_OUTPUT_PATH)}"}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "ファイルが見つかりません"})
    return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=filename)

# 如果原先还存在异步轮询等路由，此处已删除或注释
