import json
import requests

# 获取模型列表
url = "https://yupp.ai/api/trpc/model.getModelInfoList?batch=1&input={}"

# 添加请求头模拟浏览器请求
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Cookie": "",
}

try:
    # 创建一个session来自动处理压缩
    session = requests.Session()
    response = session.get(url, headers=headers)
    print(f"响应状态码: {response.status_code}")
    print(f"响应头Content-Encoding: {response.headers.get('Content-Encoding', 'none')}")
    
    response.raise_for_status()  # 检查HTTP错误
    
    # requests会自动解压缩，直接获取JSON
    response_data = response.json()
    print("成功获取并解析JSON数据")
        
except requests.exceptions.RequestException as e:
    print(f"网络请求失败: {e}")
    response_data = None
except (ValueError, json.JSONDecodeError) as e:
    print(f"JSON解析失败: {e}")
    print(f"响应内容: {response.text[:200] if 'response' in locals() else 'No response'}")
    response_data = None

# 根据响应结构提取json属性中的模型列表
if response_data and isinstance(response_data, list) and len(response_data) > 0:
    data = response_data[0]["result"]["data"]["json"]
else:
    # 从本地models.json文件中读取
    try:
        with open("models.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("未找到models.json文件，且API请求失败")
        data = []

res = []

for item in data:
    if (
        item["family"]
        in ["GPT", "Claude", "Gemini", "Qwen", "DeepSeek", "Perplexity", "Kimi"]
        or item["isImageGeneration"] == True
        or item["isAgent"] == True
        or item["isLive"] == True
    ):
        # 构建标签
        tags = []
        if item["isPro"]:
            tags.append("☀️")
        if item["isMax"]:
            tags.append("🔥")
        if item["isNew"]:
            tags.append("🆕")
        if item["isLive"]:
            tags.append("🎤")
        if item["isAgent"]:
            tags.append("🤖")
        if item["isFast"]:
            tags.append("🚀")
        if item["isReasoning"]:
            tags.append("🧠")
        if  item["isImageGeneration"]:
            tags.append("🎨")
        if item.get("supportedAttachmentMimeTypes") and len(item["supportedAttachmentMimeTypes"]) > 0:
            tags.append("📎")

        # 构建name，如果有标签就换行添加
        name = item["label"]
        if tags:
            name += "\n" + " | ".join(tags)

        new_item = {
            "id": item["id"],
            "name": item["name"],
            "label": name,
            "shortLabel": item["shortLabel"],
            "publisher": item["publisher"],
            "family": item["family"],
            "isPro": item["isPro"],
            "isInternal": item["isInternal"],
            "isMax": item["isMax"],
            "isLive": item["isLive"],
            "isNew": item["isNew"],
            "isImageGeneration": item["isImageGeneration"],
            "isAgent": item["isAgent"],
            "isReasoning": item["isReasoning"],
            "isFast": item["isFast"],
        }
        res.append(new_item)

with open("model.json", "w") as f:
    json.dump(res, f, indent=4)
