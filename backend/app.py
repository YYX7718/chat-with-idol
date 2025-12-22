import os
import re
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models.chat_session import SessionManager
from services.idol_chat_service import idol_chat_service
from services.divination_service import divination_service

# 创建Flask应用
# 如果存在 static 目录（Docker 部署），则使用它作为静态文件目录
static_folder = 'static' if os.path.exists('static') else None
app = Flask(__name__, static_folder=static_folder, static_url_path='')
app.logger.setLevel(logging.INFO)

# 配置 CORS（跨域资源共享）
# 开发环境：允许所有来源（仅用于本地开发）
# 生产环境：应该限制为特定域名
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins, supports_credentials=True)

# 初始化会话管理器
session_manager = SessionManager()

# API路由前缀
api_prefix = '/api'

# 偶像列表
@app.route(f'{api_prefix}/idols', methods=['GET'])
def get_idols():
    """
    获取偶像列表
    """
    idols = idol_chat_service.get_idol_list()
    return jsonify({"idols": idols})

# 偶像详情
@app.route(f'{api_prefix}/idols/<idol_id>', methods=['GET'])
def get_idol(idol_id):
    """
    获取偶像详情
    """
    idol = idol_chat_service.get_idol_info(idol_id)
    if not idol:
        return jsonify({"error": "偶像不存在", "code": 404}), 404
    return jsonify(idol)

# 创建会话
@app.route(f'{api_prefix}/sessions', methods=['POST'])
def create_session():
    """
    创建聊天会话
    """
    data = request.get_json()
    idol_id = data.get('idol_id')
    user_id = data.get('user_id')
    
    # 如果提供了idol_id，验证是否存在
    if idol_id:
        if not idol_chat_service.get_idol_info(idol_id):
            return jsonify({"error": "偶像不存在", "code": 404}), 404
    
    session = session_manager.create_session(idol_id, user_id)
    return jsonify(session.to_dict()), 201

