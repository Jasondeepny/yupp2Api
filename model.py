import json
import requests
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv


# 配置类
class YuppConfig:
    """Yupp API 配置管理"""

    def __init__(self):
        self.base_url = "https://yupp.ai"
        # 注意：这个 URL 是 URL-encoded 的 tRPC 请求（保持原样）
        self.api_url = f"{self.base_url}/api/trpc/model.getModelInfoList,scribble.getScribbleByLabel?batch=1&input=%7B%220%22%3A%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D%2C%221%22%3A%7B%22json%22%3A%7B%22label%22%3A%22homepage_banner%22%7D%7D%7D"

    def get_headers(self) -> Dict[str, str]:
        """获取必要的请求头"""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Referer": f"{self.base_url}/",
            "Origin": self.base_url,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

    def get_cookies(self) -> Dict[str, str]:
        """从环境变量获取 session token 并构建 cookies"""
        env_tokens = os.getenv("YUPP_TOKENS")
        if not env_tokens:
            print("警告: YUPP_TOKENS 环境变量未设置")
            return {}

        try:
            tokens = [token.strip() for token in env_tokens.split(",") if token.strip()]
            if not tokens:
                print("警告: 未找到有效的 token")
                return {}
            token = tokens[0]
            return {"__Secure-yupp.session-token": token}
        except Exception as e:
            print(f"警告: 解析 YUPP_TOKENS 环境变量失败: {e}")
            return {}


# 初始化配置
config = YuppConfig()


def fetch_model_data() -> Optional[List[Dict[str, Any]]]:
    """获取模型数据（更鲁棒地解析可能带前缀的 JSON 响应）"""
    try:
        session = requests.Session()
        cookies = config.get_cookies()
        headers = config.get_headers()

        # 设置 cookies 到 session
        for key, value in cookies.items():
            session.cookies.set(key, value)

        print(f"正在请求: {config.api_url}")
        response = session.get(config.api_url, headers=headers, timeout=30)
        print(f"响应状态码: {response.status_code}")

        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容（前200字符）: {response.text[:200]!r}")
            return None

        text = response.text or ""
        if not text.strip():
            print("响应体为空，无法解析 JSON")
            return None

        # 先尝试 requests 自带的 json()（快速路径）
        response_data = None
        try:
            response_data = response.json()
            print("成功使用 response.json() 解析 JSON")
        except (ValueError, json.JSONDecodeError):
            # 如果失败，尝试去除常见 XSSI / 前缀直到第一个 { 或 [
            trimmed = text.lstrip()
            first_idx = None
            for i, ch in enumerate(trimmed):
                if ch in ('{', '['):
                    first_idx = i
                    break
            if first_idx is None:
                print("无法在响应中找到 JSON 的开始字符 ('{' 或 '[')。响应前200字符:")
                print(trimmed[:200])
                return None
            cleaned = trimmed[first_idx:]
            try:
                response_data = json.loads(cleaned)
                print("通过清理前缀成功解析 JSON（去掉了前导非 JSON 内容）")
            except Exception as e:
                print(f"JSON 解析失败（去除前缀后仍然失败）: {e}")
                print("响应前200字符:", trimmed[:200])
                return None

        # 现在尝试从解析后的 response_data 中提取模型列表
        data = None

        # 常见 tRPC/批量返回：列表，其中每项包含 result.data.json
        if isinstance(response_data, list) and len(response_data) > 0:
            # 尝试在列表中的对象里找 result -> data -> json
            for entry in response_data:
                if isinstance(entry, dict) and "result" in entry:
                    result = entry.get("result", {})
                    if isinstance(result, dict):
                        dat = result.get("data") or result.get("data", {})
                        if isinstance(dat, dict) and "json" in dat:
                            data = dat["json"]
                            break
                        if isinstance(dat, list):
                            data = dat
                            break
            # 若没有找到嵌套结构，尝试把整个 response_data 当作模型列表
            if data is None:
                # 如果第一个元素本身可能就是返回的 json 列表
                if isinstance(response_data[0], dict) and "json" in response_data[0]:
                    data = response_data[0]["json"]
                else:
                    data = response_data

        elif isinstance(response_data, dict):
            # 处理 dict 返回：可能形如 { "result": { "data": { "json": [...] } } }
            if "result" in response_data:
                result = response_data.get("result", {})
                if isinstance(result, dict):
                    dat = result.get("data") or result.get("data", {})
                    if isinstance(dat, dict) and "json" in dat:
                        data = dat["json"]
                    elif isinstance(dat, list):
                        data = dat
                    elif isinstance(dat, dict) and dat:
                        data = dat
            elif "data" in response_data:
                data = response_data["data"]
            elif "json" in response_data:
                data = response_data["json"]
            else:
                # 如果 dict 直接就是列表的映射，则把它包成列表返回
                data = response_data

        else:
            # 其他情况：直接赋值
            data = response_data

        # 规范化返回：尽量返回 List[Dict]
        if isinstance(data, list):
            print(f"成功获取模型数据（列表，共 {len(data)} 条）")
            return data

        if isinstance(data, dict):
            # 尝试从常见键中抽取列表
            for candidate in ("models", "items", "list", "data"):
                if candidate in data and isinstance(data[candidate], list):
                    return data[candidate]
            # 如果真的是单个模型对象，封装为列表返回
            return [data]

        print("响应数据格式无法识别，无法提取模型列表。响应前200字符：")
        print(text[:200])
        return None

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
        return None


