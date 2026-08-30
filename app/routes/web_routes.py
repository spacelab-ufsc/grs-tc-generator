import logging

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.database.factories.database_manager import DatabaseManager
from app.models.operator import Operator
from app.services.satellite_service import SatelliteService
from app.services.telecommand_service import TelecommandService

logger = logging.getLogger(__name__)
web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    """Render the dashboard with grouped telecommand status data."""
    logger.info("Loading dashboard page")
    session = DatabaseManager.get_session()
    try:
        dashboard = TelecommandService.get_dashboard_data()
        satellites = SatelliteService.list_all()
        operators = session.query(Operator).filter_by(status='active').all()

        return render_template(
            'index.html',
            pending_tcs=dashboard['pending_tcs'],
            sent_tcs=dashboard['sent_tcs'],
            history_tcs=dashboard['history_tcs'],
            satellites=satellites,
            operators=operators,
        )
    except Exception:
        logger.exception("Failed to load dashboard data")
        raise
    finally:
        session.close()

# --- Telecommand Routes ---

@web_bp.route('/telecommand/create', methods=['POST'])
def create_telecommand():
    """Handle telecommand creation form submission."""
    logger.info("Creating telecommand via web form")
    try:
        payload = request.form.to_dict()
        TelecommandService.create(payload)
        flash('Telecommand created successfully!', 'success')
    except ValueError as exc:
        logger.warning("Invalid telecommand creation payload: %s", exc)
        flash(str(exc), 'warning')
    except Exception:
        logger.exception("Unexpected failure while creating telecommand")
        flash('Error creating telecommand.', 'danger')
    return redirect(url_for('web.index'))

@web_bp.route('/telecommand/update/<int:tc_id>', methods=['POST'])
def update_telecommand(tc_id):
    """Handle telecommand updates via AJAX."""
    logger.info("Updating telecommand %s", tc_id)
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        TelecommandService.update(tc_id, data)
        return jsonify({'success': True, 'message': 'Telecommand updated successfully'})
    except LookupError as exc:
        logger.warning("Telecommand update failed: %s", exc)
        return jsonify({'success': False, 'error': str(exc)}), 404
    except ValueError as exc:
        logger.warning("Telecommand update validation failed: %s", exc)
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception:
        logger.exception("Unexpected failure while updating telecommand %s", tc_id)
        return jsonify({'success': False, 'error': 'Unexpected error while updating telecommand'}), 500

@web_bp.route('/telecommand/delete/<int:tc_id>', methods=['POST'])
def delete_telecommand(tc_id):
    """Handle telecommand deletion."""
    logger.info("Deleting telecommand %s", tc_id)
    try:
        TelecommandService.delete(tc_id)
        flash(f'Telecommand {tc_id} deleted.', 'success')
    except LookupError as exc:
        logger.warning("Delete failed: %s", exc)
        flash(str(exc), 'warning')
    except Exception:
        logger.exception("Unexpected failure while deleting telecommand %s", tc_id)
        flash('Error deleting telecommand.', 'danger')
    return redirect(url_for('web.index'))

# --- Satellite Routes ---

@web_bp.route('/satellite/create', methods=['POST'])
def create_satellite():
    """Handle satellite creation via AJAX."""
    logger.info("Creating satellite via API")
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        SatelliteService.create(data)
        return jsonify({'success': True, 'message': 'Satellite created successfully'})
    except ValueError as exc:
        logger.warning("Satellite creation failed: %s", exc)
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception:
        logger.exception("Unexpected failure while creating satellite")
        return jsonify({'success': False, 'error': 'Unexpected error while creating satellite'}), 500

@web_bp.route('/satellite/update/<int:sat_id>', methods=['POST'])
def update_satellite(sat_id):
    """Handle satellite updates via AJAX."""
    logger.info("Updating satellite %s", sat_id)
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        SatelliteService.update(sat_id, data)
        return jsonify({'success': True, 'message': 'Satellite updated successfully'})
    except LookupError as exc:
        logger.warning("Satellite update failed: %s", exc)
        return jsonify({'success': False, 'error': str(exc)}), 404
    except ValueError as exc:
        logger.warning("Satellite update validation failed: %s", exc)
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception:
        logger.exception("Unexpected failure while updating satellite %s", sat_id)
        return jsonify({'success': False, 'error': 'Unexpected error while updating satellite'}), 500

@web_bp.route('/satellite/delete/<int:sat_id>', methods=['POST'])
def delete_satellite(sat_id):
    """Handle satellite deletion."""
    logger.info("Deleting satellite %s", sat_id)
    try:
        SatelliteService.delete(sat_id)
        flash(f'Satellite {sat_id} deleted.', 'success')
    except LookupError as exc:
        logger.warning("Satellite delete failed: %s", exc)
        flash(str(exc), 'warning')
    except Exception:
        logger.exception("Unexpected failure while deleting satellite %s", sat_id)
        flash('Error deleting satellite.', 'danger')
    return redirect(url_for('web.index'))

@web_bp.route('/spectrum-monitor')
def spectrum_monitor():
    """Render the RF signal monitoring page."""
    logger.info("Loading spectrum monitor page")
    return render_template('spectrum-monitor.html')

