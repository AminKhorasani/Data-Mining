# -*- coding: utf-8 -*-
"""CA_EXTRA.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QYuZHsI0sIKMSroRxtG1c7SKM3xxMyxV

# Libraries
"""

import pandas as pd
import re
from nltk.stem import PorterStemmer
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.metrics import accuracy_score, hamming_loss, precision_score, recall_score, f1_score, multilabel_confusion_matrix

"""# Load dataset"""

df = pd.read_csv('dataset.csv')

"""# Data Cleaning"""

df.head(5)

df.info()

example_title = df['TITLE'].str.extract(r'([^a-zA-Z0-9\s\.,;:\'"\(\)\[\]?!&%-])').dropna()
example_abstract =df['ABSTRACT'].str.extract(r'([^a-zA-Z0-9\s\.,;:\'"\(\)\[\]?!&%-])').dropna()

stemmer = PorterStemmer()

def clean_text(text):
    # remove special characters
    text = re.sub(r'\$.*?\$', '', text)
    # normalization
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = ' '.join([stemmer.stem(word) for word in text.split()])
    return text

# apply function
df['TITLE'] = df['TITLE'].apply(clean_text)
df['ABSTRACT'] = df['ABSTRACT'].apply(clean_text)

# check the cleaned text
df[['TITLE', 'ABSTRACT']].head()

"""# Part 1"""

category_counts = df[['Computer Science', 'Physics', 'Mathematics', 'Statistics',
                        'Quantitative Biology', 'Quantitative Finance']].sum()

# plotting
plt.figure(figsize=(10, 6))
category_counts.plot(kind='bar', color='blue')
plt.title('Distribution of Documents Across Subject Categories')
plt.xlabel('Subject Categories')
plt.ylabel('Number of Documents')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

"""# Part 3"""

# prepare text data
text = df['TITLE'] + ' ' + df['ABSTRACT']  # combine title and abstract
tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(text)
sequences = tokenizer.texts_to_sequences(text)
text_padded = pad_sequences(sequences, maxlen=300)

# prepare labels
labels = df[['Computer Science', 'Physics', 'Mathematics', 'Statistics', 'Quantitative Biology', 'Quantitative Finance']].values

# split data
X_train, X_test, y_train, y_test = train_test_split(text_padded, labels, test_size=0.2, random_state=42)

# build the model
model = Sequential()
model.add(Embedding(input_dim=5000, output_dim=128, input_length=300))
model.add(LSTM(64, return_sequences=True))
model.add(Dropout(0.5))
model.add(LSTM(32))
model.add(Dense(6, activation='sigmoid'))

# compile
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# train
history = model.fit(X_train, y_train, epochs=100, batch_size=64, validation_split=0.1)

"""# Part 4"""

# evaluation
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy*100:.2f}%")

predictions = model.predict(X_test)
# convert probabilities to binary predictions
predictions_binary = (predictions > 0.5).astype(int)

subset_accuracy = accuracy_score(y_test, predictions_binary)
hammingloss = hamming_loss(y_test, predictions_binary)

# evaluation parameters
precision = precision_score(y_test, predictions_binary, average='samples')
recall = recall_score(y_test, predictions_binary, average='samples')
f1 = f1_score(y_test, predictions_binary, average='samples')

print(f"Subset Accuracy: {subset_accuracy:.4f}")
print(f"Hamming Loss: {hammingloss:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

metrics = {
    "Subset Accuracy": subset_accuracy,
    "Hamming Loss": hammingloss,
    "Precision": precision,
    "Recall": recall,
    "F1 Score": f1
}

plt.figure(figsize=(10, 6))
sns.barplot(x=list(metrics.keys()), y=list(metrics.values()))
plt.title('Performance Evaluation')
plt.ylabel('Score')
plt.ylim(0, 1)
plt.show()

# confusion matrix
conf_matrices = multilabel_confusion_matrix(y_test, predictions_binary)

# plotting an example
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrices[0], annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix for Label 1')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()