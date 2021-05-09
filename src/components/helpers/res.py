from flask import jsonify

def build_res_obj(message, status_code=None, payload=None):
  res_obj = {}
  res_obj['message'] = f'{message}'
  res_obj['data'] = payload
  res = jsonify(res_obj)
  res.status_code = status_code
  return res