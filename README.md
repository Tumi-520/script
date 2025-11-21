# 每日天气推送 - 使用指南

## 1. 代码已就绪
我已经为您创建了所有必要的文件：
-   `weather_push/weather_push.py`: 核心脚本，用于获取天气并发送 QQ 消息。
-   `.github/workflows/daily_weather.yml`: 自动化配置，每天北京时间 09:00 运行。
-   `weather_push/requirements.txt`: 依赖库列表。

## 2. 关键步骤：配置 Secrets (必做)
为了让代码能运行，您必须在 GitHub 上配置密钥。

1.  **将代码推送到 GitHub**:
    -   请确保您当前的文件夹 `script` 是一个 GitHub 仓库，并将其推送到 GitHub。
2.  **打开 GitHub 仓库设置**:
    -   进入您的仓库页面 -> 点击 **Settings** (设置)。
    -   在左侧菜单找到 **Secrets and variables** -> 点击 **Actions**。
3.  **添加 Repository secrets**:
    点击 **New repository secret** 按钮，依次添加以下两个密钥：

    | Name (名称) | Value (值) | 说明 |
    | :--- | :--- | :--- |
    | `QWEATHER_KEY` | `您的和风天气Key` | [获取地址](https://console.qweather.com/) (创建项目 -> Web API -> 复制 Key) |
    | `QMSG_KEY` | `您的Qmsg酱Key` | [获取地址](https://qmsg.zendee.cn/) (登录 -> 复制 Key) |

## 3. 验证运行
配置好 Secrets 后，我们可以手动触发一次来测试。

1.  进入仓库的 **Actions** 标签页。
2.  在左侧点击 **Daily Weather Push**。
3.  点击右侧的 **Run workflow** 按钮 -> 点击绿色 **Run workflow**。
4.  等待几秒钟，刷新页面。如果显示绿色对勾 ✅，说明运行成功。
5.  **检查您的 QQ**，应该会收到一条天气推送消息。

## 4. 常见问题
-   **报错 401/403**: 检查 Key 是否复制正确，或者和风天气是否选择了 "Web API" 类型。
-   **没收到 QQ 消息**: 检查 Qmsg 酱是否添加了您的 QQ 号，或者是否被拦截。
-   **时间不准**: GitHub Actions 使用 UTC 时间，代码中已设置为 `cron: '0 1 * * *'` (UTC 01:00)，即北京时间 09:00。
