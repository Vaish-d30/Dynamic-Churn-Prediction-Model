from flask import Flask, request, render_template, url_for
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import os

app = Flask(__name__)

if not os.path.exists('static'):
    os.makedirs('static')

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    try:
    
        data = pd.read_csv(file)
        print("Columns:", data.columns)

        
        churn_col = next((col for col in ['Churn', 'Exited'] if col in data.columns), None)
        if churn_col is None:
            raise KeyError("Churn column not found!")

        
        data = data.drop(['CustomerId', 'Surname'], axis=1, errors='ignore')

        
        data = data.dropna()

        
        for col in data.select_dtypes(include=['object']).columns:
            data[col] = data[col].astype('category').cat.codes

        
        X = data.drop([churn_col], axis=1)
        y = data[churn_col]

        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        
        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        conf_matrix = confusion_matrix(y_test, y_pred)

        plt.figure(figsize=(6, 4))
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Churned', 'Churned'], 
                    yticklabels=['Not Churned', 'Churned'])
        plt.title('Actual vs Predicted Churn')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.savefig('static/confusion_matrix.png')
        plt.close()

        feature_importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
        plt.figure(figsize=(8, 5))
        sns.barplot(x=feature_importances, y=feature_importances.index)
        plt.title('Feature Importance - Why Customers Churn')
        plt.xlabel('Importance Score')
        plt.ylabel('Features')
        plt.savefig('static/feature_importance.png')
        plt.close()

        result = f'Model Accuracy: {accuracy * 100:.2f}%'
        return render_template('upload.html', prediction=result)

    except Exception as e:
        return f"An error occurred: {str(e)}", 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
