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
        self.api_url = f"{self.base_url}/api/trpc/model.getModelInfoList,scribble.getScribbleByLabel?batch=1&input=%7B%220%22%3A%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D%2C%221%22%3A%7B%22json%22%3A%7B%22label%22%3A%22homepage_banner%22%7D%7D%7D"

    def get_headers(self) -> Dict[str, str]:
        """获取必要的请求头"""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": f"{self.base_url}/",
            "Origin": self.base_url,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

    def get_cookies(self) -> Dict[str, str]:
        """从环境变量获取 session token 并构建 cookies"""
        # 从环境变量获取 YUPP_TOKENS
        env_tokens = os.getenv("YUPP_TOKENS")
        if not env_tokens:
            print("警告: YUPP_TOKENS 环境变量未设置")
            return {}

        try:
            # 支持逗号分隔的多个token，取第一个
            tokens = [token.strip() for token in env_tokens.split(",") if token.strip()]
            if not tokens:
                print("警告: 未找到有效的 token")
                return {}

            # 使用第一个有效的 token
            token = tokens[0]
            return {"__Secure-yupp.session-token": token}

        except Exception as e:
            print(f"警告: 解析 YUPP_TOKENS 环境变量失败: {e}")
            return {}


# 初始化配置
config = YuppConfig()


def fetch_model_data() -> Optional[List[Dict[str, Any]]]:
    """获取模型数据"""
    try:
        # 创建 session 并设置 cookies
        session = requests.Session()
        cookies = config.get_cookies()
        headers = config.get_headers()

        # 设置 cookies
        for key, value in cookies.items():
            session.cookies.set(key, value)

        print(f"正在请求: {config.api_url}")
        response = session.get(config.api_url, headers=headers, timeout=30)

        print(f"响应状态码: {response.status_code}")

        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return None

        # 解析 JSON 响应
        print(response.text)
        response_data = response.json()
        print("成功获取并解析JSON数据")

        # 提取模型列表数据
        if isinstance(response_data, list) and len(response_data) > 0:
            return response_data[0]["result"]["data"]["json"]
        else:
            print("响应数据格式异常")
            return None

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
        return None
    except (ValueError, json.JSONDecodeError) as e:
        print(f"JSON解析失败: {e}")
        if "response" in locals():
            print(f"响应内容: {response.text[:200]}")
        return None
    except KeyError as e:
        print(f"数据结构解析失败: {e}")
        return None


def load_fallback_data() -> List[Dict[str, Any]]:
    """从本地文件加载备用数据"""
    try:
        with open("models.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("未找到 models.json 备用文件")
        return []
    except json.JSONDecodeError as e:
        print(f"备用文件 JSON 解析失败: {e}")
        return []


# 模型数据将在 main() 函数中获取


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
    # 支持的模型家族
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
        # 过滤条件：支持的家族或特殊功能
        if (
            item.get("family") in supported_families
            or item.get("isImageGeneration")
            or item.get("isAgent")
            or item.get("isLive")
        ):

            # 生成标签
            tags = generate_model_tags(item)

            # 构建显示名称
            label = item.get("label", "")
            if tags:
                label += "\n" + " | ".join(tags)

            # 构建处理后的模型数据
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
    models: List[Dict[str, Any]], filename: str = "model.json"
) -> bool:
    """保存模型数据到文件"""
    try:
        # 确保父目录存在
        dir_name = os.path.dirname(filename)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        # 若文件不存在则先创建
        if not os.path.exists(filename):
            try:
                with open(filename, "x", encoding="utf-8") as _:
                    pass
                print(f"已创建文件: {filename}")
            except FileExistsError:
                # 并发场景下可能被其他进程创建，忽略
                pass

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(models, f, indent=4, ensure_ascii=False)
        print(f"成功保存 {len(models)} 个模型到 {filename}")
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False


def fetch_and_save_models(filename: str = "model.json") -> bool:
    """获取并保存模型数据到指定文件"""
    # 加载环境变量
    load_dotenv()

    print("=== 自动获取 Yupp 模型数据 ===")

    # 检查必要的环境变量
    if not os.getenv("YUPP_TOKENS"):
        print("警告: YUPP_TOKENS 环境变量未设置，无法自动获取模型数据")
        return False

    # 获取模型数据
    data = fetch_model_data()
    if not data:
        print("API 请求失败，尝试加载本地备用数据...")
        data = load_fallback_data()

    # 处理模型数据
    if data:
        print(f"开始处理 {len(data)} 个模型数据...")
        processed_models = filter_and_process_models(data)
        return save_models_to_file(processed_models, filename)
    else:
        print("没有可用的模型数据")
        return False


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    print("=== Yupp 模型数据获取工具 ===")

    # 检查必要的环境变量
    if not os.getenv("YUPP_TOKENS"):
        print("警告: YUPP_TOKENS 环境变量未设置")
        print("请设置 YUPP_TOKENS 环境变量，例如：")
        print("export YUPP_TOKENS='your_token_here'")
        return False

    # 获取模型数据
    data = fetch_model_data()
    if not data:
        print("API 请求失败，尝试加载本地备用数据...")
        data = load_fallback_data()

    # 处理模型数据
    if data:
        print(f"开始处理 {len(data)} 个模型数据...")
        processed_models = filter_and_process_models(data)
        save_models_to_file(processed_models)
    else:
        print("没有可用的模型数据")
        return False

    return True


if __name__ == "__main__":
    main()
