from flask import Flask, render_template, request
import mysql.connector
import pandas as pd
from config import DB_CONFIG
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

app = Flask(__name__)

# Function to execute the query and return data
def get_transaction_data():
    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['dbname'],
            port=DB_CONFIG['port']
        )
        query = """
            SELECT 
                SUBSTRING(hub_service_provider_id, 1, LENGTH(hub_service_provider_id) - 13) AS USER,
                country_code,
                mno_name,
                currency,
                order_id,
                reference_id,
                transaction_timestamp,
                updated_at,
                amount, 
                payment_status,
                user_msisdn
            FROM mobilemoneydb.payment_transactions
            WHERE transaction_timestamp > '2024-01-01' -- You can adjust the date filter
        """
        # Read data into a Pandas DataFrame
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("Error connecting to the database:", e)
        return None

# Function to train a machine learning model
def train_model(df):
    # Preprocess data (example: encoding categorical variables)
    df = pd.get_dummies(df, columns=['country_code', 'mno_name', 'currency', 'payment_status'], drop_first=True)
    
    # Assuming 'payment_status' is the target variable
    X = df.drop(columns=['payment_status', 'order_id', 'reference_id', 'transaction_timestamp', 'updated_at'])
    y = df['payment_status']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a Random Forest model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Get model predictions and classification report
    predictions = model.predict(X_test)
    report = classification_report(y_test, predictions)

    return report

@app.route('/', methods=['GET', 'POST'])
def index():
    data = get_transaction_data()
    if data is not None:
        table = data.to_html(classes='table table-striped', index=False)
        model_report = ''
        if request.method == 'POST':
            model_report = train_model(data)
        return render_template('index.html', table=table, model_report=model_report)
    else:
        return "<p>Failed to retrieve data from the database.</p>"

if __name__ == '__main__':
    app.run(debug=True)
