from flask import request, jsonify


def read_pagination():

    try:

        page = int(request.args.get("page", 1))

        size = int(request.args.get("size", 10))

    except (ValueError, TypeError):

        return None, None, (
            jsonify({
                "success": False,
                "error": "Page and size must be whole numbers."
            }),
            400
        )

    if page < 1:

        return None, None, (
            jsonify({
                "success": False,
                "error": "Page must be at least 1."
            }),
            400
        )

    if size < 1 or size > 100:

        return None, None, (
            jsonify({
                "success": False,
                "error": "Size must be between 1 and 100."
            }),
            400
        )

    return page, size, None


def require_json_object():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return None, (
            jsonify({
                "success": False,
                "error": "A valid JSON object is required."
            }),
            400
        )

    return data, None