from flask import Flask
import asyncio
import sv

app = Flask(__name__)

@app.route('/create-user', methods=['POST'])
def create_user():
    user_data = request.get_json()
    response = asyncio.run(sv.get_response(query=user_data['input']))
    return jsonify(response), 201

if __name__ == "__main__":
    app.run()
