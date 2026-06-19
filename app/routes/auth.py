# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Traitement du formulaire de connexion
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Identifiants incorrects', 'error')
    
    return render_template('login.html')  

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Traitement du formulaire d'inscription
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Créer l'utilisateur
        user = User.create_user(username, email, password)
        login_user(user)
        flash('Inscription réussie !', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('register.html') 



@auth_bp.route('/profile')
@login_required
def profile():
    """
    Page de profil utilisateur.
    """
    stats = current_user.get_stats()
    return render_template('profile.html', 
                         user=current_user, 
                         stats=stats)

# app/routes/auth.py
@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    username = current_user.username
    logout_user()
    flash(f'À bientôt {username} !', 'info')
    return redirect(url_for('main.index'))