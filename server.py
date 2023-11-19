from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint to handle POST requests
@app.route('api/endpoint', methods=['POST'])
def endpoint():
    data = request.get_json()  # Get JSON data from the request body
    print('Received POST request with data:', data)

    # Process the data as needed
    # ...

    # Send a response back to the client
    response_data = {'message': 'POST request received successfully'}
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)