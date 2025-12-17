import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models.chat_session import SessionManager
from services.idol_chat_service import idol_chat_service
from services.divination_service import divination_service

# 创建Flask应用
# 如果存在 static 目录（Docker 部署），则使用它作为静态文件目录
static_folder = 'static' if os.path.exists('static') else None
app = Flask(__name__, static_folder=static_folder, static_url_path='')

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
            # 阶段一：占卜
            divination_type = idol_chat_service.detect_divination_intent(content)
            result = divination_service.generate_divination(None, divination_type, content, None)
            
            # 添加占卜记录（会自动切换状态到 TRANSITION）
            session.add_divination(divination_type, content, result)
            response_content = result
            
        elif current_state == session.STATE_TRANSITION:
            # 阶段二：过渡
            # 假设用户输入的就是偶像名字
            idol_name = content.strip()
            
            # 生成动态 Persona
            # 提示用户正在连接...（前端可能需要处理，这里后端直接生成并返回第一句）
            # 注意：生成 Persona 可能需要几秒钟
            
            try:
                # 1. 生成 Persona 配置
                persona_config = idol_chat_service.generate_persona_profile(idol_name)
                
                # 2. 存入 Session
                session.persona_config = persona_config
                session.idol_id = "dynamic_idol" # 标记为动态偶像
                
                # 3. 切换状态
                session.set_state(session.STATE_IDOL_CHAT)
                
                # 4. 生成开场白
                idol_response = idol_chat_service.generate_idol_response(persona_config, session)
                response_content = idol_response['persona_reply']
                if idol_response.get('translation'):
                    response_content += f"\n\n[翻译]\n{idol_response['translation']}"
                    
            except Exception as e:
                response_content = f"抱歉，我无法连接到{idol_name}。请尝试其他名字。"
                print(f"Error generating persona: {e}")

        elif current_state == session.STATE_IDOL_CHAT:
            # 阶段三：偶像聊天
            if not session.persona_config:
                # 异常情况，回退到过渡
                session.set_state(session.STATE_TRANSITION)
                response_content = "系统错误：未找到偶像配置。请重新输入偶像名字。"
            else:
                idol_info = session.persona_config
                idol_response = idol_chat_service.generate_idol_response(idol_info, session)
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
    
    # 获取偶像信息
    idol_info = idol_chat_service.get_idol_info(session.idol_id)
    
    # 生成占卜结果
    try:
        result = divination_service.generate_divination(
            idol_info, divination_type, question
        )
        
        # 添加占卜记录
        divination = session.add_divination(divination_type, question, result)
        
        # 同时添加到消息历史
        session.add_message("user", f"请求{divination_type}占卜：{question}")
        session.add_message("idol", result)
        
        return jsonify({
            "session_id": session_id,
            "divination": divination.to_dict()
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