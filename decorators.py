import functools
from flask import jsonify

def not_implemented_yet(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return jsonify({"error": "Not implemented yet"}), 501
    return wrapper
