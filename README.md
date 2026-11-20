<img width="1456" height="948" alt="image" src="https://github.com/user-attachments/assets/89b1fefe-3a86-4dea-9712-01bf228eeb3b" />
<img width="1897" height="871" alt="image" src="https://github.com/user-attachments/assets/658a2c51-22e3-411e-a080-4eb719fbe301" />


#  PhishFlow-AI
### Exploring Machine Learning Through Cybersecurity

PhishFlow-AI is a machine learning-based phishing URL detection project developed to explore how machine learning can be applied to cybersecurity, particularly in identifying potentially malicious URLs.

This project began as my first hands-on exploration of machine learning. With limited prior experience in ML, I approached it by learning the fundamentals, experimenting with visual machine learning workflows in **KNIME Analytics Platform**, and gradually implementing the same concepts using Python and Scikit-learn.

The goal was not just to build a phishing classifier, but to understand the complete machine learning process — from dataset preparation and feature extraction to model training, evaluation, and application integration.

---

##  How It Started

Machine learning was initially a new area for me. Rather than immediately jumping into complex algorithms or frameworks, I started by understanding how a basic ML pipeline works.

I explored questions such as:

- What is a dataset, and how should it be prepared?
- What are features and labels?
- How do training and testing datasets differ?
- How does a classification algorithm learn patterns?
- What do accuracy, precision, recall, and F1-score actually measure?
- How can a trained model be used in a real application?

I used **KNIME Analytics Platform** as my starting point because its visual workflow made it easier to understand the individual stages of machine learning without having to write the entire pipeline in code.

Once I understood the workflow, I moved towards implementing the project in Python.

This progression — from visual experimentation to code-based implementation — became the foundation of PhishFlow-AI.

---

##  KNIME Analytics Platform — Learning the ML Workflow

KNIME played an important role in the initial development and understanding of this project.

Instead of treating machine learning as a black box, I used KNIME to visually construct and examine the classification pipeline.

### Workflow implemented in KNIME

**CSV Reader → Number to String → Table Partitioner → Random Forest Learner → Predictor → Scorer**

| KNIME Node | Purpose |
|---|---|
| CSV Reader | Imported the prepared phishing URL dataset |
| Number to String | Converted the label column into a categorical target |
| Table Partitioner | Split the dataset into training and testing sets |
| Random Forest Learner | Trained a classification model |
| Predictor | Generated predictions on unseen test data |
| Scorer | Evaluated model performance |

### KNIME Configuration

- Train-test split: 80:20
- Sampling: Stratified
- Random seed: 42
- Algorithm: Random Forest
- Number of trees: 100

### Initial KNIME Evaluation

| Metric | Result |
|---|---:|
| Accuracy | 81.75% |
| Precision | 66.20% |
| Recall | 96.15% |
| F1-score | 78.43% |

This initial experiment helped me understand that accuracy alone is not enough to evaluate a cybersecurity classifier.

For phishing detection, recall is particularly important because false negatives represent phishing URLs that the model incorrectly classifies as legitimate.

KNIME also allowed me to experiment with a trained model using additional sample URLs and understand how a prediction workflow operates.

**What I learned through KNIME:**
- Building an end-to-end ML workflow.
- Preparing and partitioning datasets.
- Understanding classification algorithms.
- Training and testing Random Forest models.
- Evaluating predictions using a Scorer node.
- Understanding the difference between model training and inference.

---

##  Moving from KNIME to Python

After understanding the visual workflow, I implemented the machine learning pipeline in Python.

This helped me move beyond configuring nodes and understand how each stage works programmatically.

### Python ML Workflow

1. Load and validate the dataset.
2. Prepare numerical features and target labels.
3. Split the dataset using stratified sampling.
4. Train Decision Tree and Random Forest classifiers.
5. Evaluate both models.
6. Compare their performance.
7. Analyze false positives and false negatives.
8. Extract feature importance.
9. Save the trained model using Joblib.

### Models Implemented

**Decision Tree Classifier**

Used as a baseline classification model to understand how decision-based learning works.

**Random Forest Classifier**

Used as the primary model. It combines multiple decision trees to generate a classification prediction.

Random Forest was selected for integration into the Flask application based on its performance in the Python evaluation.

---

##  URL Feature Extraction

Instead of relying on website content, PhishFlow-AI analyzes numerical characteristics extracted directly from the submitted URL.

The project uses 11 features:

| Feature | Description |
|---|---|
| url_length | Total length of the URL |
| uses_https | Whether the URL uses HTTPS |
| has_at_symbol | Presence of an @ symbol |
| host_is_ip | Whether the hostname is an IP address |
| subdomain_count | Number of subdomains |
| has_hyphen_in_hostname | Presence of a hyphen in the hostname |
| uses_url_shortener | Whether a recognized URL shortener is used |
| matched_keyword_count | Number of matched suspicious keywords |
| hostname_length | Length of the hostname |
| path_length | Length of the URL path |
| hostname_digit_count | Number of digits in the hostname |

The extracted features are passed to the trained machine learning model for classification.

---

## Python Model Evaluation

The dataset contains 20,000 URL records.

