from flask import request, jsonify, Blueprint
from index import app
from worker import task_queue


main = Blueprint("main", __name__)


@main.route("/api/search", methods=["POST"])
def search_for_name():
    name_to_search = request.form.get("name", default=None, type=str)
    year_to_search = request.form.get("year", default=None, type=str)
    email = request.form.get("email", default=None, type=str)

    if not name_to_search or not year_to_search:
        return jsonify({"error": "Both 'name' and 'year' parameters are required"}), 400

    # Add the task to the queue
    task_queue.put((name_to_search, year_to_search, email))

    return (
        jsonify(
            {
                "message": "Your request is being processed. You will be updated by email."
            }
        ),
        200,
    )


app.register_blueprint(main)
