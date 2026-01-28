# AstrBot 宝塔面板插件

该插件用于在 AstrBot 中调用宝塔面板（BT Panel）API，提供系统状态、站点列表与面板重启等常用操作。

## 功能
- `bt status`：查询系统状态。
- `bt sites`：查询站点列表。
- `bt restart panel`：重启面板服务。
- `bt help`：查看帮助。

## 安装
将仓库放入 AstrBot 插件目录，并在 AstrBot 配置中启用。

## 配置示例
```json
{
  "base_url": "https://example.com:8888",
  "api_key": "your-api-key",
  "timeout_seconds": 10,
  "verify_tls": true,
  "token_mode": "time+md5key"
}
```

## 签名模式说明
- `time+key`: `md5(time + key)`
- `time+md5key`: `md5(time + md5(key))`

## 开发
依赖 `requests`。

## 需求文档
见 `docs/requirements.md`。
