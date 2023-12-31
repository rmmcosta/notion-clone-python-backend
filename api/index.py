from flask import Flask, request, jsonify, make_response, Response
from flask_cors import CORS
import time
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY',''))
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/completion/metrics', methods=['POST'])
def completionMetrics():
    data = request.get_json()
    prompt = data['prompt']

    start_time = time.time()

    completion = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
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
        stream=True
    )

    collected_chunks = []
    collected_messages = []

    for chunk in completion:
        chunk_time = time.time() - start_time
        collected_chunks.append(chunk)
        chunk_message = chunk.choices[0].delta.content
        collected_messages.append(chunk_message)

    collected_messages = [m for m in collected_messages if m is not None]
    full_reply_content = ''.join([m for m in collected_messages])

    return jsonify({
        'time': chunk_time,
        'conversation': full_reply_content
    })
    
@app.route('/api/completion', methods=['POST'])
def completion():
    data = request.get_json()
    prompt = data['prompt']

    def generate():
        completion = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
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
            stream=True
        )

        for chunk in completion:
            chunk_message = chunk.choices[0].delta.content
            if chunk_message is not None:
                yield chunk_message

    return Response(generate(), mimetype='text/plain')

@app.route('/api/hello', methods=['GET'])
def hello():
    response = make_response('Hello, World!')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/env-var-test', methods=['GET'])
def envVarTest():
    return os.environ.get('MY_ENV_VAR','MY_ENV_VAR Not Found')

@app.route('/')
def home():
    return "Working..."

if __name__ == '__main__':
    app.run()