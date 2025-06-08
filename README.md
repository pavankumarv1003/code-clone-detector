---
title: Clone Detector App
emoji: 🐢
colorFrom: green
colorTo: gray
sdk: docker
pinned: false
license: apache-2.0
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Neural Network-Based Clone Detection

A deep learning-powered web application to detect structural similarities between two Java code snippets. This project uses a Siamese Long Short-Term Memory (LSTM) network to overcome the limitations of traditional token-based models and achieve high accuracy in identifying Type-1, Type-2, and Type-3 code clones.

**[➡️ Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/Ted6000/clone-detector-app)**

---

## Table of Contents
- [Project Overview](#project-overview)
- [How It Works: The Architecture](#how-it-works-the-architecture)
- [Dataset](#dataset)
- [Performance & Results](#performance--results)
- [Tech Stack](#tech-stack)
- [How to Run Locally](#how-to-run-locally)
- [Project Evolution & Challenges](#project-evolution--challenges)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Project Overview

Code clones—segments of code that are identical or functionally similar—are common in large software projects. While sometimes benign, they can increase maintenance costs and propagate bugs. This project aims to build a reliable tool for detecting these clones.

The initial approach using TF-IDF and a simple neural network resulted in a misleading 100% accuracy due to "identifier leakage." This project documents the journey of diagnosing that issue and implementing a sophisticated Siamese LSTM network that learns the underlying structure of code, providing a much more robust and realistic solution.

### Key Features
- **Structural Similarity Detection:** Goes beyond simple text matching to understand the sequence and structure of code.
- **Resilient to Renaming:** Correctly identifies clones even when variable, method, and class names have been changed (Type-2 clones).
- **Handles Minor Modifications:** Can detect similarities even when lines of code have been added or removed (Type-3 clones).
- **Interactive Web Interface:** A simple and intuitive web UI built with Flask to test any two Java code snippets in real-time.

---

## How It Works: The Architecture

The model uses a Siamese network architecture, which is specifically designed for comparing two inputs to determine their similarity.

```mermaid
graph TD
    subgraph Input
        A[Code Snippet A] --> B(Abstract & Tokenize);
        C[Code Snippet B] --> D(Abstract & Tokenize);
    end
    
    subgraph Preprocessing
        B --> E{Keras Tokenizer};
        D --> E;
        E --> F[Pad Sequences];
    end

    subgraph Siamese Network
        F --> G1(Shared LSTM Model);
        F --> G2(Shared LSTM Model);
    end

    G1 --> H{Embedding Vector A};
    G2 --> I{Embedding Vector B};

    subgraph Similarity Calculation
        H --> J(Calculate Manhattan Distance);
        I --> J;
        J --> K[Similarity Score (0-1)];
    end
    
    K --> L[Final Prediction: Clone / Not Clone];

```

1.  **Code Abstraction:** Each Java code snippet is first parsed using the `javalang` library. All specific identifiers (variable/method names) are replaced with a generic `"ID"` token, and literals (e.g., `"hello"`) are replaced with `"LITERAL"`. This forces the model to learn structure, not names.
2.  **Tokenization & Sequencing:** The abstracted code is converted into a sequence of integers by a `keras.Tokenizer`, where each unique token gets a unique integer ID.
3.  **Padding:** All sequences are padded or truncated to a fixed length (`MAX_SEQUENCE_LENGTH = 200`) so they can be fed into the LSTM network.
4.  **Siamese LSTM Model:**
    - Two identical, weight-sharing LSTM "twin" networks process the two sequences.
    - Each LSTM network learns to process its input sequence and outputs a fixed-size embedding vector—a dense numerical representation (a "fingerprint") of the code's semantic structure.
5.  **Similarity Calculation:** The Manhattan Distance between the two embedding vectors is calculated. This distance measures how "far apart" the two code snippets are in the learned embedding space. This distance is then passed through an exponentiated negative absolute difference layer to produce a final similarity score between 0 (completely different) and 1 (identical).

---

## Dataset

This model was trained on a subset of the **BigCloneBench** dataset (specifically, the IJaDataset 2.0).

- **Total Code Pairs:** 20,000
- **Class Distribution:**
  - **Clones (Label 1):** 10,000
  - **Non-Clones (Label 0):** 10,000

---

## Performance & Results

The final Siamese LSTM model was evaluated on a held-out test set (20% of the total data, amounting to 3,974 pairs). The model demonstrates excellent performance, achieving a final validation accuracy of **98.05%**.

- **Final Validation Accuracy:** `98.05%`
- **Final Validation Loss:** `0.0649`

**Classification Report:**
```
              precision    recall  f1-score   support

           0       0.98      0.97      0.98      1959
           1       0.97      0.98      0.98      2015

    accuracy                           0.98      3974
   macro avg       0.98      0.98      0.98      3974
weighted avg       0.98      0.98      0.98      3974
```

---

## Tech Stack

- **Backend:** Flask
- **Deep Learning:** TensorFlow / Keras
- **Code Parsing:** `javalang`
- **Data Handling:** Pandas, NumPy, Scikit-learn
- **Deployment:** Docker, Gunicorn, Hugging Face Spaces

---

## How to Run Locally

To set up and run this project on your own machine, follow these steps.

1.  **Clone the Repository:**
    ```bash
    git clone https://huggingface.co/spaces/Ted6000/clone-detector-app
    cd clone-detector-app
    ```

2.  **Set Up a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask Web Application:**
    ```bash
    python app.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

*(Optional) To retrain the model, you would run the `preprocess_and_train.py` script, which will regenerate the `.h5` and `.pkl` files.*

---

## Project Evolution & Challenges

This project underwent a significant architectural evolution, which is a core part of the learning experience.

-   **Initial Model & The "100% Accuracy" Problem:** The first version used a TF-IDF vectorizer and a simple feedforward neural network. It achieved near-perfect accuracy on both training and test sets.
-   **The Diagnosis - Data Leakage:** This "too good to be true" result was diagnosed as a classic case of data leakage. The model wasn't learning code structure; it was simply memorizing that clone pairs shared the same unique variable and method names.
-   **The Solution - Abstraction and Sequence Modeling:** The problem was solved by fundamentally changing the approach:
    1.  **Code Abstraction:** `javalang` was introduced to strip away specific identifiers.
    2.  **Sequence Modeling:** The model architecture was upgraded to a Siamese LSTM network to analyze the *order* of tokens, allowing it to learn true programming patterns and logic.

---

## Future Improvements

-   **Advanced Models:** Explore using more powerful, pre-trained transformer models like **CodeBERT** or **GraphCodeBERT**, which have a deeper understanding of code semantics and could potentially solve Type-4 (functional) clone detection.
-   **Handling More Languages:** Extend the parser and model to support other programming languages like Python or JavaScript.
-   **Performance Optimization:** For very large code snippets, optimize the prediction speed or implement batch processing.

---

## Author

-   **Pavan Kumar V**
