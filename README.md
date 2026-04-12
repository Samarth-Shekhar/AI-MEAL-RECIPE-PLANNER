<div align="center">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-000000?style=for-the-badge&logo=groq&logoColor=white" />
  <img src="https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white" />
</div>

<h1 align="center">🥗 NutriAI - Personal AI Meal Planner & Recipe Generator</h1>

<p align="center">
  A premium, beautifully designed, all-in-one dietary dashboard that leverages advanced algorithms and the blazing-fast Groq Llama-3 API to instantly calculate your body metrics, optimize macronutrients, and generate authentic recipes.
</p>

---

## ✨ Key Features

- **Single-Page Glassmorphism UI:** A sleek, fully responsive and dynamic web dashboard. Includes a built-in Dark/Light mode toggle with breathtaking ambient gradients.
- **Live Body Analysis:** Input your physical metrics and lifestyle, and the dashboard instantly visualizes your health status on a dynamic Plotly BMI Gauge. Features completely live statistics including BMR, TDEE, exact Calorie Targets, and a calculated Protein Target (in grams).
- **Fast-Track Parallel AI Generation:** Waits of the past are over. Using Python multithreading, NutriAI crafts all three daily meals (Breakfast, Lunch, and Dinner), generating immersive AI descriptions and authentic recipes concurrently—reducing generation time to less than 5 seconds.
- **Advanced Knapsack Optimization:** Uses a dynamic programming approach (the Knapsack algorithm) behind the scenes to accurately hit your calorie macros utilizing our curated nutritional database.
- **Master PDF Export:** Instantly download a comprehensive, beautifully formatted PDF of your exact BMI details, daily meal structure, and full recipes for offline viewing (complete with safe UTF sanitization).

## 🪟 Interface Preview

Our dashboard boasts a stunning interface powered solely by custom Streamlit CSS injection:
- Real-time Plotly Indicator Dashboard.
- Smooth, translucent frosted-glass floating cards.
- Complete 1-Page flow (No page refreshes or hidden components).

## ⚙️ Installation & Usage

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/Samarth-Shekhar/AI-MEAL-RECIPE-PLANNER.git
cd AI-MEAL-RECIPE-PLANNER
```

### 3. Install Dependencies
Install all required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```
*(Core dependencies: `streamlit`, `plotly`, `requests`, `fpdf`)*

### 4. API Keys Configuration
This project relies on the **Groq API** for ultra-fast Llama-3 recipe generation.
Create a `.streamlit` folder in the root directory and add a `secrets.toml` file:

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "gsk_YourAPIKeyGoesHere"
```

### 5. Run the Application
```bash
streamlit run streamlit_meal_planner.py
```
Open your browser to `http://localhost:8501`.

## 🧠 Project Architecture
- **`streamlit_meal_planner.py`:** The main engine running the UI, CSS, Knapsack algorithm, multithreading, and Plotly graphics.
- **`recipe_generator.py`:** Pre-built deterministic authentic recipe formulations.
- **`prompts.py`:** Tuned LLM templates requesting dietary rationale and flavor profiles.
- **`data.py`:** Core nutritional database mapping containing macro/calorie counts for various diets (Vegan/Vegetarian/Non-Vegetarian).
- **`pdf_exporter.py`:** Dynamic FPDF generation engine parsing emojis and UTF characters safely into a downloadable plan.

---
**Created by [Samarth Shekhar](https://github.com/Samarth-Shekhar)**
