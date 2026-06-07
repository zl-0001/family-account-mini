"""微信API调用工具"""
import httpx
from app.core.config import settings


class WeChatService:
    """微信接口服务"""

    @staticmethod
    def code2session(js_code: str) -> dict:
        """
        通过 code 换取 session
        返回 openid 和 session_key
        文档: https://developers.weixin.qq.com/miniprogram/dev/OpenAPI/login/login.html
        """
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": settings.WEIXIN_APPID,
            "secret": settings.WEIXIN_APPSECRET,
            "js_code": js_code,
            "grant_type": "authorization_code",
        }
        try:
            response = httpx.get(url, params=params, timeout=httpx.Timeout(10.0, connect=5.0))
            data = response.json()
        except httpx.TimeoutException:
            raise Exception("微信服务器连接超时，请检查网络后重试")
        except Exception as e:
            raise Exception(f"微信登录失败: {str(e)}")

        if "errcode" in data and data["errcode"] != 0:
            raise Exception(f"微信登录失败: {data.get('errmsg', '未知错误')}")

        return data
