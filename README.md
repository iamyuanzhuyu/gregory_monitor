# gregory Monitor

一个自动监控gregory 网站折扣信息并发送邮件通知的Python脚本。

## 功能特点

- 自动监控指定网站的折扣信息
- 发现折扣时自动发送邮件通知
- 支持自定义监控间隔
- 完善的日志记录
- 错误处理和自动重试机制

## 安装要求

- Python 3.7+
- pip

## 依赖安装

```bash
pip install -r requirements.txt
```

## 配置说明

在项目根目录创建 `.env` 文件，配置以下参数：

```env
# Gmail 配置
EMAIL_USER=your-email@gmail.com
EMAIL_PWD=your-app-password

# 监控配置
WEBSITE_URL=https://example.com
CHECK_INTERVAL=1800
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER=your-email@gmail.com
RECEIVER=receiver@example.com
USER_AGENT=Mozilla/5.0 ...
```

## 使用方法

```bash
python gregory_monitor.py
```

## 部署说明

详细的部署说明请参考 [deployment.md](deployment.md)。

## 许可证

MIT License
