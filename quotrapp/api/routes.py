from flask import Blueprint, jsonify
from sqlalchemy import func
from quotrapp.models import Quote


api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/api/quote')
def index():
    quote = Quote.query.order_by(func.random()).first()
    return jsonify({'Quote': quote.content, 'Author': quote.author.name})
