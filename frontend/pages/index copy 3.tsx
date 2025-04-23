import { useState } from 'react';
import Head from 'next/head';
import md5 from 'crypto-js/md5';

export default function Home() {
  const [images, setImages] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [selected, setSelected] = useState<boolean[]>([]);

  const handleFiles = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setImages(files);
      setSelected(files.map(() => true));
    }
  };

  const getBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const handleSubmit = async () => {
    if (images.length === 0) return alert("画像を選んでください");
    setUploading(true);

    const base64Images = await Promise.all(images.map(file => getBase64(file).then(base64 => ({ url: base64 }))));

    const authKey = '647c8bdbff6148b0aca615a6291b1ec1';
    const authSecret = 'bihcgEv0IJDFhZU4Bt5tC186GcT8okQr';
    const timestamp = Date.now().toString();
    const sign = md5(authKey + authSecret + timestamp).toString();

    const payload = {
      agentId: authKey,
      chatId: null,
      userChatInput: "請求書画像を読み取り、指定フォーマットのJSONで返してください。",
      images: base64Images,
      state: {},
      debug: false
    };

    try {
      const response = await fetch("https://agentify.jp/openapi/agents/chat/completions/v1", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          authKey,
          timestamp,
          sign
        },
        body: JSON.stringify(payload)
      });

      const json = await response.json();
      const text = json.choices?.map((c: any) => c.content).join('') || '';

      try {
        const parsed = JSON.parse(text);
        if (Array.isArray(parsed)) {
          setResults(parsed.map((r, i) => ({ filename: images[i]?.name || `file-${i}`, result: r })));
          setSelected(parsed.map(() => true));
        } else {
          alert("⚠️ JSON配列ではありません");
        }
      } catch (e) {
        console.warn("❌ JSON解析失敗：", e);
        alert("❌ JSON解析に失敗しました");
      }
    } catch (e) {
      console.error(e);
      alert("❌ 请求失败");
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
      const res = await fetch('http://localhost:8000/generate_excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filtered.map(r => r.result))
      });
      const { download_url } = await res.json();
      const excelRes = await fetch('http://localhost:8000' + download_url);
      const blob = await excelRes.blob();
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
    <div className="min-h-screen flex items-start justify-center bg-[#f1f4f9] py-16 px-6">
      <Head>
        <title>領収書 AI 解析システム</title>
      </Head>
      <div className="w-full max-w-7xl bg-white shadow-2xl p-10 rounded-3xl border border-blue-100">
        <h1 className="text-4xl font-bold text-blue-900 mb-10 text-center tracking-tight">📸 領収書 AI 解析システム</h1>

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-center sm:space-x-4 space-y-4 sm:space-y-0 mb-8">
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={handleFiles}
            className="text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <button
            onClick={handleSubmit}
            disabled={uploading || images.length === 0}
            className="bg-blue-600 text-white py-2 px-6 rounded-full hover:bg-blue-700 disabled:bg-gray-300"
          >
            {uploading ? 'アップロード中...' : 'アップロードして解析'}
          </button>
        </div>

        {results.length > 0 && (
          <div className="mt-10">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4 sm:mb-0">解析結果</h2>
              <button
                onClick={handleDownload}
                className="bg-green-600 text-white px-6 py-2 rounded-full hover:bg-green-700 shadow-sm"
              >
                ✅ 選択した結果をExcelでダウンロード
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full table-fixed text-sm text-gray-800 border border-gray-200 bg-white shadow rounded-xl">
                <colgroup>
                  <col className="w-[40px]" />
                  <col className="w-[200px]" />
                  <col className="w-[140px]" />
                  <col className="w-[220px]" />
                  <col className="w-[280px]" />
                  <col className="w-[100px]" />
                  <col className="w-[80px]" />
                </colgroup>
                <thead className="bg-blue-50 text-left">
                  <tr>
                    <th className="px-2 py-3 font-semibold">✔</th>
                    <th className="px-2 py-3 font-semibold">ファイル名</th>
                    <th className="px-2 py-3 font-semibold">日付</th>
                    <th className="px-2 py-3 font-semibold">取引先名</th>
                    <th className="px-2 py-3 font-semibold">支出明細</th>
                    <th className="px-2 py-3 font-semibold">金額</th>
                    <th className="px-2 py-3 font-semibold">カテゴリ</th>
                  </tr>
                </thead>
                <tbody className="bg-white">
                  {results.map((r, i) => (
                    <tr key={i} className="border-t hover:bg-gray-50">
                      <td className="px-2 py-2">
                        <input
                          type="checkbox"
                          checked={selected[i]}
                          onChange={() => handleCheckboxChange(i)}
                        />
                      </td>
                      <td className="px-2 py-2 font-mono text-blue-700 break-all whitespace-pre-wrap">{r.filename}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{r.result['日付']}</td>
                      <td className="px-2 py-2 break-words whitespace-pre-wrap">{r.result['取引先名'] || r.result['取引名']}</td>
                      <td className="px-2 py-2 break-words whitespace-pre-wrap">{r.result['支出明細'] || r.result['支明細'] || r.result['出明細']}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{r.result['金額（JPY)'] || r.result['金額JPY)'] || r.result['金（JPY)']}</td>
                      <td className="px-2 py-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${r.result['カテゴリ']?.includes('飲') ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                          {r.result['カテゴリ'] || r.result['']}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
