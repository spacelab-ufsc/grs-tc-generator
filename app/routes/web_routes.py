from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import desc
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
        # Since Telecommand doesn't have updated_at, we use confirmed_at for confirmed ones
        # and created_at for failed ones (or just created_at for generic sorting)
        # Using created_at is safer as it's always present.
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
        
        new_tc = Telecommand(
            satellite_id=int(data['satellite_id']),
            operator_id=int(data['operator_id']), # In real app: current_user.id
            command_type=data['command_type'],
            priority=int(data['priority']),
            status='pending',
            parameters={} # Simplified for now, could parse JSON from form
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
