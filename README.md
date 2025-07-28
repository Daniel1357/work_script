# 飞书智能回复机器人

一个基于飞书开放平台和AI大模型的智能客服回复工具，能够获取飞书群组消息并生成高情商的专业回复。

## 功能特性

- 🤖 **智能回复生成**: 使用豆包AI模型生成高情商、专业的客服回复
- 📱 **飞书集成**: 通过飞书开放平台API获取群组消息
- 🎯 **客服专用**: 专为客户服务场景优化的回复风格
- 🛡️ **错误处理**: 优雅处理各种消息格式和异常情况
- ⚡ **实时流式**: 支持流式AI回复，提升响应体验

## 技术栈

- **Python 3.11+**
- **飞书开放平台 API** (lark-oapi)
- **豆包AI模型** (通过OpenAI兼容接口)
- **JSON消息解析**

## 安装指南

### 1. 克隆项目

```bash
git clone https://github.com/Daniel1357/work_script.git
cd work_script
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境

在 `reply.py` 中配置以下参数：

```python
# 飞书应用配置
APP_ID = "your_app_id"
APP_SECRET = "your_app_secret"
GROUP_ID = "your_group_id"

# AI模型配置
AKR_API_KEY = "your_ai_api_key"
```

## 使用方法

### 运行脚本

```bash
source venv/bin/activate
python reply.py
```

### 脚本执行流程

1. **连接飞书API** - 获取访问令牌
2. **获取群组消息** - 获取最近3天的群组消息
3. **解析消息内容** - 提取文本消息并过滤
4. **生成AI回复** - 调用豆包AI生成专业回复
5. **输出结果** - 显示消息详情和AI回复

### 示例输出

```
脚本开始执行...
API请求已发送
API调用成功
获取到 19 条消息

消息ID: om_xxx
内容: {"text":"关于客户服务流程规范的重要通知..."}
发送者: ou_xxx
创建时间: 2025-07-28 10:19:02
...

----- streaming request -----
您好！关于客户服务流程规范的重要通知，主要包含以下几个方面：
1. 服务标准明确化 - 响应时效、服务用语规范
2. 流程关键变更 - 投诉审批、退换货标准  
...
```

## 配置说明

### 飞书应用配置

1. 在飞书开放平台创建应用
2. 获取 `APP_ID` 和 `APP_SECRET`
3. 配置应用权限：`im:message`
4. 获取目标群组的 `GROUP_ID`

### AI模型配置

1. 注册豆包AI服务
2. 获取API密钥
3. 配置模型端点（默认使用 `deepseek-r1-250528`）

## 项目结构

```
work_script/
├── reply.py           # 主脚本文件
├── requirements.txt   # Python依赖
├── .gitignore        # Git忽略文件
├── README.md         # 项目说明
└── venv/             # 虚拟环境（忽略）
```

## 功能详解

### 消息获取
- 获取指定群组最近3天的消息
- 支持文本消息解析
- 自动跳过非文本消息和无效格式

### AI回复生成
- 使用专业的系统提示词
- 生成高情商、有耐心的客服回复
- 支持流式输出，实时显示生成过程

### 错误处理
- JSON解析错误自动跳过
- API调用失败友好提示
- 网络异常优雅处理

## 依赖包说明

主要依赖：
- `lark-oapi`: 飞书开放平台SDK
- `openai`: AI模型调用（兼容接口）
- `requests`: HTTP请求处理

## 注意事项

1. **API密钥安全**: 请勿将API密钥提交到公共仓库
2. **权限配置**: 确保飞书应用有足够的消息读取权限
3. **网络要求**: 需要能够访问飞书API和AI模型接口
4. **消息限制**: 目前获取最近3天的消息，可根据需要调整

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License

## 更新日志

### v1.0.0 (2025-07-28)
- ✨ 初始版本发布
- 🔧 支持飞书消息获取
- 🤖 集成豆包AI模型
- 🛠️ 完善错误处理机制 