"""Business logic for satellite-related operations."""

import logging
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError

from app.database.factories.database_manager import DatabaseManager
from app.models.satellite import Satellite

logger = logging.getLogger(__name__)


class SatelliteService:
    """Encapsulate satellite CRUD and validation rules."""

    @staticmethod
    def list_all() -> list[Satellite]:
        """Return all satellites ordered by name."""
        session = DatabaseManager.get_session()
        try:
            return session.query(Satellite).order_by(Satellite.name).all()
        finally:
            session.close()

    @staticmethod
    def create(data: Dict[str, Any]) -> Satellite:
        """Create a new satellite and persist it."""
        session = DatabaseManager.get_session()
        try:
            satellite = Satellite(
                name=data["name"],
                code=data["code"],
                status=data.get("status", "active"),
                description=data.get("description", ""),
            )
            session.add(satellite)
            session.commit()
            logger.info("Satellite created: %s (%s)", satellite.name, satellite.code)
            return satellite
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Failed to create satellite: duplicate or invalid data")
            raise ValueError("Satellite code must be unique.") from exc
        except Exception:
            session.rollback()
            logger.exception("Unexpected error while creating satellite")
            raise
        finally:
            session.close()

    @staticmethod
    def update(satellite_id: int, data: Dict[str, Any]) -> Satellite:
        """Update an existing satellite using the provided payload."""
        session = DatabaseManager.get_session()
        try:
            satellite = session.get(Satellite, satellite_id)
            if not satellite:
                raise LookupError("Satellite not found.")

            for field in ("name", "code", "status", "description"):
                if field in data:
                    setattr(satellite, field, data[field])

            session.commit()
            logger.info("Satellite updated: %s (%s)", satellite.name, satellite.code)
            return satellite
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Failed to update satellite: unique constraint violation")
            raise ValueError("Satellite code must be unique.") from exc
        except Exception:
            session.rollback()
            logger.exception("Unexpected error while updating satellite")
            raise
        finally:
            session.close()

    @staticmethod
    def delete(satellite_id: int) -> None:
        """Delete a satellite by id."""
        session = DatabaseManager.get_session()
        try:
            satellite = session.get(Satellite, satellite_id)
            if not satellite:
                raise LookupError("Satellite not found.")

            session.delete(satellite)
            session.commit()
            logger.info("Satellite deleted: %s (%s)", satellite.name, satellite.code)
        except Exception:
            session.rollback()
            logger.exception("Unexpected error while deleting satellite")
            raise
        finally:
            session.close()
