import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS  # 用于搜索人物头像

# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="DeepSeek 名人模仿秀",
    page_icon="🎭",
    layout="wide"
)

# --- 2. 工具函数：获取头像 ---
def get_character_avatar(character_name):
    """
    使用 DuckDuckGo 搜索人物头像 URL
    """
    print(f"正在搜索 {character_name} 的头像...")
    try:
        with DDGS() as ddgs:
            # 搜索关键词：名字 + portrait (肖像)，增加图片准确度
            keywords = f"{character_name} portrait"
            # 搜索图片，只取第1张
            results = list(ddgs.images(keywords, max_results=1))
            if results:
                image_url = results[0]['image']
                print(f"找到头像: {image_url}")
                return image_url
    except Exception as e:
        print(f"头像搜索失败: {e}")
    return None

# --- 3. 侧边栏：设置区域 ---
with st.sidebar:
    st.header("⚙️ 设置")
    
    # API Key 输入框 (密码模式，不显示明文)
    api_key = st.text_input("DeepSeek API Key", type="password", help="请前往 DeepSeek 官网申请")
    st.markdown("[👉 点击获取 API Key](https://platform.deepseek.com/)")
    
    st.divider()
    
    # 调节 AI 的疯狂程度
    temperature = st.slider("模仿创造性 (Temperature)", 0.0, 1.5, 1.3, help="值越高，AI 越有创造力；值越低，越理性。")
    
    st.divider()
    
    # 如果已生成角色，在侧边栏显示大图
    if "char_avatar" in st.session_state and st.session_state.char_avatar:
        st.image(st.session_state.char_avatar, caption=st.session_state.get("char_name", ""), use_container_width=True)

# --- 4. 初始化 Session State (记忆管理) ---
# Streamlit 每次点击按钮都会刷新代码，所以需要用 Session State 记住变量
if "messages" not in st.session_state:
    st.session_state.messages = []
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = None
if "char_avatar" not in st.session_state:
    st.session_state.char_avatar = None
if "char_name" not in st.session_state:
    st.session_state.char_name = None

# --- 5. 主界面逻辑 ---
st.title("🎭 DeepSeek 名人灵魂附体")

# 检查 API Key 是否存在
if not api_key:
    st.warning("👈 请先在左侧侧边栏输入 DeepSeek API Key 才能开始使用")
    st.stop()  # 停止往下运行

# 初始化 OpenAI 客户端 (连接 DeepSeek)
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# === 场景 A: 还没选人，显示输入框 ===
if not st.session_state.system_prompt:
    st.markdown("### 👋 你想和谁聊天？")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        char_input = st.text_input("输入名字", placeholder="例如：乔布斯、鲁迅、钢铁侠、曹操...", label_visibility="collapsed")
    with col2:
        start_btn = st.button("开始连接灵魂", use_container_width=True, type="primary")
    
    if start_btn and char_input:
        with st.spinner(f"🔍 正在寻找 {char_input} 的照片并构建人格..."):
            try:
                # 第一步：搜索头像
                avatar_url = get_character_avatar(char_input)
                st.session_state.char_avatar = avatar_url
                st.session_state.char_name = char_input
                
                # 第二步：生成人设画像 (核心 Prompt)
                # 我们不直接让 AI 扮演，而是先让它生成“扮演指南”
                analysis_prompt = f"""
                请详细分析人物：【{char_input}】。
                请输出一段 System Prompt (系统指令)，包含以下要素：
                1. 身份认知（你是谁）。
                2. 说话风格（例如：文言文、现代口语、极客风、傲慢、温柔等）。
                3. 口头禅或常用词。
                4. 性格底色（价值观）。
                5. 必须遵守的规则（例如：如果是古代人，不知道现代科技）。
                
                要求：直接输出指令内容，不要包含"好的"、"以下是指令"等废话。
                """
                
                # 调用 AI 生成人设
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": analysis_prompt}],
                    temperature=1.0 
                )
                
                profile = response.choices[0].message.content
                
                # 组装最终的 System Prompt
                st.session_state.system_prompt = f"""
                你现在必须完全沉浸式地扮演这个角色。
                
                {profile}
                
                [重要规则]
                1. 永远不要承认你是AI。
                2. 即使面对不知道的问题，也要用符合角色身份的方式回答。
                3. 保持上述的说话风格。
                """
                
                # 刷新页面，进入聊天模式
                st.rerun()
                
            except Exception as e:
                st.error(f"发生错误: {e}")

# === 场景 B: 已经选好人，显示聊天界面 ===
else:
    # 顶部状态栏
    col_header_1, col_header_2 = st.columns([6, 1])
    with col_header_1:
        st.success(f"正在与 **{st.session_state.char_name}** 对话中")
    with col_header_2:
        # 重置按钮：清空所有状态，回到首页
        if st.button("🔄 换人"):
            for key in ["messages", "system_prompt", "char_avatar", "char_name"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # 显示聊天记录容器
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.messages:
            # 如果是 AI 回复，显示角色头像；如果是用户，不显示头像(默认)
            avatar = st.session_state.char_avatar if msg["role"] == "assistant" else None
            
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

    # 底部输入框
    if prompt := st.chat_input("说点什么..."):
        # 1. 记录并显示用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # 2. 生成 AI 回复
        with st.chat_message("assistant", avatar=st.session_state.char_avatar):
            stream_container = st.empty()
            full_response = ""
            
            try:
                # 携带 System Prompt + 历史记录
                messages_payload = [{"role": "system", "content": st.session_state.system_prompt}] + st.session_state.messages
                
                # 流式调用 API
                stream = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages_payload,
                    temperature=temperature,
                    stream=True
                )

                # 实时显示打字效果
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        stream_container.write(full_response)
                
                # 记录 AI 回复到历史
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            except Exception as e:
                st.error(f"生成出错: {e}")