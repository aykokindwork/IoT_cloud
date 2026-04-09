# test_model.py
print("Смотрим первые байты scaler.pkl...")
with open("models/scaler.pkl", "rb") as f:
    print(f.read(20))

print("\nСмотрим первые байты label_encoder.pkl...")
with open("models/label_encoder.pkl", "rb") as f:
    print(f.read(20))