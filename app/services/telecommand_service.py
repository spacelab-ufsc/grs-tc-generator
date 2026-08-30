"""Business logic for telecommand operations."""

import json
import logging
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.database.factories.database_manager import DatabaseManager
from app.models.telecommand import Telecommand

logger = logging.getLogger(__name__)


class TelecommandService:
    """Encapsulate telecommand validation, creation, updates, and retrieval."""

    @staticmethod
    def get_dashboard_data() -> Dict[str, list[Telecommand]]:
        """Return the dashboard telecommand groups used by the main page."""
        session = DatabaseManager.get_session()
        try:
            pending_tcs = (
                session.query(Telecommand)
                .options(selectinload(Telecommand.satellite), selectinload(Telecommand.operator))
                .filter(Telecommand.status.in_(["pending", "queued"]))
                .order_by(Telecommand.created_at.desc())
                .limit(10)
                .all()
            )
            sent_tcs = (
                session.query(Telecommand)
                .options(selectinload(Telecommand.satellite), selectinload(Telecommand.operator))
                .filter(Telecommand.status == "sent")
                .order_by(Telecommand.sent_at.desc())
                .limit(10)
                .all()
            )
            history_tcs = (
                session.query(Telecommand)
                .options(selectinload(Telecommand.satellite), selectinload(Telecommand.operator))
                .filter(Telecommand.status.in_(["confirmed", "failed"]))
                .order_by(Telecommand.created_at.desc())
                .limit(10)
                .all()
            )
            return {
                "pending_tcs": pending_tcs,
                "sent_tcs": sent_tcs,
                "history_tcs": history_tcs,
            }
        finally:
            session.close()

    @staticmethod
    def create(data: Dict[str, Any]) -> Telecommand:
        """Create a telecommand from a validated payload."""
        session = DatabaseManager.get_session()
        try:
            parameters = data.get("parameters") or {}
            if isinstance(parameters, str):
                parameters = json.loads(parameters)

            telecommand = Telecommand(
                satellite_id=int(data["satellite_id"]),
                operator_id=int(data["operator_id"]),
                command_type=data["command_type"],
                priority=int(data.get("priority", 5)),
                status="pending",
                parameters=parameters,
            )

            session.add(telecommand)
            session.commit()
            logger.info("Telecommand created: %s for satellite %s", telecommand.command_type, telecommand.satellite_id)
            return telecommand
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            session.rollback()
            logger.exception("Invalid telecommand payload")
            raise ValueError("Invalid telecommand payload.") from exc
        except Exception:
            session.rollback()
            logger.exception("Unexpected error while creating telecommand")
            raise
        finally:
            session.close()

    @staticmethod
    def update(telecommand_id: int, data: Dict[str, Any]) -> Telecommand:
        """Apply updates to an existing telecommand."""
        session = DatabaseManager.get_session()
        try:
            telecommand = session.get(Telecommand, telecommand_id)
            if not telecommand:
                raise LookupError("Telecommand not found.")

            if "parameters" in data:
                telecommand.parameters = data["parameters"]
            if "satellite_id" in data:
                telecommand.satellite_id = int(data["satellite_id"])
            if "command_type" in data:
                telecommand.command_type = data["command_type"]
            if "priority" in data:
                telecommand.priority = int(data["priority"])
            if "status" in data:
                telecommand.update_status(data["status"])

            session.commit()
            logger.info("Telecommand updated: %s", telecommand_id)
            return telecommand
        except (TypeError, ValueError) as exc:
            session.rollback()
            logger.exception("Invalid telecommand update payload")
            raise ValueError("Invalid telecommand update payload.") from exc
        except Exception:
            session.rollback()
            logger.exception("Unexpected error while updating telecommand")
            raise
        finally:
            session.close()

    @staticmethod
    def delete(telecommand_id: int) -> None:
        """Delete a telecommand by id."""
        session = DatabaseManager.get_session()
        try:
            telecommand = session.get(Telecommand, telecommand_id)
            if not telecommand:
                raise LookupError("Telecommand not found.")

            session.delete(telecommand)
            session.commit()
            logger.info("Telecommand deleted: %s", telecommand_id)
        except Exception:
            session.rollback()
            logger.exception("Unexpected error while deleting telecommand")
            raise
        finally:
            session.close()
