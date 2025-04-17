from datetime import datetime, timedelta
from flask import jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

# Utility functions for the application

def validate_date(date_str, date_format='%Y-%m-%d'):
    """Validate date string format"""
    try:
        return datetime.strptime(date_str, date_format).date()
    except ValueError:
        return None

def calculate_time_period(period):
    """
    Calculate start and end date based on period string
    Supported periods: 'today', 'week', 'month', 'year'
    """
    today = datetime.utcnow().date()
    
    if period == 'today':
        return today, today
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())
        return start_date, today
    elif period == 'month':
        start_date = today.replace(day=1)
        return start_date, today
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
        return start_date, today
    else:
        return None, None

def format_currency(value):
    """Format number as currency string"""
    return "{:,.0f} VND".format(value) if value else "0 VND"

def admin_required(fn):
    """
    Decorator to require admin role for endpoint
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        if current_user_id != 1:
            return jsonify({"error": "Cần có quyền truy cập của quản trị viên"}), 403
        return fn(*args, **kwargs)
    return wrapper

def handle_db_errors(fn):
    """
    Decorator to handle common database errors
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "error": "Thao tác cơ sở dữ liệu không thành công",
                "message": str(e)
            }), 500
    return wrapper

def generate_monthly_labels(start_date, end_date):
    """
    Generate monthly labels between two dates
    """
    labels = []
    current = start_date.replace(day=1)
    
    while current <= end_date:
        labels.append(current.strftime('%Y-%m'))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    return labels

def build_response(data=None, message="Success", status=200, error=None):
    """
    Standardize API response format
    """
    response = {
        "status": status,
        "message": message,
        "data": data
    }
    if error:
        response["error"] = error
    return jsonify(response), status

def parse_request_data(schema):
    """
    Decorator to parse and validate request data with marshmallow schema
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            errors = schema.validate(data)
            if errors:
                return build_response(
                    message="Xác thực không thành công",
                    status=400,
                    error=errors
                )
            return fn(data, *args, **kwargs)
        return wrapper
    return decorator