# 获取会话
@app.route(f'{api_prefix}/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    获取聊天会话
    """
    session = session_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "会话不存在", "code": 404}), 404
    return jsonify(session.to_dict())

# 删除会话
@app.route(f'{api_prefix}/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    删除聊天会话
    """
    success = session_manager.delete_session(session_id)
    if not success:
        return jsonify({"error": "会话不存在", "code": 404}), 404
    return jsonify({"message": "会话已删除"})

# 发送消息
@app.route(f'{api_prefix}/chat/<session_id>', methods=['POST'])
def send_message(session_id):
    """
    发送聊天消息，处理不同阶段的逻辑
    """
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({"error": "消息内容不能为空", "code": 400}), 400
    
    # 获取会话
    session = session_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "会话不存在", "code": 404}), 404
    
    # 添加用户消息
    session.add_message("user", content)
    
    try:
        response_content = ""
        current_state = session.current_state
        
        if current_state == session.STATE_DIVINATION:
            app.logger.info("DIVINATION input session=%s content=%s", session_id, content)
            divination_type = idol_chat_service.detect_divination_intent(content) or "general"
            result = divination_service.generate_divination(None, divination_type, content, None)
            app.logger.info("DIVINATION output session=%s result=%s", session_id, str(result)[:800])
            session.add_divination(divination_type, content, result)
            session.set_state(session.STATE_TRANSITION)
            session.transition_step = "ASK_MORE"
            response_content = result
            
        elif current_state == session.STATE_TRANSITION:
            step = session.transition_step or "ASK_MORE"

            def is_negative(text):
                negative_keywords = ["不需要", "不用", "不要", "算了", "不想", "没事", "不了", "先不用"]
                return any(k in text for k in negative_keywords)

            def is_affirmative(text):
                affirmative_keywords = ["需要", "想", "要", "好的", "好", "可以", "嗯", "想聊", "陪伴", "请"]
                return any(k in text for k in affirmative_keywords) and not is_negative(text)

            def normalize_idol_name(text):
                t = (text or "").strip()
                t = t.strip(" \t\r\n\"'“”‘’")
                t = re.sub(r"^(我想|想|我要|要|请|帮我|给我|召唤|召请|请你召唤|请召唤)[：:\s]*", "", t)
                t = re.sub(r"^(一位|一个)?(虚拟)?(偶像)?(疗愈师)?[：:\s]*", "", t)
                return t.strip()

            def looks_like_name(text):
                t = normalize_idol_name(text)
                if not t:
                    return False
                if any(k in t for k in ["占卜", "问题", "建议", "陪伴", "聊聊", "需要", "不需要", "不用", "不要"]):
                    return False
                if re.fullmatch(r"[A-Za-z][A-Za-z .'\-]{1,39}", t):
                    return True
                if re.fullmatch(r"[\u4e00-\u9fff·\s]{2,20}", t):
                    return True
                return False

            def summon_idol(idol_name_raw):
                idol_name = normalize_idol_name(idol_name_raw)
                if not idol_name:
                    return "你想召唤谁？直接把名字发给我就好。"

                persona_config = idol_chat_service.generate_persona_profile(idol_name)
                session.persona_config = persona_config
                session.idol_id = "dynamic_idol"
                session.transition_step = None
                session.set_state(session.STATE_IDOL_CHAT)

                lang = (persona_config.get("default_language", "zh") or "zh").lower()
                need_translation = lang not in ["zh", "zh-cn", "chinese", "en", "english"]
                idol_response = idol_chat_service.generate_idol_response(persona_config, session, translate=need_translation)
                response_text = f"✨ 正在为您召唤 {idol_name} AI 疗愈师...\n提示：此“疗愈师”为虚拟 AI 人设，并非偶像真人，仅供娱乐与情绪陪伴。\n\n" + idol_response["persona_reply"]
                if idol_response.get("translation"):
                    response_text += f"\n\n[翻译]\n{idol_response['translation']}"
                return response_text

            if step == "ASK_MORE":
                if is_negative(content):
                    response_content = "明白。我会把这次占卜先放在这里。如果你之后想继续聊聊或需要一点陪伴，随时告诉我。"
                elif is_affirmative(content):
                    session.transition_step = "ASK_IDOL"
                    response_content = "好的。我可以陪你聊聊。你想选择哪位公众人物作为“虚拟偶像疗愈师”？\n\n提示：这是虚拟 AI 人设，不是真人，仅供娱乐与情绪陪伴。"
                elif looks_like_name(content):
                    try:
                        response_content = summon_idol(content)
                    except Exception as e:
                        app.logger.error(f"Error in ASK_MORE direct idol summon: {str(e)}")
                        response_content = "我明白你想直接召唤一位疗愈师。你可以再把名字发一次吗？"
                else:
                    response_content = "我在这里。如果你愿意继续，我可以陪你聊聊。\n\n你想要更多建议或陪伴吗？如果想的话，回复“需要”；如果不想，回复“不需要”。"
            elif step == "ASK_IDOL":
                try:
                    response_content = summon_idol(content)
                except Exception as e:
                    idol_name = normalize_idol_name(content)
                    app.logger.error(f"Error in ASK_IDOL phase: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    response_content = f"抱歉，我暂时没法生成“{idol_name}”的虚拟人设。请稍后再试，或者换一个名字。"
            else:
                session.transition_step = "ASK_MORE"
                response_content = "如果你愿意继续，我可以陪你聊聊。想要吗？"

        elif current_state == session.STATE_IDOL_CHAT:
            if not session.persona_config:
                session.set_state(session.STATE_TRANSITION)
                response_content = "系统错误：未找到偶像配置。请重新输入偶像名字。"
            else:
                idol_info = session.persona_config
                lang = idol_info.get("default_language", "zh").lower()
                need_translation = lang not in ["zh", "zh-cn", "chinese", "en", "english"]
                idol_response = idol_chat_service.generate_idol_response(idol_info, session, translate=need_translation)
                response_content = idol_response['persona_reply']
                if idol_response.get('translation'):
                    response_content += f"\n\n[翻译]\n{idol_response['translation']}"

        # 添加系统/偶像消息
        idol_message = session.add_message("idol", response_content)
        return jsonify({
            "session_id": session_id,
            "message": idol_message.to_dict(),
            "state": session.current_state # 返回当前状态方便前端处理
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "code": 500}), 500

# 获取消息历史
@app.route(f'{api_prefix}/chat/<session_id>/messages', methods=['GET'])
def get_messages(session_id):
    """
    获取消息历史
    """
    session = session_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "会话不存在", "code": 404}), 404
    
    # 获取分页参数
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    messages = session.messages[offset:offset+limit]
    return jsonify({
        "session_id": session_id,
        "messages": [msg.to_dict() for msg in messages]
    })

