# Climate-Smart Agriculture Prediction API

A production-ready pipeline that takes user input on soil and weather, predicts the optimal crop using a trained Random Forest model, and simultaneously calculates sustainability metrics and irrigation methods. It features a modern Streamlit frontend and an LLM-powered conversational Chatbot!

## Steps to Start and Initialize

Follow these steps exactly to initialize your environment, train the model, and start the full application:

### 1. Install Dependencies
Initialize the virtual environment and install all required Python packages (including FastAPI and Streamlit):

**Using Make:**
```bash
make install
```

**Without Make:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Set up your local environment file. Make sure to add your `GROQ_API_KEY` for the Chatbot functionality:
```bash
cp .env.example .env
```

### 3. Train the Model
Train the Random Forest model using your local `crop_cleaned.xls` dataset. This will automatically process the data, perform a grid search, and save the optimized model artifact (`models/rf_crop_model.joblib`):

**Using Make:**
```bash
make train
```

**Without Make:**
```bash
source .venv/bin/activate
python -m src.ml.train
```

### 4. Run the Full Stack
Start both the FastAPI backend and the Streamlit frontend:

**Using Make (Runs both concurrently):**
```bash
make run
```

**Without Make:**
Open two separate terminal windows. Make sure your virtual environment is activated in both (`source .venv/bin/activate`).

**Terminal 1 (Backend):**
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
python -m streamlit run src/frontend/app.py --server.headless true --server.fileWatcherType none
```

### 5. Access the Application
Once the servers are running, open your web browser and navigate to:
👉 **[http://localhost:8501](http://localhost:8501)** (Streamlit Frontend UI)

*(The backend API Swagger Docs are still accessible at [http://localhost:8000/docs](http://localhost:8000/docs))*
