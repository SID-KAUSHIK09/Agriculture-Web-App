"""Fixed lists shared by the forms, the database and the model."""

# Order matches the integer labels (0-21) in data/crop_recommendation.csv.
CROP_LABELS = [
    "Rice", "Maize", "Chickpea", "Kidney beans", "Pigeon peas", "Moth beans",
    "Mung bean", "Black gram", "Lentil", "Pomegranate", "Banana", "Mango",
    "Grapes", "Watermelon", "Muskmelon", "Apple", "Orange", "Papaya",
    "Coconut", "Cotton", "Jute", "Coffee",
]

# Crop names exactly as stored in data/info.db (same order as the form's options 1-22).
INFO_CROPS = [
    "Rice", "Maize", "Chickpea", "Kidneybeans", "Pigeonpeas", "Mothbeans",
    "Mungbean", "Blackgram", "Lentil", "Pomegranate", "Banana", "Mango",
    "Grapes", "Watermelon", "Muskmelon", "Apple", "Orange", "Papaya",
    "Coconut", "Cotton", "Jute", "Coffee",
]

INFO_TYPES = [
    "Crop Plan", "Seeds Information", "Soil Needs", "Irrigation Strategy",
    "Protecting the crop", "Machinery Required", "Storage Information", "MSP of crop",
]

# Model input features, in the column order of the training CSV.
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
