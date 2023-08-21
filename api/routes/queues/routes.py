from flask import request
from flask.views import MethodView
from _helpers import submit_message

class QueueView(MethodView):
    
    def post(self, queue_name):
        args = request.get_json()
        message = args["message"]
        message_submitted = submit_message(queue_name, message)
        return message_submitted, 201

