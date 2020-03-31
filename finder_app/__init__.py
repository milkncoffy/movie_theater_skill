# coding: utf-8
from __future__ import unicode_literals
import json
import logging
from flask import Flask, request
from finder_app.dialog_processing import handle_dialog
from finder_app.data_holders import SessionStorage
from finder_app.session import *

app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)
session_storage = SessionStorage()


@app.route("/", methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "text": "",
            "end_session": False
        }
    }

    session_info = request.json['session']
    if session_info['new']:
        session = Session(session_info['session_id'], session_info['user_id'])
        session_storage.add_session(session_info['session_id'], session)
    else:
        session = session_storage.get_session(session_info['session_id'])
    handle_dialog(session, request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )
