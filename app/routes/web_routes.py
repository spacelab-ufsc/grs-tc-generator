from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from sqlalchemy import desc
import json
from app.database.factories.database_manager import DatabaseManager
from app.models.telecommand import Telecommand
from app.models.satellite import Satellite
from app.models.operator import Operator

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Render the main dashboard with telecommands grouped by status."""
    session = DatabaseManager.get_session()
    try:
        # Fetch recent telecommands grouped by status
        # We limit to 10 per category for performance/cleanliness
        pending_tcs = session.query(Telecommand)\
            .filter(Telecommand.status.in_(['pending', 'queued']))\
            .order_by(desc(Telecommand.created_at))\
            .limit(10).all()

        sent_tcs = session.query(Telecommand)\
            .filter(Telecommand.status == 'sent')\
            .order_by(desc(Telecommand.sent_at))\
            .limit(10).all()

        # History: Confirmed or Failed
        history_tcs = session.query(Telecommand)\
            .filter(Telecommand.status.in_(['confirmed', 'failed']))\
            .order_by(desc(Telecommand.created_at))\
            .limit(10).all()
            
        # Fetch satellites for the create modal dropdown
        satellites = session.query(Satellite).filter_by(status='active').all()
        
        # Fetch operators (In a real app, this would be the logged-in user)
        operators = session.query(Operator).filter_by(status='active').all()

        return render_template(
            'index.html',
            pending_tcs=pending_tcs,
            sent_tcs=sent_tcs,
            history_tcs=history_tcs,
            satellites=satellites,
            operators=operators
        )
    finally:
        session.close()

@web_bp.route('/telecommand/create', methods=['POST'])
def create_telecommand():
    """Handle telecommand creation form submission."""
    session = DatabaseManager.get_session()
    try:
        data = request.form
        
        # Parse parameters JSON if provided
        params = {}
        if data.get('parameters'):
            try:
                params = json.loads(data['parameters'])
            except json.JSONDecodeError:
                flash('Invalid JSON in parameters field', 'warning')
                return redirect(url_for('web.index'))

        new_tc = Telecommand(
            satellite_id=int(data['satellite_id']),
            operator_id=int(data['operator_id']),
            command_type=data['command_type'],
            priority=int(data['priority']),
            status='pending',
            parameters=params
        )
        
        session.add(new_tc)
        session.commit()
        flash('Telecommand created successfully!', 'success')
        
    except Exception as e:
        session.rollback()
        flash(f'Error creating telecommand: {str(e)}', 'danger')
    finally:
        session.close()
        
    return redirect(url_for('web.index'))

@web_bp.route('/telecommand/update/<int:tc_id>', methods=['POST'])
def update_telecommand(tc_id):
    """Handle telecommand updates via AJAX."""
    session = DatabaseManager.get_session()
    try:
        tc = session.get(Telecommand, tc_id)
        if not tc:
            return jsonify({'success': False, 'error': 'Telecommand not found'}), 404
            
        # Get JSON data from request body
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Update fields if provided
        if 'parameters' in data:
            tc.parameters = data['parameters']
        
        if 'satellite_id' in data:
            tc.satellite_id = int(data['satellite_id'])
            
        if 'command_type' in data:
            tc.command_type = data['command_type']
            
        if 'priority' in data:
            tc.priority = int(data['priority'])
            
        if 'status' in data:
            # Use update_status method if available to handle timestamps, 
            # otherwise set directly
            if hasattr(tc, 'update_status'):
                tc.update_status(data['status'])
            else:
                tc.status = data['status']
            
        session.commit()
        return jsonify({'success': True, 'message': 'Telecommand updated successfully'})
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@web_bp.route('/telecommand/delete/<int:tc_id>', methods=['POST'])
def delete_telecommand(tc_id):
    """Handle telecommand deletion."""
    session = DatabaseManager.get_session()
    try:
        tc = session.get(Telecommand, tc_id)
        if tc:
            session.delete(tc)
            session.commit()
            flash(f'Telecommand {tc_id} deleted.', 'success')
        else:
            flash('Telecommand not found.', 'warning')
    except Exception as e:
        session.rollback()
        flash(f'Error deleting: {str(e)}', 'danger')
    finally:
        session.close()
        
    return redirect(url_for('web.index'))
