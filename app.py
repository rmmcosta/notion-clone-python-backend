from flask import Flask, request, Response, stream_with_context, make_response
from flask_cors import CORS
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

def generate(completion):
    for chunk in completion:
        chunk_message = chunk.choices[0].delta.get('content')
        if chunk_message is not None:
            yield f"data: {json.dumps({'message': chunk_message})}\n\n"

@app.route('/api/completion', methods=['POST'])
def completion():
    print(request.get_json())
    data = request.get_json()
    prompt = data['prompt']

    completion = client.chat.completions.create(model='gpt-3.5-turbo',
    messages = [
        {
            'role': 'system',
            'content': '''You are a helpful AI embedded in a notion text editor app that is used to autocomplete sentences.
            The traits of AI include expert knowledge, helpfulness, cleverness, and articulateness.
            AI is a well-behaved and well-mannered individual.
            AI is always friendly, kind, and inspiring, and he is eager to provide vivid and thoughtful responses to the user.'''
        },
        {
            'role': 'user',
            'content': '''I am writing a piece of text in a notion text editor app.
            Help me complete my train of thought here: ##{}##
            keep the tone of the text consistent with the rest of the text.
            keep the response short and sweet.'''.format(prompt)
        },
    ],
    stream=True)

    response = Response(stream_with_context(generate(completion)), mimetype='text/event-stream')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/hello', methods=['GET'])
def hello():
    response = make_response('Hello, World!')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(port=3004, debug=True)