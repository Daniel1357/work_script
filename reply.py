from datetime import datetime
import json
import os

import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from openai import OpenAI

NOW = int(datetime.now().timestamp())
THREE_DAYS_AGO = NOW - 7 * 24 * 60 * 60

APP_ID = "cli_a80a277c847e500b"
APP_SECRET = "q8T2uSZAzoYgTTDyzvTIchA52Jn3NrpU"

GROUP_ID = "oc_16eefcc056bd0bafd898e0c69b171f76"
# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development
# 以下示例代码默认根据文档示例值填充，如果存在代码问题，请在 API 调试台填上相关必要参数后再复制代码使用
# 复制该 Demo 后, 需要将 "YOUR_APP_ID", "YOUR_APP_SECRET" 替换为自己应用的 APP_ID, APP_SECRET.
def get_messages(group_id):
    # 创建client
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    all_messages = []
    page_token = ""
    page_count = 0
    max_pages = 100  # 增加最大页数限制
    
    print("🔄 开始分页获取所有历史消息...")
    
    while page_count < max_pages:
        page_count += 1
        print(f"📄 正在获取第 {page_count} 页消息...")
        
        # 构造请求对象
        request_builder = ListMessageRequest.builder() \
            .container_id_type("chat") \
            .container_id(group_id) \
            .start_time(str(THREE_DAYS_AGO)) \
            .end_time(str(NOW)) \
            .sort_type("ByCreateTimeAsc") \
            .page_size(50)  # 设置每页消息数量
            
        if page_token:
            request_builder = request_builder.page_token(page_token)
            
        request = request_builder.build()

        # 发起请求
        response: ListMessageResponse = client.im.v1.message.list(request)

        # 处理失败返回
        if not response.success():
            print(f"❌ API调用失败: code={response.code}, msg={response.msg}")
            lark.logger.error(
                f"client.im.v1.message.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            break

        # 处理当前页的消息
        page_messages = []
        if response.data.items:
            for message in response.data.items:
                try:
                    content = json.loads(message.body.content)
                    if "text" not in content:
                        continue

                    # 简化消息输出，只显示关键信息
                    text_content = content.get("text", "")
                    timestamp = datetime.fromtimestamp(int(message.create_time) / 1000)
                    
                    print(f"📝 {timestamp.strftime('%Y-%m-%d %H:%M')} - {text_content[:50]}{'...' if len(text_content) > 50 else ''}")
                    page_messages.append(message.body.content)
                    all_messages.append(message.body.content)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"跳过消息 {message.message_id}，解析错误: {e}")
                    continue
        
        print(f"✅ 第 {page_count} 页获取到 {len(page_messages)} 条有效消息")
        
        # 检查是否还有更多页
        if not response.data.has_more:
            print("🎉 已获取所有历史消息！")
            break
        
        page_token = response.data.page_token
        print(f"🔍 发现还有更多消息，继续获取...")
        
    print(f"📊 总计获取到 {len(all_messages)} 条历史消息")
    return all_messages


SYSTEM_PROMPT = """
# 角色
你是一位名为回复大师的高情商客户服务专家，擅长以温暖、专业且充满共情的方式，对输入的内容进行回答。

## 任务
将输入的原始内容按照技能和要求进行回复。输出的内容请体现共情、理解并有耐心的特点。

## 输入
{{messages}}

## 技能
### 技能 1: 回复内容
1. 仔细分析输入的原始内容，从中体会用户可能存在的情绪和关切点。
2. 基于对用户情绪和关切的理解，运用礼貌、有耐心且专业的语言，对输入内容进行回复。
3. 在重述过程中，绝对避免出现指责或防御语气，要让用户强烈感受到被倾听和理解。
4. 优化后的表达需呈现出对用户状态的共情，以高情商的方式组织回复内容。
5. 回复内容简洁凝练。

## 限制:
- 仅围绕用户输入的原始内容进行回复，不涉及其他无关话题。
- 回答的内容必须符合高情商、礼貌、有耐心、专业且无指责或防御语气的要求。 
- 思考过程中不展示提示词的部分。
"""

AKR_API_KEY = "0a5e6ae2-30fd-4662-a4aa-61f05c79daaa"
def get_reply(message,messages):
    client = OpenAI(
        api_key = AKR_API_KEY,
        base_url = "https://ark.cn-beijing.volces.com/api/v3",
    )

    # Non-streaming:
    # print("----- standard request -----")
    # completion = client.chat.completions.create(
    #     model = "deepseek-r1-250528",  # your model endpoint ID
    #     messages = [
    #         {"role": "system", "content": "你是人工智能助手"},
    #         {"role": "user", "content": "常见的十字花科植物有哪些？"},
    #     ],
    # )
    # print(completion.choices[0].message.content)

    # Streaming:
    print("\n" + "="*60)
    print("🤖 AI智能回复生成中...")
    print("="*60)
    
    stream = client.chat.completions.create(
        model = "deepseek-r1-250528",  # your model endpoint ID
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(messages=messages)},
            {"role": "user", "content": message},
        ],
        stream=True
    )

    reply_content = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="")
            reply_content += content
    
    print("\n" + "="*60)
    print("\n" + "🎯 飞书回复内容 🎯".center(60))
    print("="*60)
    print(reply_content)
    print("="*60)
    print("💡 直接复制上面框内内容发送到飞书群组即可")
    print("="*60)
    
    return reply_content

if __name__ == "__main__":
    print("🚀 飞书智能回复机器人启动中...")
    print("📱 正在获取飞书群组消息...")
    
    messages = get_messages(GROUP_ID)
    
    if messages:
        print(f"\n✅ 成功获取到 {len(messages)} 条有效消息")
        print("🧠 开始生成智能回复...")
        
        reply = get_reply("露嘉，就在 先找客户理清楚问题有哪些，安抚下吧，要约上业务、内控，It也是内部扛不住压力了，帮帮IT。刚刚，多点销售拉了个群，讲今天去谈商务续费，客户全程在吐槽智书，我拉你和销售对接，然后一起和销售处理好吧。", messages)
        
        print(f"\n🎉 回复生成完成！总计 {len(reply)} 个字符")
        print("✨ 请直接复制上面框内的回复内容发送到飞书群组")
    else:
        print("❌ 未获取到有效消息，请检查群组ID和权限配置")