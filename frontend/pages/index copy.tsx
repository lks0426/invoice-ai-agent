// frontend/pages/index.tsx
import { useState } from 'react';
import Head from 'next/head';
import axios from 'axios';

export default function Home() {
  const [images, setImages] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [selected, setSelected] = useState<boolean[]>([]);

  const handleFiles = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setImages(files);
      setSelected(files.map(() => true)); // 默认全选
    }
  };

  const handleSubmit = async () => {
    const formData = new FormData();
    images.forEach((file) => formData.append('images', file));
    setUploading(true);
    try {
      const res = await axios.post('http://localhost:8000/parse', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResults(res.data.results);
      setSelected(res.data.results.map(() => true)); // 设置默认选中
    } catch (err) {
      console.error('❌ Upload failed', err);
      alert('アップロードに失敗しました。サーバーが起動しているか確認してください。');
    } finally {
      setUploading(false);
    }
  };

  const handleCheckboxChange = (index: number) => {
    const newSelected = [...selected];
    newSelected[index] = !newSelected[index];
    setSelected(newSelected);
  };

  const handleDownload = async () => {
    const filtered = results.filter((_, i) => selected[i]);
    if (filtered.length === 0) return alert("少なくとも1つ選んでください");

    try {

      // 下载 Excel 文件真正数据
      const res = await axios.post('http://localhost:8000/generate_excel',
        filtered.map((r) => r.result)
      );
      const downloadUrl = 'http://localhost:8000' + res.data.download_url;

      const excelRes = await axios.get(downloadUrl, {
        responseType: 'blob'
      });

      const blob = new Blob([excelRes.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = '領収書出力.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error("❌ ダウンロード失敗", err);
      alert("Excelの生成またはダウンロードに失敗しました。");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <Head>
        <title>領収書 AI 解析</title>
      </Head>
      <div className="max-w-3xl mx-auto bg-white shadow p-6 rounded-md">
        <h1 className="text-2xl font-bold mb-4">📸 領収書 AI 解析システム</h1>

        <input
          type="file"
          accept="image/*"
          multiple
          onChange={handleFiles}
          className="mb-4 w-full"
        />
        <button
          onClick={handleSubmit}
          disabled={uploading || images.length === 0}
          className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:bg-gray-300"
        >
          {uploading ? 'アップロード中...' : 'アップロードして解析'}
        </button>

        {results.length > 0 && (
          <div className="mt-6">
            <h2 className="text-lg font-semibold mb-2">解析結果</h2>
            <button
              onClick={handleDownload}
              className="mb-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              ✅ 選択した結果をExcelでダウンロード
            </button>
            <div className="space-y-4">
              {results.map((r, i) => (
                <div key={i} className="p-4 border rounded bg-gray-50">
                  <label className="flex items-center space-x-2 mb-2">
                    <input
                      type="checkbox"
                      checked={selected[i]}
                      onChange={() => handleCheckboxChange(i)}
                    />
                    <span className="font-medium">{r.filename}</span>
                  </label>
                  <pre className="text-sm whitespace-pre-wrap break-all bg-white p-2 rounded border">
                    {JSON.stringify(r.result, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
