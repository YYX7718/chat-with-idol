from flask import Flask, request, jsonify
from models.chat_session import SessionManager
from services.idol_chat_service import idol_chat_service
from services.divination_service import divination_service

# 创建Flask应用
app = Flask(__name__)

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
    
    if not idol_id:
        return jsonify({"error": "缺少偶像ID", "code": 400}), 400
    
    # 验证偶像是否存在
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
    发送聊天消息
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
    
    # 获取偶像信息
    idol_info = idol_chat_service.get_idol_info(session.idol_id)
    
    # 生成偶像回复
    try:
        idol_response = idol_chat_service.generate_idol_response(idol_info, session)
        # 添加偶像消息
        idol_message = session.add_message("idol", idol_response)
        return jsonify({
            "session_id": session_id,
            "message": idol_message.to_dict()
        })
    except Exception as e:
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)