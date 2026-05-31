# TrustLayer MVP

![Coverage](./coverage-badge.svg)

## 📌 Overview
Το TrustLayer είναι ένα MVP project που δείχνει πώς μπορούμε να χτίσουμε μια αξιόπιστη πλατφόρμα δεδομένων με:
- **Postgres database** για αποθήκευση οικονομικών δεδομένων
- **Flask API** για πρόσβαση σε GDP data
- **Pytest tests** για αξιοπιστία και σταθερότητα
- **CI/CD pipeline** στο GitHub Actions με coverage badge

## 🚀 Quick Start
1. Κάνε clone το repo
2. Τρέξε `pip install -r requirements.txt`
3. Εκτέλεσε `flask run` για να ξεκινήσει το API
4. Κάλεσε το endpoint: `http://127.0.0.1:5000/gdp`

## ✅ Features
- Επιστροφή GDP δεδομένων μέσω API
- Tests για DB και API
- Αυτόματο pipeline με coverage report
- Coverage badge που ενημερώνεται σε κάθε commit

## 📈 Roadmap
- Φάση 1: MVP (API + DB + Tests)
- Φάση 2: Proof of Concept (δεύτερο dataset, filters)
- Φάση 3: Scaling (frontend demo, monitoring)
- Φάση 4: Exit discussions

  Trigger CI/CD deploy

---