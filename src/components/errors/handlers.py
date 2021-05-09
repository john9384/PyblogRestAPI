from flask import jsonify

class CustomError(Exception):
    """
    A Custom error class extending from the exeption
    """

    def __init__(self,message,status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

    def get_json(self):
      return "Hello"

def build_err_obj(message, status_code, payload=None):
      err = {}
      err['message'] = f'{message}'
      err['payload']= payload
      res = jsonify(err)
      res.status_code = status_code
      return res

