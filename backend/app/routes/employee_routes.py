"""Store Employee and Cashier management routes for SmartFlow."""
import random
import string
from flask import Blueprint, request, jsonify
from backend.app.extensions import db
from backend.app.models.user import Employee, User
from backend.app.models.store_inventory import Store
from backend.app.auth.decorators import admin_required

employee_bp = Blueprint('employees', __name__, url_prefix='/api/employees')


@employee_bp.route('', methods=['GET'])
@admin_required()
def get_employees():
    """List all store employees, cashiers, and shift staff."""
    employees = Employee.query.order_by(Employee.id.desc()).all()
    return jsonify({
        'success': True,
        'count': len(employees),
        'employees': [e.to_dict() for e in employees]
    }), 200


@employee_bp.route('', methods=['POST'])
@admin_required()
def create_employee():
    """Create new store employee account (Admin only)."""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', 'Cashier@12345')
    full_name = data.get('full_name', '').strip()
    store_id = data.get('store_id')
    position = data.get('position', 'Cashier')
    shift = data.get('shift', 'MORNING')

    if not username or not email or not full_name or not store_id:
        return jsonify({'success': False, 'error': 'username, email, full_name, and store_id required'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'success': False, 'error': 'Username or Email is already registered'}), 409

    try:
        user = User(
            username=username,
            email=email,
            role='EMPLOYEE',
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        code = f"EMP-{random.randint(1000, 9999)}"
        while Employee.query.filter_by(employee_code=code).first():
            code = f"EMP-{random.randint(1000, 9999)}"

        emp = Employee(
            user_id=user.id,
            store_id=store_id,
            employee_code=code,
            full_name=full_name,
            position=position,
            shift=shift,
            is_active=True
        )
        db.session.add(emp)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Employee created successfully', 'employee': emp.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/<int:employee_id>', methods=['PUT'])
@admin_required()
def update_employee(employee_id):
    """Update employee store allocation, role, or shift status (Admin only)."""
    emp = Employee.query.get_or_404(employee_id)
    data = request.get_json() or {}

    if 'store_id' in data:
        emp.store_id = int(data['store_id'])
    if 'position' in data:
        emp.position = data['position'].strip()
    if 'shift' in data:
        emp.shift = data['shift'].strip()
    if 'is_active' in data:
        emp.is_active = bool(data['is_active'])
        if emp.user:
            emp.user.is_active = bool(data['is_active'])

    db.session.commit()
    return jsonify({'success': True, 'message': 'Employee record updated', 'employee': emp.to_dict()}), 200
