from flask import Flask, request, render_template
import numpy as np
import pickle
import javalang
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow.keras.backend as K

app = Flask(__name__)

# --- Load the NEW pre-trained models ---
print("Loading Siamese model and Keras tokenizer...")

# Define the custom distance function so Keras knows what it is when loading the model
def manhattan_distance(vectors):
    vec1, vec2 = vectors
    return K.exp(-K.sum(K.abs(vec1 - vec2), axis=1, keepdims=True))

try:
    # When loading a model with custom layers/functions, you need to provide them
    MODEL = load_model("siamese_lstm_model.h5", custom_objects={'manhattan_distance': manhattan_distance})
    TOKENIZER = pickle.load(open("keras_tokenizer.pkl", 'rb'))
    MAX_SEQUENCE_LENGTH = 200 # Must be the same value used in training
    print("✅ Models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    MODEL, TOKENIZER = None, None

# (Your javalang abstraction function remains the same)
def abstract_code_from_string(code_string):
    # ... same as before ...
    try:
        tokens = list(javalang.tokenizer.tokenize(code_string))
        abstracted_tokens = []
        for token in tokens:
            if isinstance(token, javalang.tokenizer.Identifier):
                abstracted_tokens.append("ID")
            elif isinstance(token, javalang.tokenizer.Literal) and ('"' in token.value or "'" in token.value):
                abstracted_tokens.append("LITERAL")
            else:
                abstracted_tokens.append(token.value)
        return ' '.join(abstracted_tokens)
    except:
        return ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not MODEL or not TOKENIZER:
        return render_template('index.html', result_text="Error: Model not loaded.")

    code1 = request.form['code1']
    code2 = request.form['code2']

    # 1. Abstract the code (same as before)
    abstracted_code1 = abstract_code_from_string(code1)
    abstracted_code2 = abstract_code_from_string(code2)

    # 2. Convert to integer sequences using the loaded Tokenizer
    seq1 = TOKENIZER.texts_to_sequences([abstracted_code1])
    seq2 = TOKENIZER.texts_to_sequences([abstracted_code2])

    # 3. Pad the sequences
    padded1 = pad_sequences(seq1, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post')
    padded2 = pad_sequences(seq2, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post')
    
    # 4. Make a prediction
    # The model expects a list of two inputs
    prediction_prob = MODEL.predict([padded1, padded2])[0][0]
    confidence = prediction_prob * 100

    # 5. Format the result (can use a threshold like 50 or tune it)
    if confidence > 50:
        result_text = f"Result: CLONE ({confidence:.0f}% Confidence)"
    else:
        result_text = f"Result: NOT a Clone ({(100-confidence):.0f}% Confidence)"
        
    return render_template('index.html', result_text=result_text)

if __name__ == '__main__':
    app.run(debug=True)