def load_fallback_data() -> List[Dict[str, Any]]:
    """从本地文件加载备用数据（models.json）"""
    try:
        with open("models.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("未找到 models.json 备用文件")
        return []
    except json.JSONDecodeError as e:
        print(f"备用文件 JSON 解析失败: {e}")
        return []


def generate_model_tags(item: Dict[str, Any]) -> List[str]:
    """生成模型标签"""
    tags = []
    tag_mapping = {
        "isPro": "☀️",
        "isMax": "🔥",
        "isNew": "🆕",
        "isLive": "🎤",
        "isAgent": "🤖",
        "isFast": "🚀",
        "isReasoning": "🧠",
        "isImageGeneration": "🎨",
    }

    for key, emoji in tag_mapping.items():
        if item.get(key, False):
            tags.append(emoji)

    # 检查是否支持附件
    if (
        item.get("supportedAttachmentMimeTypes")
        and len(item["supportedAttachmentMimeTypes"]) > 0
    ):
        tags.append("📎")

    return tags


def filter_and_process_models(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """过滤和处理模型数据"""
    supported_families = [
        "GPT",
        "Claude",
        "Gemini",
        "Qwen",
        "DeepSeek",
        "Perplexity",
        "Kimi",
    ]

    processed_models = []

    for item in data:
        if (
            item.get("family") in supported_families
            or item.get("isImageGeneration")
            or item.get("isAgent")
            or item.get("isLive")
        ):

            tags = generate_model_tags(item)

            label = item.get("label", "")
            if tags:
                label += "\n" + " | ".join(tags)

            processed_item = {
                "id": item.get("id"),
                "name": item.get("name"),
                "label": label,
                "shortLabel": item.get("shortLabel"),
                "publisher": item.get("publisher"),
                "family": item.get("family"),
                "isPro": item.get("isPro", False),
                "isInternal": item.get("isInternal", False),
                "isMax": item.get("isMax", False),
                "isLive": item.get("isLive", False),
                "isNew": item.get("isNew", False),
                "isImageGeneration": item.get("isImageGeneration", False),
                "isAgent": item.get("isAgent", False),
                "isReasoning": item.get("isReasoning", False),
                "isFast": item.get("isFast", False),
            }
            processed_models.append(processed_item)

    return processed_models


def save_models_to_file(
    models: List[Dict[str, Any]], filename: str = "models.json"
) -> bool:
    """保存模型数据到文件"""
    try:
        dir_name = os.path.dirname(filename)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        if not os.path.exists(filename):
            try:
                with open(filename, "x", encoding="utf-8") as _:
                    pass
                print(f"已创建文件: {filename}")
            except FileExistsError:
                pass

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(models, f, indent=4, ensure_ascii=False)
        print(f"成功保存 {len(models)} 个模型到 {filename}")
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False


def fetch_and_save_models(filename: str = "models.json") -> bool:
    """获取并保存模型数据到指定文件"""
    load_dotenv()
    print("=== 自动获取 Yupp 模型数据 ===")

    if not os.getenv("YUPP_TOKENS"):
        print("警告: YUPP_TOKENS 环境变量未设置，无法自动获取模型数据")
        return False

    data = fetch_model_data()
    if not data:
        print("API 请求失败，尝试加载本地备用数据...")
        data = load_fallback_data()

    if data:
        print(f"开始处理 {len(data)} 个模型数据...")
        processed_models = filter_and_process_models(data)
        return save_models_to_file(processed_models, filename)
    else:
        print("没有可用的模型数据")
        return False


def main():
    """主函数"""
    load_dotenv()
    print("=== Yupp 模型数据获取工具 ===")

    if not os.getenv("YUPP_TOKENS"):
        print("警告: YUPP_TOKENS 环境变量未设置")
        print("请设置 YUPP_TOKENS 环境变量，例如：")
        print("export YUPP_TOKENS='your_token_here'")
        return False

    data = fetch_model_data()
    if not data:
        print("API 请求失败，尝试加载本地备用数据...")
        data = load_fallback_data()

    if data:
        print(f"开始处理 {len(data)} 个模型数据...")
        processed_models = filter_and_process_models(data)
        save_models_to_file(processed_models)  # 默认保存到 models.json
    else:
        print("没有可用的模型数据")
        return False

    return True


if __name__ == "__main__":
    main()
