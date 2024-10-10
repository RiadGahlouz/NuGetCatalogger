from flask import Flask, request, jsonify
import json

app = Flask(__name__)
registry = {}

def load_registry(file_name: str):
  with open(file_name, 'r') as file:
    global registry
    registry = json.load(file)

@app.route('/package/<package_id>', methods=['GET'])
def get_package(package_id):
  pkg_id = package_id.lower()
  if pkg_id not in registry:
    return jsonify({"message": f"Package {package_id} not found"}), 404
  return jsonify({"result": registry[pkg_id]}), 200

if __name__ == '__main__':
  print("Loading registry...")
  load_registry('registry.json')
  print("Registry loaded")
  app.run(debug=True)