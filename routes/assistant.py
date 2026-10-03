from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, ChatHistory
from services.chatbot_service import generate_chat_response

assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.route("/assistant", methods=["GET"])
@login_required
def assistant():
    # Load past chat history
    history = (
        ChatHistory.query.filter_by(user_id=current_user.id)
        .order_by(ChatHistory.created_at.asc())
        .limit(30)
        .all()
    )
    return render_template("assistant/chatbot.html", history=history)


@assistant_bp.route("/assistant/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    bot_reply = generate_chat_response(user_message, user_id=current_user.id)

    # Save to chat history
    record = ChatHistory(
        user_id=current_user.id,
        user_message=user_message,
        assistant_response=bot_reply
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "status": "success",
        "reply": bot_reply,
        "message_id": record.id
    })
