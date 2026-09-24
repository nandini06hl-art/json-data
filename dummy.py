import json
import time
import uuid
from flask import Flask, Response, stream_with_context

app = Flask(__name__)

WORDS = ['Hello!', ' How ', 'can I ', 'help you ', 'today?']
GAP_MS = 8000
ITEM_ID = '1'


def generate_events():
    request_id = str(uuid.uuid4())
    full_text = ''

    for word in WORDS:
        full_text += word
        event = {
            'type': 'response.output_text.delta',
            'item_id': ITEM_ID,
            'delta': word,
            'id': request_id,
        }
        yield 'data: ' + json.dumps(event) + '\n\n'
        time.sleep(GAP_MS / 2000.0)

    done_event = {
        'type': 'response.output_item.done',
        'item': {
            'id': ITEM_ID,
            'content': [
                {'text': full_text, 'type': 'output_text', 'annotations': []}
            ],
            'role': 'assistant',
            'type': 'message',
        },
        'id': request_id,
        'databricks_output': {
            'app_version_id': 'models:/dummy_test/model/1',
            'databricks_request_id': request_id,
        },
    }
    yield 'data: ' + json.dumps(done_event) + '\n\n'
    yield 'data: [DONE]\n\n'


@app.route('/stream')
def stream():
    return Response(
        stream_with_context(generate_events()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
