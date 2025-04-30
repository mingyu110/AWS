import json
import time
import hmac
import hashlib
import base64
import urllib.parse
import urllib.request

class DingTalkClient:
    """
    钉钉机器人通知客户端
    """
    def __init__(self, webhook_url, secret=None):
        """
        初始化钉钉机器人客户端
        
        Args:
            webhook_url (str): 钉钉机器人 Webhook URL
            secret (str, optional): 钉钉机器人安全密钥
        """
        self.webhook_url = webhook_url
        self.secret = secret
        
    def _generate_sign(self):
        """
        生成签名
        
        Returns:
            str: 签名参数字符串
        """
        if not self.secret:
            return ""
            
        timestamp = str(int(time.time() * 1000))
        string_to_sign = f'{timestamp}\n{self.secret}'
        hmac_code = hmac.new(
            self.secret.encode(), 
            string_to_sign.encode(), 
            digestmod=hashlib.sha256
        ).digest()
        
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return f"&timestamp={timestamp}&sign={sign}"
    
    def send_text(self, content, at_mobiles=None, at_all=False):
        """
        发送文本消息
        
        Args:
            content (str): 消息内容
            at_mobiles (list, optional): 要@的手机号列表
            at_all (bool, optional): 是否@所有人
            
        Returns:
            dict: 钉钉 API 响应
        """
        if not at_mobiles:
            at_mobiles = []
            
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                "atMobiles": at_mobiles,
                "isAtAll": at_all
            }
        }
        
        return self._send_request(data)
    
    def send_markdown(self, title, text, at_mobiles=None, at_all=False):
        """
        发送 Markdown 消息
        
        Args:
            title (str): 消息标题
            text (str): Markdown 格式消息内容
            at_mobiles (list, optional): 要@的手机号列表
            at_all (bool, optional): 是否@所有人
            
        Returns:
            dict: 钉钉 API 响应
        """
        if not at_mobiles:
            at_mobiles = []
            
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                "atMobiles": at_mobiles,
                "isAtAll": at_all
            }
        }
        
        return self._send_request(data)
        
    def _send_request(self, data):
        """
        发送请求到钉钉 API
        
        Args:
            data (dict): 请求数据
            
        Returns:
            dict: 钉钉 API 响应
        """
        sign_url = self._generate_sign()
        webhook_url = f"{self.webhook_url}{sign_url}"
        
        headers = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        
        # 构建请求
        request = urllib.request.Request(
            url=webhook_url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        
        try:
            # 发送请求
            response = urllib.request.urlopen(request)
            result = response.read().decode('utf-8')
            return json.loads(result)
        except Exception as e:
            print(f"钉钉通知发送失败: {str(e)}")
            return {"errcode": -1, "errmsg": str(e)} 