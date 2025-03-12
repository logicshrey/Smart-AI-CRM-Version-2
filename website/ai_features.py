import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, timedelta

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
    def prepare_transaction_data(self, transactions):
        # Convert QuerySet to DataFrame
        data = []
        for t in transactions:
            data.append({
                'amount': float(t.amount) if hasattr(t, 'amount') else 0,
                'hour': t.created_at.hour if hasattr(t, 'created_at') else 0,
                'day_of_week': t.created_at.weekday() if hasattr(t, 'created_at') else 0,
            })
        df = pd.DataFrame(data)
        return self.scaler.fit_transform(df)
    
    def detect_anomalies(self, transactions):
        if not transactions:
            return []
        
        X = self.prepare_transaction_data(transactions)
        predictions = self.model.fit_predict(X)
        
        # Return indices of anomalies
        return [i for i, pred in enumerate(predictions) if pred == -1]

class VirtualAgent:
    def __init__(self):
        self.responses = {
            'greeting': [
                "Hello! How can I assist you today?",
                "Welcome! What can I help you with?",
                "Hi there! How may I help you?"
            ],
            'farewell': [
                "Thank you for using our service. Have a great day!",
                "Goodbye! Feel free to return if you need more assistance.",
                "Thanks for chatting. Take care!"
            ],
            'account': [
                "I can help you with account-related queries. What specific information do you need?",
                "For account assistance, please provide your account number or username."
            ],
            'payment': [
                "I can help you with payment-related questions. Would you like to know about payment methods or make a payment?",
                "For payment assistance, I can guide you through our payment options."
            ],
            'default': [
                "I'm not sure I understand. Could you please rephrase that?",
                "I apologize, but I need more information to help you better."
            ]
        }
        
    def get_intent(self, message):
        message = message.lower()
        if any(word in message for word in ['hi', 'hello', 'hey']):
            return 'greeting'
        elif any(word in message for word in ['bye', 'goodbye', 'thank']):
            return 'farewell'
        elif any(word in message for word in ['account', 'profile', 'login']):
            return 'account'
        elif any(word in message for word in ['pay', 'payment', 'bill']):
            return 'payment'
        return 'default'
    
    def get_response(self, message):
        intent = self.get_intent(message)
        return np.random.choice(self.responses[intent])

def analyze_customer_behavior(customer_data, timeframe_days=30):
    """Analyze customer behavior patterns"""
    today = datetime.now()
    start_date = today - timedelta(days=timeframe_days)
    
    # Example metrics
    metrics = {
        'total_transactions': len(customer_data),
        'average_amount': np.mean([float(t.amount) for t in customer_data]) if customer_data else 0,
        'transaction_frequency': len(customer_data) / timeframe_days if customer_data else 0
    }
    
    return metrics
