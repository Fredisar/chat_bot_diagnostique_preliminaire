from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import mongo
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Page principale du tableau de bord."""
    stats = current_user.get_stats()
    history = current_user.get_history(20)
    
    return render_template('dashboard.html', 
                         user=current_user, 
                         stats=stats,
                         history=history)

@dashboard_bp.route('/history')
@login_required
def history():
    """Page d'historique complet."""
    limit = request.args.get('limit', 100, type=int)
    history = current_user.get_history(limit)
    
    return render_template('history.html', 
                         history=history,
                         total=len(history),
                         user=current_user)

@dashboard_bp.route('/api/history')
@login_required
def api_history():
    """API pour récupérer l'historique."""
    limit = request.args.get('limit', 50, type=int)
    history = current_user.get_history(limit)
    
    for entry in history:
        if 'timestamp' in entry and entry['timestamp']:
            entry['timestamp'] = entry['timestamp'].isoformat()
    
    return jsonify({
        'success': True,
        'history': history,
        'total': len(history)
    })

@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API pour récupérer les statistiques."""
    stats = current_user.get_stats()
    
    return jsonify({
        'success': True,
        'stats': stats
    })