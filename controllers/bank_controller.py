from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User
from utils.auth import login_required
from utils.db import get_collection

bank_bp = Blueprint('bank', __name__)

@bank_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@bank_bp.route('/dashboard')
@login_required()  # accessible for any logged-in user
def dashboard(payload):
    user = User.find_by_username(payload['username'])
    if user.role == 'banker':
        return render_template('dashboard_banker.html', user=user)
    else:
        return render_template('dashboard_customer.html', user=user)


@bank_bp.route('/deposit', methods=['POST'])
@login_required()
def deposit(payload):
    user = User.find_by_username(payload['username'])
    try:
        amount = float(request.form.get('amount'))
        if amount <= 0:
            raise Exception("Invalid amount")
        user.balance += amount
        user.save_balance()
        get_collection('transactions').insert_one({
            'username': user.username,
            'type': 'deposit',
            'amount': amount
        })
        flash("Deposit successful.", "success")
    except Exception as e:
        flash("Deposit failed: " + str(e), "danger")
    return redirect(url_for('bank.dashboard'))

@bank_bp.route('/withdraw', methods=['POST'])
@login_required()
def withdraw(payload):
    user = User.find_by_username(payload['username'])
    try:
        amount = float(request.form.get('amount'))
        if amount <= 0:
            raise Exception("Invalid withdrawal amount")
        if amount > user.balance:
            # Render the dashboard with an error message
            return render_template(
                'dashboard_customer.html',
                user=user,
                withdraw_error='Insufficient balance!'
            )
        user.balance -= amount
        user.save_balance()
        get_collection('transactions').insert_one({
            'username': user.username,
            'type': 'withdraw',
            'amount': amount
        })
        flash("Withdrawal successful.", "success")
    except Exception as e:
        flash("Withdrawal failed: " + str(e), "danger")
    return redirect(url_for('bank.dashboard'))


@bank_bp.route('/transactions')
@login_required()
def transactions(payload):
    txns = list(get_collection('transactions').find({'username': payload['username']}))
    return render_template('transactions.html', txns=txns)

# Banker-only routes

@bank_bp.route('/accounts')
@login_required(role='banker')  # restrict to banker role only
def account_list(payload):
    users = User.all_customers()
    return render_template('accounts.html', users=users)

@bank_bp.route('/all-transactions')
@login_required(role='banker')  # restrict to banker role only
def all_transactions(payload):
    txns = list(get_collection('transactions').find())
    return render_template('transactions.html', txns=txns, all=True)

@bank_bp.route('/check-balance')
@login_required(role='customer')
def check_balance(payload):
    user = User.find_by_username(payload['username'])
    return render_template('check_balance.html', user=user)

