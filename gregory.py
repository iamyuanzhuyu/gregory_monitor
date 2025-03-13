import os
from pathlib import Path
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Set, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    """配置数据类"""
    website_url: str
    check_interval: int
    smtp_server: str
    smtp_port: int
    email_user: str
    email_password: str
    sender: str
    receiver: str
    user_agent: str

    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量创建配置"""
        load_dotenv()
        return cls(
            website_url=os.getenv("WEBSITE_URL", ""),
            check_interval=int(os.getenv("CHECK_INTERVAL", 1800)),
            smtp_server=os.getenv("SMTP_SERVER", ""),
            smtp_port=int(os.getenv("SMTP_PORT", 587)),
            email_user=os.getenv("EMAIL_USER", ""),
            email_password=os.getenv("EMAIL_PWD", ""),
            sender=os.getenv("SENDER", ""),
            receiver=os.getenv("RECEIVER", ""),
            user_agent=os.getenv("USER_AGENT", "")
        )

    def validate(self) -> List[str]:
        """验证配置完整性"""
        errors = []
        for field, value in self.__dict__.items():
            if not value:
                errors.append(f"配置项 {field} 不能为空")
        return errors

# 将 DiscountMonitor 改名为更通用的名称，比如 GregoryMonitor
class GregoryMonitor:
    """折扣监控类"""
    def __init__(self, config: Config):
        self.config = config
        self.keywords: Set[str] = {
            'sale', 'discount', 'off', 
            'promo', 'coupon', 'clearance',
            '% off', 'special offer'
        }
        self.last_sent: float = 0
        self.cooldown: int = 86400  # 24小时冷却时间
        self._setup_logging()

    def _setup_logging(self) -> None:
        """设置日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            # 将日志文件名从 discount_monitor.log 改为 gregory.log
            filename='logs/gregory.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def check_discount(self) -> bool:
        """检查网站折扣信息"""
        try:
            headers = {
                'User-Agent': self.config.user_agent,
                'Referer': self.config.website_url
            }
            
            response = requests.get(
                self.config.website_url,
                headers=headers,
                timeout=15
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(["script", "style", "noscript"]):
                element.decompose()

            text = soup.get_text(separator=' ', strip=True).lower()
            found_keywords = [kw for kw in self.keywords if kw in text]
            
            if found_keywords:
                logging.info(f"发现折扣关键词：{', '.join(found_keywords)}")
                return True
                
            return False

        except requests.RequestException as e:
            logging.error(f"网络请求异常：{str(e)}")
            return False
        except Exception as e:
            logging.error(f"检查过程中发生异常：{str(e)}")
            return False

    def send_email(self) -> bool:
        """发送邮件通知"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            mail_content = f"""
            <h2>折扣提醒！</h2>
            <p>检测到 {self.config.website_url} 有促销活动</p>
            <p>立即查看：<a href="{self.config.website_url}">{self.config.website_url}</a></p>
            <p>检测时间：{current_time}</p>
            """

            message = MIMEText(mail_content, 'html', 'utf-8')
            # 更新发件人显示名称
            message['From'] = Header("Gregory 监控机器人", 'utf-8')
            message['To'] = Header(self.config.receiver, 'utf-8')
            message['Subject'] = Header("[重要] 发现打折信息！", 'utf-8')

            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_user, self.config.email_password)
                server.sendmail(
                    self.config.sender,
                    [self.config.receiver],
                    message.as_string()
                )
            logging.info("邮件发送成功")
            return True

        except smtplib.SMTPException as e:
            logging.error(f"SMTP错误：{str(e)}")
            return False
        except Exception as e:
            logging.error(f"邮件发送失败：{str(e)}")
            return False

    def run(self) -> None:
        """运行监控服务"""
        logging.info("启动折扣监控服务")
        
        while True:
            try:
                if self.check_discount():
                    current_time = time.time()
                    if (current_time - self.last_sent) > self.cooldown:
                        if self.send_email():
                            self.last_sent = current_time
                    else:
                        logging.info("检测到折扣，但仍在冷却期内")
                else:
                    logging.info("未检测到折扣信息")

                time.sleep(self.config.check_interval)
                
            except KeyboardInterrupt:
                logging.info("用户中断监控")
                break
            except Exception as e:
                logging.error(f"主循环异常：{str(e)}")
                time.sleep(300)  # 发生异常时等待5分钟后继续

def main():
    """主函数"""
    config = Config.from_env()
    
    if errors := config.validate():
        for error in errors:
            print(error)
        return
    
    # 更新实例化的类名
    monitor = GregoryMonitor(config)
    monitor.run()

if __name__ == "__main__":
    main()