| Dataset | Samples |
|---|---:|
| Training set | 16,000 |
| Testing set | 4,000 |
| Total | 20,000 |

### Model Comparison

| Metric | Decision Tree | Random Forest |
|---|---:|---:|
| Accuracy | 89.15% | 90.83% |
| Precision | 90.87% | 92.24% |
| Recall | 87.05% | 89.15% |
| F1-score | 88.92% | 90.67% |

### Random Forest Confusion Matrix

| | Predicted Legitimate | Predicted Phishing |
|---|---:|---:|
| Actual Legitimate | 1850 | 150 |
| Actual Phishing | 217 | 1783 |

### Understanding the Results

- **Accuracy:** Percentage of all predictions that were correct.
- **Precision:** How many URLs predicted as phishing were actually phishing in the test dataset.
- **Recall:** How many phishing URLs in the test dataset were correctly identified.
- **F1-score:** Harmonic mean of precision and recall.

The model achieved 90.83% accuracy on the random stratified test split.

These results are specific to this dataset and evaluation setup. They do not guarantee the same performance on new or real-world phishing URLs.

---

##  Web Application

After training and evaluating the model, I integrated it into a Flask application to make the classifier usable through a web interface.

### Application Features

**1. URL Scanner**

Users can submit a URL and receive a machine learning classification.

**2. Phishing Score**

Displays the model-estimated probability of the phishing class.

**3. Feature Analysis**

Displays the numerical URL features extracted during analysis.

**4. Scan History**

Uses SQLite to store previous scans, predictions, scores, and timestamps.

**5. Analytics Dashboard**

Displays:
- Total URLs scanned.
- Potential phishing predictions.
- Likely legitimate predictions.
- Scan distribution.

**6. Input Validation and Error Handling**

Handles empty inputs, unsupported URL protocols, and excessively long URLs.

**7. Automated Testing**

Uses Python's unittest framework to test application behaviour, input validation, scanning, and database functionality.

---

##  Tech Stack

| Technology | How It Is Used |
|---|---|
| Python | Core application and ML development |
| KNIME Analytics Platform | Visual ML workflow development and experimentation |
| Pandas | Dataset loading and preprocessing |
| Scikit-learn | Decision Tree, Random Forest, model evaluation |
| Joblib | Saving and loading the trained model |
| Flask | Backend and web application |
| SQLite | Persistent scan history |
| HTML5 | Dashboard structure |
| CSS3 | Responsive dashboard styling |
| Python unittest | Automated application testing |
| Git & GitHub | Version control and project management |
| VS Code | Development environment |

---

## Project Architecture

```text
                PHISHFLOW-AI
                      |
                      v
              Phishing URL Dataset
                      |
                      v
              Data Preprocessing
                      |
                      v
              URL Feature Extraction
                      |
                      v
              Machine Learning
                /          \
               v            v
         Decision Tree   Random Forest
               |            |
               v            v
              Model Evaluation
                      |
                      v
               Save Trained Model
                      |
                      v
                Flask Backend
                      |
             URL Submitted by User
                      |
                      v
              Feature Extraction
                      |
                      v
              Random Forest Model
                      |
                      v
              Prediction and Score
                      |
             +--------+--------+
             |                 |
             v                 v
        SQLite Database    Web Dashboard
        Scan History       Analytics
```

---

##  Project Structure

```text
PhishFlow-AI/
│
├── app.py
│
├── data/
│   ├── phishing_dataset.xlsx
│   └── ml_features.csv
│
├── models/
│   └── phishflow_random_forest.pkl
│
├── reports/
│   ├── random_forest_false_negatives.csv
│   └── random_forest_false_positives.csv
│
├── src/
│   ├── url_features.py
│   └── train_model.py
│
├── templates/
│   └── index.html
│
├── tests/
│   ├── test_app.py
│   └── test_url_features.py
│
├── .gitignore
└── README.md
```

---


##  Running Tests

Run the application tests using:

```bash
python -m unittest discover -s tests -p "test_app.py" -v
```

The tests cover:
- Homepage loading.
- Empty URL validation.
- Unsupported URL protocols.
- Valid URL scanning.
- Scan history storage.
- Dashboard analytics.

---

##  Limitations

- The system analyzes URL-based features rather than website content.
- It does not currently use live threat intelligence feeds or domain reputation services.
- A legitimate-looking URL may still lead to malicious content.
- Model predictions are not definitive security verdicts.
- The reported model metrics are based on a random stratified train-test split.
- Similarities between URLs or hostnames across the training and testing sets may influence evaluation results.

---


##  Key Learning Outcomes

Through this project, I explored:

- Machine learning fundamentals through a practical cybersecurity use case.
- Visual ML pipeline development using KNIME.
- Dataset preprocessing and feature engineering.
- Classification using Decision Tree and Random Forest.
- Model evaluation and error analysis.
- Translating a visual ML workflow into Python.
- Integrating a trained model into a Flask application.
- Using SQLite for persistent application data.
- Building and testing an end-to-end ML application.

---

**PhishFlow-AI — Learning Machine Learning by Building for Cybersecurity.**
