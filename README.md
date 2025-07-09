# 🧠 AI Meal Planner App 🍽️

The **AI Meal Planner** is a smart dietary planning application that creates personalized meal plans based on your age, weight, gender, and dietary preference (vegan, vegetarian, non-vegetarian). It calculates your BMR, optimizes meals using the knapsack algorithm, and generates creative descriptions using **LLaMA 3 (Groq API)**.

---

## 📸 Demo

### 🏠 Home Page  
![Image](https://github.com/user-attachments/assets/3d2d891e-3dc6-4b78-b586-66421f3b4d37)

### 🧠 Meal Suggestions  
![Image](https://github.com/user-attachments/assets/bf242436-46ab-41c6-a5a2-75a523693a9f)

### 📝 Generated Meal Plan  
![Image](https://github.com/user-attachments/assets/b84d075f-d52e-4b52-8a21-799aecaa1391)

### 📄 PDF Export  
![Image](https://github.com/user-attachments/assets/4e427504-005f-4ad7-b32e-0d56f4bbb4dd)


## 🔥 Features

- 🔢 BMR (Calorie) calculation based on user profile
- 🥦 Choose your diet: **Vegan**, **Vegetarian**, or **Non-Vegetarian**
- 📦 Meal optimization using **Knapsack algorithm**
- 🧠 AI-generated meal names and descriptions via **Groq’s LLaMA-3**
- 📄 Export full meal plan as a downloadable PDF
- 🧪 Streamlit-based interactive UI

## 🛠️ Tech Stack

- **Python**
- **Streamlit** – UI & interactivity
- **Pandas** – Data manipulation
- **FPDF** – PDF export
- **Groq API** – AI-generated meal names & descriptions
- **Knapsack Algorithm** – Optimized food item selection

🚀 How to Run the App
Install dependencies
pip install -r requirements.txt
Add your Groq API key
Create a file .streamlit/secrets.toml and add:

Add your Groq API key
Create a file .streamlit/secrets.toml and add:
GROQ_API_KEY = "your_api_key"
Run the app
streamlit run streamlit_meal_planner.py

## 📁 Project Structure
```
AI-Meal-Planner/
├── data.py                  # Meal item data
├── knapsack.py              # Knapsack logic
├── pdf_exporter.py          # PDF export functionality
├── streamlit_meal_planner.py # Main Streamlit app
├── requirements.txt
├── README.md
└── .streamlit/
    └── secrets.toml

```
## 👨‍💻 Author

Made with ❤️ by Samarth Shekhar
GitHub
https://github.com/Samarth-Shekhar 
LinkedIn 
www.linkedin.com/in/samarth-shekhar-185ba311a
```