# 请求占卜
@app.route(f'{api_prefix}/divination/<session_id>', methods=['POST'])
def request_divination(session_id):
    """
    请求占卜服务
    """
    data = request.get_json()
    divination_type = data.get('type')
    question = data.get('question')
    
    if not divination_type:
        return jsonify({"error": "缺少占卜类型", "code": 400}), 400
    
    if not question:
        return jsonify({"error": "缺少占卜问题", "code": 400}), 400
    
    # 验证占卜类型
    valid_types = ['love', 'career', 'fortune', 'study']
    if divination_type not in valid_types:
        return jsonify({"error": "无效的占卜类型", "code": 400}), 400
    
    # 获取会话
    session = session_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "会话不存在", "code": 404}), 404

    # 生成占卜结果
    try:
        was_divination = session.current_state == session.STATE_DIVINATION
        app.logger.info("/divination input session=%s type=%s question=%s", session_id, divination_type, str(question)[:500])
        result = divination_service.generate_divination(
            None, divination_type, question, None
        )
        app.logger.info("/divination output session=%s result=%s", session_id, str(result)[:800])
        
        # 添加占卜记录
        divination = session.add_divination(divination_type, question, result)
        if was_divination:
            session.set_state(session.STATE_TRANSITION)
            session.transition_step = "ASK_MORE"
        
        # 同时添加到消息历史
        session.add_message("user", f"请求{divination_type}占卜：{question}")
        session.add_message("idol", result)
        
        return jsonify({
            "session_id": session_id,
            "divination": divination.to_dict(),
            "state": session.current_state,
            "transition_step": session.transition_step
        })
    except Exception as e:
        return jsonify({"error": str(e), "code": 500}), 500

# 获取占卜历史
@app.route(f'{api_prefix}/divination/<session_id>/history', methods=['GET'])
def get_divination_history(session_id):
    """
    获取占卜历史
    """
    session = session_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "会话不存在", "code": 404}), 404
    
    # 获取分页参数
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    divinations = session.divinations[offset:offset+limit]
    return jsonify({
        "session_id": session_id,
        "divinations": [div.to_dict() for div in divinations]
    })

# 提供前端静态文件（用于 Docker 部署）
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """
    提供前端静态文件
    如果存在 static 目录，则提供前端文件；否则返回 404
    """
    if static_folder and os.path.exists(static_folder):
        if path != "" and os.path.exists(os.path.join(static_folder, path)):
            return send_from_directory(static_folder, path)
        else:
            # 对于前端路由，返回 index.html
            return send_from_directory(static_folder, 'index.html')
    else:
        # 开发环境或分离部署，不提供静态文件
        return jsonify({"message": "Frontend not available. Please access frontend separately."}), 404

if __name__ == '__main__':
    # 从环境变量读取配置
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    # 生产环境应该设置 debug=False
    app.run(debug=debug_mode, port=port, host='0.0.0.0')
