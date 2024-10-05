from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
import logging

from ..services import repository_service
from ..schemas import SetupRepositorySchema, SetupRepository

logger = logging.getLogger(__name__)

repository_bp = Blueprint('repository', __name__)

@repository_bp.route('/repository/setup', methods=['POST'])
async def repository_setup():
    """Endpoint to setup the repository."""

    try:
        data = SetupRepositorySchema().load(request.get_json())

        if not isinstance(data, SetupRepository):
            raise ValidationError('Invalid data')

    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")
        return jsonify({'errors': err.messages}), 400

    except Exception as err:
        logger.error(f"Unexpected error during validation: {str(err)}")
        return jsonify({'message': 'Internal Server Error'}), 500

    try:
        response = await repository_service.setup(
            data
        )

        return response

    except Exception as err:
        logger.error(f"Error in repository setup: {str(err)}")
        return jsonify({'message': 'Failed to setup repository'}), 500
