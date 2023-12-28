import openai
from config import conf
from utils.log import logger
from common.session import Session
from common.reply import Reply, ReplyType
from common.context import ContextType, Context
import re


def process_message(msg):
    # 移除包含特定关键词的Markdown代码块
    cleaned_msg = re.sub(r'```[\s\S]*?(prompt|search\(|mclick\()[\s\S]*?```', '', msg)

    # 提取并下载图片
    image_regex = re.compile(r'!\[image]\((.*?)\)')
    matches = image_regex.findall(cleaned_msg)
    # 检查是否有找到图片链接
    if len(matches) > 0:
        # 有图片链接时，返回 imgflag=1 和第一个图片链接
        return 1, matches[0]
    else:
        # 没有图片链接时，返回 imgflag=0 和清理后的消息
        # 移除包含 ![image] 的行和前后的空白行
        cleaned_msg = re.sub(r'^\s*.*!\[image\].*\n', '', cleaned_msg, flags=re.MULTILINE)
        # 移除包含 [下载链接] 的行和前后的空白行
        cleaned_msg = re.sub(r'^\s*.*\[下载链接\].*\n', '', cleaned_msg, flags=re.MULTILINE)
        cleaned_msg = re.sub(r'^\s*\n+', '', cleaned_msg)
        cleaned_msg = re.sub(r'\[\[\d+\]\(https?:\/\/[^\]]+\)\]', '', cleaned_msg)

    return 0, cleaned_msg


class ChatGPTBot:
    def __init__(self):
        openai.api_key = conf().get("openai_api_key")
        api_base = conf().get("openai_api_base")
        proxy = conf().get("proxy")
        if api_base:
            openai.api_base = api_base
        if proxy:
            openai.proxy = proxy
        self.name = self.__class__.__name__
        self.args = {
            "model": conf().get("model"),
            "temperature": conf().get("temperature"),
        }

    def reply(self, context: Context) -> Reply:
        query = context.query
        logger.info(f"[{self.name}] Query={query}")
        if context.type == ContextType.CREATE_IMAGE:
            return self.reply_img(query)
        else:
            session_id = context.session_id
            session = Session.build_session_query(context)
            response = self.reply_text(session)
            logger.info(f"[{self.name}] Response={response['content']}")
            if response["completion_tokens"] > 0:
                Session.save_session(
                    response["content"], session_id, response["total_tokens"]
                )
            img_flag, reply_content = process_message(response["content"])
            if img_flag == 1:
                reply = Reply(ReplyType.IMAGE, reply_content)
            else:
                reply = Reply(ReplyType.TEXT, reply_content)

            return reply

    def reply_img(self, query) -> Reply:
        create_image_size = conf().get("create_image_size", "512x512")
        create_image_model = conf().get("create_image_model", "dall-e-3")
        create_image_style = conf().get("create_image_style", "vivid")
        create_image_quality = conf().get("create_image_quality", "standard")

        try:
            response = openai.Image.create(prompt=query, model=create_image_model, n=1, size=create_image_size,
                                           style=create_image_style, quality=create_image_quality)
            image_url = response["data"][0]["url"]
            logger.info(f"[{self.name}] Image={image_url}")
            return Reply(ReplyType.IMAGE, image_url)
        except Exception as e:
            logger.error(f"[{self.name}] Create image failed: {e}")
            return Reply(ReplyType.TEXT, "Image created failed")

    def reply_text(self, session):
        try:
            response = openai.ChatCompletion.create(
                messages=session,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                **self.args,
            )
            return {
                "total_tokens": response["usage"]["total_tokens"],
                "completion_tokens": response["usage"]["completion_tokens"],
                "content": response.choices[0]["message"]["content"],
            }
        except Exception as e:
            result = {"completion_tokens": 0, "content": "Please ask me again"}
            if isinstance(e, openai.error.RateLimitError):
                logger.warn(f"[{self.name}] RateLimitError: {e}")
                result["content"] = "Ask too frequently, please try again in 20s"
            elif isinstance(e, openai.error.APIConnectionError):
                logger.warn(f"[{self.name}] APIConnectionError: {e}")
                result[
                    "content"
                ] = "I cannot connect the server, please check the network and try again"
            elif isinstance(e, openai.error.Timeout):
                logger.warn(f"[{self.name}] Timeout: {e}")
                result["content"] = "I didn't receive your message, please try again"
            elif isinstance(e, openai.error.APIError):
                logger.warn(f"[{self.name}] APIError: {e}")
            else:
                logger.exception(f"[{self.name}] Exception: {e}")
        return result
