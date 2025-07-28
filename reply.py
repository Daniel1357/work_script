from datetime import datetime
import json
import os

import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from openai import OpenAI

NOW = int(datetime.now().timestamp())
THREE_DAYS_AGO = NOW - 3 * 24 * 60 * 60

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

    # 构造请求对象
    request: ListMessageRequest = ListMessageRequest.builder() \
        .container_id_type("chat") \
        .container_id(group_id) \
        .start_time(str(THREE_DAYS_AGO)) \
        .end_time(str(NOW)) \
        .sort_type("ByCreateTimeAsc") \
        .build()
        # .page_size(20) \
        # .build()
        # .page_token("GxmvlNRvP0NdQZpa7yIqf_Lv_QuBwTQ8tXkX7w-irAghVD_TvuYd1aoJ1LQph86O-XImC4X9j9FhUPhXQDvtrQ==") \
        # .build()

    # 发起请求
    response: ListMessageResponse = client.im.v1.message.list(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    messages = []
    for message in response.data.items:
        try:
            content = json.loads(message.body.content)
            if "text" not in content:
                continue

            print(message.message_id)
            print(message.body.content)
            print(message.sender.id)
            print(datetime.fromtimestamp(int(message.create_time) / 1000))
            print(datetime.fromtimestamp(int(message.update_time) / 1000))
            if message.mentions:
                mentions = [m.name for m in message.mentions]
                print(mentions)
            print("\n")
            messages.append(message.body.content)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"跳过消息 {message.message_id}，解析错误: {e}")
            continue

    return messages


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
    print("----- streaming request -----")
    stream = client.chat.completions.create(
        model = "deepseek-r1-250528",  # your model endpoint ID
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(messages=messages)},
            {"role": "user", "content": message},
        ],
        stream=True
    )

    for chunk in stream:
        if not chunk.choices:
            continue
        print(chunk.choices[0].delta.content, end="")
    print()

if __name__ == "__main__":
    messages = get_messages(GROUP_ID)
    print(get_reply("客户服务流程规范的重要通知包括了啥？", messages))