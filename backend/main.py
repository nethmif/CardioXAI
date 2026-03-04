# import torch
# import io
# import cv2
# import numpy as np
# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# from PIL import Image
# from model_utils import HierarchicalECGModel
# from processor import process_ecg_signal
# import base64
# from xai_helper import generate_heatmaps
# import matplotlib
# matplotlib.use('Agg')
# matplotlib.font_manager._get_fontconfig_fonts.cache_clear()
# import matplotlib.pyplot as plt
# import joblib
# import pandas as pd
# import dice_ml
# import shap
# import lime
# from pydantic import BaseModel
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()      

# client = OpenAI()

# app = FastAPI()

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],  
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# device = torch.device("cpu")
# model = HierarchicalECGModel().to(device)

# # checkpoint = torch.load('backend/checkpoints/best_hierarchical_model.pth', map_location=device)
# checkpoint = torch.load('checkpoints/best_hierarchical_model.pth', map_location=device)
# model.load_state_dict(checkpoint['model_state_dict'])
# model.eval()

# @app.get("/")
# def read_root():
#     return {"message": "CardioXAI API is running"}

# def encode_img(img):
#     _, buffer = cv2.imencode('.jpg', img)
#     return base64.b64encode(buffer).decode('utf-8')

# @app.post("/predict")
# async def predict(file: UploadFile = File(...)):
#     try:
#         data = await file.read()
#         image = Image.open(io.BytesIO(data)).convert('RGB')
#         img_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#         processed_img = process_ecg_signal(img_cv2)
        
#         img_t = torch.from_numpy(processed_img).float().permute(2, 0, 1) / 255.0
#         mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
#         std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
#         img_t = (img_t - mean) / std
#         input_tensor = img_t.unsqueeze(0).to(device)
        
#         with torch.no_grad():
#             out1, out2 = model(input_tensor)
#             prob1 = torch.sigmoid(out1).item()
#             if prob1 > 0.5:
#                 l1_label = "Myocardial"
#                 display_confidence = prob1  
#             else:
#                 l1_label = "Other Cardiac Conditions"
#                 display_confidence = 1 - prob1 
#             l2_idx = torch.argmax(out2, dim=1).item()
#             l2_classes = ['Normal', 'Abnormal Heartbeat', 'History of MI', 'Acute MI']
#             l2_label = l2_classes[l2_idx]

#         rgb_for_xai = processed_img.astype(np.float32) / 255.0
#         vis_l1, vis_l2 = generate_heatmaps(model, input_tensor, rgb_for_xai)
        
#         return {
#             "level1_prediction": l1_label,
#             "level1_confidence": f"{display_confidence:.4f}",
#             "level2_prediction": l2_label,
#             "heatmap_l1": f"data:image/jpeg;base64,{encode_img(vis_l1)}",
#             "heatmap_l2": f"data:image/jpeg;base64,{encode_img(vis_l2)}"
#         }

#     except Exception as e:
#         import traceback
#         print(traceback.format_exc()) 
#         return {"error": str(e)}

# def get_base64_plot(fig=None):
#     buf = io.BytesIO()
#     if fig:
#         fig.savefig(buf, format='png', bbox_inches='tight')
#     else:
#         plt.savefig(buf, format='png', bbox_inches='tight')
    
#     buf.seek(0)
#     img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
#     plt.close('all')  
#     return img_str

# FEATURE_NAMES_DISPLAY = {
#     'age': 'Age', 
#     'sex': 'Gender', 
#     'cp': 'Chest Pain Type', 
#     'trestbps': 'Resting BP (mmHg)', 
#     'chol': 'Cholesterol (mg/dl)', 
#     'fbs': 'Fasting Sugar > 120', 
#     'restecg': 'Resting ECG', 
#     'thalach': 'Max Heart Rate', 
#     'exang': 'Exercise Angina', 
#     'oldpeak': 'ST Depression', 
#     'ca': 'Major Vessels', 
#     'thal': 'Thallium Stress', 
#     'slope': 'ST Slope'
# }

# INTERNAL_MAPPING = {
#     "cp": {"typical angina": 0.0, "atypical angina": 1.0, "non-anginal": 2.0, "asymptomatic": 3.0},
#     "restecg": {"normal": 0.0, "stt abnormality": 1.0, "lv hypertrophy": 2.0},
#     "slope": {"upsloping": 0.0, "flat": 1.0, "downsloping": 2.0},
#     "thal": {"normal": 1.0, "fixed defect": 2.0, "reversible defect": 3.0}
# }

# # clinical_model = joblib.load('backend/checkpoints/clinical_model.pkl')
# # dice_train_df = pd.read_pickle('backend/checkpoints/train_data.pkl')
# clinical_model = joblib.load('checkpoints/clinical_model.pkl')
# dice_train_df = pd.read_pickle('checkpoints/train_data.pkl')

# class ClinicalInput(BaseModel):
#     age: float
#     sex: float
#     cp: float
#     trestbps: float
#     chol: float
#     fbs: float
#     restecg: float
#     thalach: float
#     exang: float
#     oldpeak: float
#     ca: float
#     thal: float
#     slope: float

# # @app.post("/predict_clinical")
# # async def predict_clinical(data: ClinicalInput):
# #     try:
# #         input_dict = data.model_dump()
# #         correct_order = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'ca', 'thal', 'slope']
        
# #         raw_values = np.array([[float(input_dict[k]) for k in correct_order]], dtype=np.float32)
# #         df = pd.DataFrame(raw_values, columns=correct_order).astype(np.float32)

# #         dice_df_clean = dice_train_df[correct_order + ['target']].apply(pd.to_numeric, errors='coerce').dropna().astype(np.float32)

# #         prob = clinical_model.predict_proba(df)[0][1]
# #         prediction = int(clinical_model.predict(df)[0])

# #         xgb_comp = clinical_model.named_estimators_['xgb']
# #         explainer = shap.TreeExplainer(xgb_comp)
        
# #         shap_vals = explainer.shap_values(df.values) 
        
# #         feature_importance = dict(zip(correct_order, shap_vals[0]))
# #         top_drivers_raw = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
# #         top_drivers_readable = [FEATURE_NAMES_DISPLAY.get(d[0], d[0]) for d in top_drivers_raw]

# #         plt.figure(figsize=(20, 3))
# #         df_readable = df.rename(columns=FEATURE_NAMES_DISPLAY)
# #         shap.force_plot(explainer.expected_value, shap_vals[0], df_readable.iloc[0], matplotlib=True, show=False)
# #         shap_img = get_base64_plot()

# #         continuous_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
# #         modifiable_features = ['trestbps', 'chol', 'thalach', 'fbs', 'exang', 'oldpeak']
        
# #         d = dice_ml.Data(dataframe=dice_df_clean, continuous_features=continuous_features, outcome_name='target')
        
# #         class ModelWrapper:
# #             def __init__(self, model): self.model = model
# #             def predict_proba(self, X):
# #                 if isinstance(X, pd.DataFrame):
# #                     return self.model.predict_proba(X.astype(np.float32))
# #                 return self.model.predict_proba(X.astype(np.float32))

# #         m = dice_ml.Model(model=ModelWrapper(clinical_model), backend="sklearn")
# #         exp = dice_ml.Dice(d, m, method="random")
        
# #         target_class = 0 if prediction == 1 else 1
        
# #         # try:
# #         #     dice_exp = exp.generate_counterfactuals(
# #         #         df, 
# #         #         total_CFs=3, 
# #         #         desired_class=target_class,
# #         #         features_to_vary=modifiable_features
# #         #     )
# #         #     dice_data = dice_exp.cf_examples_list[0].final_cfs_df.to_json(orient='records')
# #         # except Exception as e:
# #         #     print(f"DiCE failed: {e}")
# #         #     dice_data = None

# #         dice_data = None
# #         try:
# #             print(f"DEBUG: Input Data Types: {df.dtypes}")
# #             # Create a copy of the training data with clean types
# #             dice_df_clean = dice_train_df[correct_order + ['target']].copy()
# #             for col in dice_df_clean.columns:
# #                 dice_df_clean[col] = pd.to_numeric(dice_df_clean[col], errors='coerce')
# #             dice_df_clean = dice_df_clean.dropna()

# #             d = dice_ml.Data(dataframe=dice_df_clean, continuous_features=continuous_features, outcome_name='target')
# #             m = dice_ml.Model(model=clinical_model, backend="sklearn") # Removed the Wrapper for a moment to test
# #             exp = dice_ml.Dice(d, m, method="random")
            
# #             target_class = 0 if prediction == 1 else 1
            
# #             dice_exp = exp.generate_counterfactuals(
# #                 df, 
# #                 total_CFs=3, 
# #                 desired_class=target_class,
# #                 features_to_vary=modifiable_features
# #             )
            
# #             # Convert to list of dicts safely
# #             raw_cf_df = dice_exp.cf_examples_list[0].final_cfs_df
# #             print(f"DEBUG: DiCE Output Raw: {raw_cf_df.iloc[0].to_dict()}")
            
# #             # THE FIX: Convert the entire dataframe to standard floats immediately
# #             # this clears out any weird numpy objects or bracketed strings
# #             dice_data = raw_cf_df.applymap(lambda x: float(str(x).replace('[','').replace(']','')) if isinstance(x, str) else float(x)).to_dict(orient='records')

# #         except Exception as dice_err:
# #             print(f"CRITICAL: DiCE failed but bypass enabled: {dice_err}")
# #             dice_data = [] # Return empty list so frontend doesn't crash

# #         llm_report = get_llm_advice(prediction, prob, input_dict, top_drivers_readable)

# #         plt.figure(figsize=(10, 5))
# #         sample_data = dice_df_clean[correct_order].sample(n=min(50, len(dice_df_clean)))
# #         sample_shap = explainer.shap_values(sample_data.values)
# #         shap.summary_plot(sample_shap, sample_data.rename(columns=FEATURE_NAMES_DISPLAY), show=False)
# #         summary_img = get_base64_plot()

# #         lime_explainer = lime.lime_tabular.LimeTabularExplainer(
# #             training_data=dice_df_clean[correct_order].values,
# #             feature_names=[FEATURE_NAMES_DISPLAY.get(c, c) for c in correct_order],
# #             mode='classification'
# #         )
# #         predict_fn = lambda x: clinical_model.predict_proba(pd.DataFrame(x, columns=correct_order).astype(np.float32))
# #         exp_lime = lime_explainer.explain_instance(df.values[0], predict_fn, num_features=8)
# #         lime_img = get_base64_plot(exp_lime.as_pyplot_figure())

# #         return {
# #             "prediction": prediction,
# #             "probability": float(prob),
# #             "shap_plot": f"data:image/png;base64,{shap_img}",
# #             "shap_explanation": get_shap_explanation(top_drivers_readable, shap_vals[0].tolist()),
# #             "lime_plot": f"data:image/png;base64,{lime_img}",
# #             "lime_explanation": get_lime_explanation(exp_lime.as_list()),
# #             "summary_plot": f"data:image/png;base64,{summary_img}",
# #             # "summary_explanation" : get_summary_explanation(top_drivers_readable),
# #             "dice_data": dice_data,
# #             "dice_explanation": get_dice_explanation(dice_data, prediction),
# #             "llm_report": llm_report
# #         }

# #     except Exception as e:
# #         import traceback
# #         print(traceback.format_exc()) 
# #         return {"error": str(e)}
# # @app.post("/predict_clinical")
# # async def predict_clinical(data: ClinicalInput):
# #     try:
# #         input_dict = data.model_dump()
# #         correct_order = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'ca', 'thal', 'slope']
        
# #         # Prepare input
# #         raw_values = np.array([[float(input_dict[k]) for k in correct_order]], dtype=np.float32)
# #         df = pd.DataFrame(raw_values, columns=correct_order).astype(np.float32)

# #         # Basic Prediction
# #         prob = float(clinical_model.predict_proba(df)[0][1])
# #         prediction = int(clinical_model.predict(df)[0])
# @app.post("/predict_clinical")
# async def predict_clinical(data: ClinicalInput):
#     try:
#         input_dict = data.model_dump()
#         correct_order = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'ca', 'thal', 'slope']
                
#         raw_values = np.array([[float(input_dict[k]) for k in correct_order]], dtype=np.float32)
#         df = pd.DataFrame(raw_values, columns=correct_order).astype(np.float32)
        
#         # FIX 1: Robust Probability Extraction
#         raw_prob = clinical_model.predict_proba(df)[0][1]
#         # Clean the probability if it's trapped in a string/list
#         prob = float(str(raw_prob).replace('[', '').replace(']', ''))
        
#         prediction = int(clinical_model.predict(df)[0])

#         # SHAP Analysis
#         xgb_comp = clinical_model.named_estimators_['xgb']
#         explainer = shap.TreeExplainer(xgb_comp)
#         shap_vals = explainer.shap_values(df.values) 
        
#         feature_importance = dict(zip(correct_order, shap_vals[0]))
#         top_drivers_raw = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
#         top_drivers_readable = [FEATURE_NAMES_DISPLAY.get(d[0], d[0]) for d in top_drivers_raw]

#         # SHAP Plot
#         plt.figure(figsize=(20, 3))
#         shap.force_plot(explainer.expected_value, shap_vals[0], df.iloc[0], matplotlib=True, show=False)
#         shap_img = get_base64_plot()

#         # --- ROBUST DICE SECTION ---
#         dice_data = []
#         # try:
#         #     continuous_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
#         #     modifiable_features = ['trestbps', 'chol', 'thalach', 'fbs', 'exang', 'oldpeak']
            
#         #     # Clean training data for DiCE
#         #     dice_df_clean = dice_train_df[correct_order + ['target']].copy()
#         #     for col in dice_df_clean.columns:
#         #         dice_df_clean[col] = pd.to_numeric(dice_df_clean[col], errors='coerce')
#         #     dice_df_clean = dice_df_clean.dropna().astype(np.float32)

#         #     d = dice_ml.Data(dataframe=dice_df_clean, continuous_features=continuous_features, outcome_name='target')
#         #     m = dice_ml.Model(model=clinical_model, backend="sklearn")
#         #     exp = dice_ml.Dice(d, m, method="random")
            
#         #     target_class = 0 if prediction == 1 else 1
#         #     dice_exp = exp.generate_counterfactuals(
#         #         df, total_CFs=3, desired_class=target_class,
#         #         features_to_vary=modifiable_features
#         #     )
            
#         #     # THE CRITICAL CLEANING STEP
#         #     raw_cf_df = dice_exp.cf_examples_list[0].final_cfs_df.copy()
            
#         #     def scrub_value(val):
#         #         """Removes brackets and handles list-type strings like [0.49]"""
#         #         s = str(val).replace('[', '').replace(']', '').replace("'", "").strip()
#         #         try:
#         #             return float(s)
#         #         except:
#         #             return 0.0

#         #     # Apply cleaning to every cell to ensure no bracketed strings remain
#         #     cleaned_cf_df = raw_cf_df.applymap(scrub_value)
            
#         #     # If a 'target' column exists and it's still weird, just drop it
#         #     if 'target' in cleaned_cf_df.columns:
#         #         cleaned_cf_df = cleaned_cf_df.drop(columns=['target'])
                
#         #     dice_data = cleaned_cf_df.to_dict(orient='records')

#         # except Exception as dice_err:
#         #     print(f"DiCE handled error: {dice_err}")
#         #     dice_data = []
#         try:
#             dice_exp = exp.generate_counterfactuals(
#                 df, 
#                 total_CFs=3, 
#                 desired_class=target_class,
#                 features_to_vary=modifiable_features
#             )
#             cf_df = dice_exp.cf_examples_list[0].final_cfs_df.copy()
            
#             for col in cf_df.columns:
#                 cf_df[col] = cf_df[col].apply(
#                     lambda x: float(str(x).replace('[', '').replace(']', '').replace("'", "")) 
#                     if not isinstance(x, (int, float, np.number)) else x
#                 )
#             dice_data = cf_df.to_dict(orient='records')
#         except Exception as dice_err:
#             print(f"DiCE Error: {dice_err}")
#             dice_data = [] # Fallback to empty list instead of None

#         # LLM, Summary, and LIME (keep your existing logic for these)
#         llm_report = get_llm_advice(prediction, prob, input_dict, top_drivers_readable)
        
#         plt.figure(figsize=(10, 5))
#         sample_data = dice_df_clean[correct_order].sample(n=min(50, len(dice_df_clean)))
#         sample_shap = explainer.shap_values(sample_data.values)
#         shap.summary_plot(sample_shap, sample_data.rename(columns=FEATURE_NAMES_DISPLAY), show=False)
#         summary_img = get_base64_plot()

#         lime_explainer = lime.lime_tabular.LimeTabularExplainer(
#             training_data=dice_df_clean[correct_order].values,
#             feature_names=[FEATURE_NAMES_DISPLAY.get(c, c) for c in correct_order],
#             mode='classification'
#         )
#         predict_fn = lambda x: clinical_model.predict_proba(pd.DataFrame(x, columns=correct_order).astype(np.float32))
#         exp_lime = lime_explainer.explain_instance(df.values[0], predict_fn, num_features=8)
#         lime_img = get_base64_plot(exp_lime.as_pyplot_figure())

#         return {
#             "prediction": prediction,
#             "probability": prob,
#             "shap_plot": f"data:image/png;base64,{shap_img}",
#             "shap_explanation": get_shap_explanation(top_drivers_readable, shap_vals[0].tolist()),
#             "lime_plot": f"data:image/png;base64,{lime_img}",
#             "lime_explanation": get_lime_explanation(exp_lime.as_list()),
#             "summary_plot": f"data:image/png;base64,{summary_img}",
#             "dice_data": dice_data,
#             "dice_explanation": get_dice_explanation(dice_data, prediction),
#             "llm_report": llm_report
#         }

#     except Exception as e:
#         import traceback
#         error_msg = traceback.format_exc()
#         print(error_msg) 
#         return {"error": str(e)} 

# def get_llm_advice(prediction, probability, input_data, top_risk_drivers):
#     """Generates a comprehensive, SHAP-anchored health report."""
    
#     status = "Increased Risk" if prediction == 1 else "Low Risk / Healthy"
    
#     drivers_text = ", ".join(top_risk_drivers)
#     full_context = ", ".join([f"{FEATURE_NAMES_DISPLAY.get(k, k)}: {v}" for k, v in input_data.items()])

#     system_prompt = f"""You are a health coach who simplifies complex SHAP and clinical data into lifestyle advice. Also, consider that the AI flagged {drivers_text} as the main concerns for their {probability*100:.1f}% risk score."""

#     prompt = f"""
#     You are an empathetic, world-class Cardiac Health Coach. 
#     A patient screening shows: {status} ({probability*100:.1f}% risk).
    
#     CRITICAL ANALYSIS:
#     Our Machine Learning model (SHAP analysis) has identified that the following 3 factors are the primary reasons for this patient's risk score: {drivers_text}.

#     PATIENT DATA:
#     {full_context}

#     TASK:
#     Write a comprehensive "Lifestyle Action Plan." 
#     Address the top 3 drivers ({drivers_text}) specifically. 
#     IMPORTANT: No medical jargon. Interpret 'ST Depression' as 'Heart Stress Recovery' and 'Fluoroscopy' as 'Vessel Clarity'.

#     STRUCTURE (MARKDOWN):

#     **[Disclaimer]** "NOTE: This report is generated by AI based on clinical data. It is NOT a medical diagnosis. Please consult a cardiologist."

#     ### ⚠️ Specific Symptoms to Watch
#     List 4 physical sensations to monitor, tailored to their data.

#     ### 🥗 Targeted Nutritional Guide
#     * **Focus Areas**: Provide 4 food items that specifically help improve {drivers_text}.
#     * **Items to Avoid**: Provide 4 items that worsen {drivers_text}.

#     ### 🏃 Moving Safely
#     Based on their Age and Max Heart Rate, suggest a specific exercise intensity.

#     ### ✅ 3 Simple Steps for Tomorrow
#     Actionable tasks to specifically address {top_risk_drivers[0]}.
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7,
#             # max_tokens=500
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         return "Advice currently unavailable. Please review the clinical charts."

# def get_shap_explanation(drivers, shap_values):
#     system_prompt = "You are a Clinical Diagnostic Consultant. Provide concise, evidence-based interpretations of SHAP global/local feature impacts. Avoid conversational filler."
    
#     prompt = f"""
#     ### CLINICAL DATA OVERVIEW
#     Global Risk Drivers: {drivers}
#     Specific SHAP Values: {shap_values}

#     ### TASK
#     Interpret the Global Feature Impact for this patient. 
#     1. Relate the primary drivers ({drivers}) to established cardiovascular risk factors.
#     2. Explain the 'Global vs. Local' alignment: Does this patient's risk profile follow standard population trends or show unique outliers?
    
#     FORMAT: Use a structured bulleted list. 
#     """
#     response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}])
#     return response.choices[0].message.content

# def get_lime_explanation(lime_data):
#     system_prompt = "You are a Senior Cardiologist. Interpret LIME (Local Interpretable Model-agnostic Explanations) for a peer physician."
    
#     prompt = f"""
#     ### LOCAL FEATURE DEVIATION
#     Patient-Specific Weights: {lime_data}

#     ### TASK
#     Analyze why the model weighted these specific variables for *this* prediction.
#     1. Identify the 'Highest Impact' local variables.
#     2. Correlate these variables to the patient's acute presentation (e.g., how specific ST/Slope changes influenced this individual decision).
    
#     FORMAT: Short, professional paragraphs. Use 'Clinical Correlation' as a header.
#     """
#     response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}])
#     return response.choices[0].message.content

# # def get_summary_explanation(drivers):
# #     prompt = f"""
# #     Act as a Senior Clinical Researcher. 
# #     Interpret this SHAP Summary Plot data for a cardiology team.
# #     The most globally influential features across the entire population are: {drivers}.
    
# #     Explain:
# #     1. Why these specific features (like Age, CP, or Thalach) are the strongest predictors for this model.
# #     2. How a clinician should use this 'Global view' to validate the reliability of the AI's logic compared to standard cardiology guidelines (e.g., AHA/ACC).
# #     """
# #     response = client.chat.completions.create(
# #         model="gpt-4o-mini",
# #         messages=[{"role": "user", "content": prompt}]
# #     )
# #     return response.choices[0].message.content

# def get_dice_explanation(dice_scenarios, prediction):
#     # Determine the "Direction" of the counterfactuals
#     is_high_risk = int(prediction) == 1
    
#     direction_title = "RISK MITIGATION ANALYSIS" if is_high_risk else "PROGNOSTIC VULNERABILITY ANALYSIS"
    
#     goal_state = "Healthy (Low Risk)" if is_high_risk else "High Risk (Diseased)"
    
#     system_prompt = "You are a Clinical Strategist. You specialize in interpreting Counterfactual Explanations to determine clinical thresholds."

#     prompt = f"""
#     ### {direction_title}
#     TARGET GOAL: Transition patient to {goal_state} state.
#     RAW COUNTERFACTUAL DATA: {dice_scenarios}

#     ### TASK
#     Analyze the 'Delta' (the difference) between the patient's current clinical state and the 3 generated scenarios.

#     1. **Key Thresholds**: For the patient to be classified as {goal_state}, identify the specific thresholds reached in the scenarios (e.g., 'Cholesterol must drop below 200mg/dl' or 'Max Heart Rate must exceed 150bpm').
#     2. **Sensitivity Analysis**: Which single variable change caused the most significant shift in the model's prediction? 
#     3. **Clinical Feasibility**: Briefly comment on the physiological significance of these changes (e.g., 'The model suggests a high sensitivity to Resting BP, indicating hypertensive management is the priority').

#     { "FOCUS: Focus on how reducing these metrics improves cardiac outlook." if is_high_risk else "FOCUS: Identify these as 'danger zones'—if the patient's metrics drift to these levels, their risk status will flip to High Risk." }

#     **[Note]** These are algorithmic simulations (DiCE).
#     FORMAT: Use concise clinical bullet points. No conversational 'AI' filler.
#     """
    
#     response = client.chat.completions.create(
#         model="gpt-4o-mini", 
#         messages=[
#             {"role": "system", "content": system_prompt}, 
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.3 
#     )
#     return response.choices[0].message.content

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="127.0.0.1", port=8000)
# # if __name__ == "__main__":
# #     import uvicorn
# #     import os
# #     port = int(os.environ.get("PORT", 10000))
# #     uvicorn.run(app, host="0.0.0.0", port=port)
# if __name__ == "__main__":
#     import uvicorn
#     import os
#     uvicorn.run(app, host="0.0.0.0", port=7860)
import torch
import io
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from model_utils import HierarchicalECGModel
from processor import process_ecg_signal  
import base64
from xai_helper import generate_heatmaps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib
import pandas as pd
import dice_ml
import shap
import lime
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()      

client = OpenAI()

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = HierarchicalECGModel().to(device)
# checkpoint = torch.load('checkpoints/best_hierarchical_model.pth', map_location=device)
# model.load_state_dict(checkpoint['model_state_dict'])
# model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
n_splits = 5
fold_models = []

for i in range(n_splits):
    model = HierarchicalECGModel().to(device)
    model.load_state_dict(
        torch.load(f'checkpoints/model_fold_{i+1}.pth', map_location=device)
    )
    model.eval()
    fold_models.append(model)


def safe_float(x):
    try:
        if isinstance(x, (list, tuple, np.ndarray)):
            return float(x[0])
        if isinstance(x, str):
            return float(x.replace('[','').replace(']',''))
        return float(x)
    except:
        return 0.0


@app.get("/")
def read_root():
    return {"message": "CardioXAI API is running"}

def encode_img(img):
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        data = await file.read()
        image = Image.open(io.BytesIO(data)).convert('RGB')
        img_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        processed_img = process_ecg_signal(img_cv2)
        
        # img_t = torch.from_numpy(processed_img).float().permute(2, 0, 1) / 255.0
        # mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        # std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        # img_t = (img_t - mean) / std
        img_t = torch.from_numpy(processed_img).float().permute(2, 0, 1) / 255.0
        mean = torch.tensor([0.5, 0.5, 0.5]).view(3, 1, 1)
        std = torch.tensor([0.5, 0.5, 0.5]).view(3, 1, 1)
        img_t = (img_t - mean) / std
        input_tensor = img_t.unsqueeze(0).to(device)
        
        # with torch.no_grad():
        #     out1, out2 = model(input_tensor)
        #     prob1 = torch.sigmoid(out1).item()
        #     if prob1 > 0.5:
        #         l1_label = "Myocardial"
        #         display_confidence = prob1  
        #     else:
        #         l1_label = "Other Cardiac Conditions"
        #         display_confidence = 1 - prob1 
        #     l2_idx = torch.argmax(out2, dim=1).item()
        #     l2_classes = ['Normal', 'Abnormal Heartbeat', 'History of MI', 'Acute MI']
        #     l2_label = l2_classes[l2_idx]
        ensemble_out1 = []
        ensemble_out2 = []

        with torch.no_grad():
            for model in fold_models:
                o1, o2 = model(input_tensor)
                ensemble_out1.append(torch.sigmoid(o1).cpu().numpy())
                ensemble_out2.append(torch.softmax(o2, dim=1).cpu().numpy())
        avg_l1_prob = np.mean(np.array(ensemble_out1))
        avg_l2_probs = np.mean(np.array(ensemble_out2), axis=0)
        l1_label = "Myocardial Infarction" if avg_l1_prob > 0.5 else "Other Cardiac Conditions"
        display_confidence = avg_l1_prob if avg_l1_prob > 0.5 else 1 - avg_l1_prob
        l2_idx = np.argmax(avg_l2_probs)
        l2_classes = ['Normal', 'Abnormal', 'History of MI', 'Acute MI']
        l2_label = l2_classes[l2_idx]
        # rgb_for_xai = processed_img.astype(np.float32) / 255.0
        # vis_l1, vis_l2 = generate_heatmaps(model, input_tensor, rgb_for_xai)
        rgb_for_xai = processed_img.astype(np.float32) / 255.0
        vis_l1, vis_l2 = generate_heatmaps(fold_models[0], input_tensor, rgb_for_xai)

        return {
            "level1_prediction": l1_label,
            "level1_confidence": f"{display_confidence:.4f}",
            "level2_prediction": l2_label,
            "heatmap_l1": f"data:image/jpeg;base64,{encode_img(vis_l1)}",
            "heatmap_l2": f"data:image/jpeg;base64,{encode_img(vis_l2)}"
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc()) 
        return {"error": str(e)}

def get_base64_plot(fig=None):
    buf = io.BytesIO()
    if fig:
        fig.savefig(buf, format='png', bbox_inches='tight')
    else:
        plt.savefig(buf, format='png', bbox_inches='tight')
    
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close('all')  
    return img_str

FEATURE_NAMES_DISPLAY = {
    'age': 'Age', 
    'sex': 'Gender', 
    'cp': 'Chest Pain Type', 
    'trestbps': 'Resting BP (mmHg)', 
    'chol': 'Cholesterol (mg/dl)', 
    'fbs': 'Fasting Sugar > 120', 
    'restecg': 'Resting ECG', 
    'thalach': 'Max Heart Rate', 
    'exang': 'Exercise Angina', 
    'oldpeak': 'ST Depression', 
    'ca': 'Major Vessels', 
    'thal': 'Thallium Stress', 
    'slope': 'ST Slope'
}

INTERNAL_MAPPING = {
    "cp": {"typical angina": 0.0, "atypical angina": 1.0, "non-anginal": 2.0, "asymptomatic": 3.0},
    "restecg": {"normal": 0.0, "stt abnormality": 1.0, "lv hypertrophy": 2.0},
    "slope": {"upsloping": 0.0, "flat": 1.0, "downsloping": 2.0},
    "thal": {"normal": 1.0, "fixed defect": 2.0, "reversible defect": 3.0}
}

clinical_model = joblib.load('checkpoints/clinical_model.pkl')
dice_train_df = pd.read_pickle('checkpoints/train_data.pkl')
print(dice_train_df.dtypes)

class ClinicalInput(BaseModel):
    age: float
    sex: float
    cp: float
    trestbps: float
    chol: float
    fbs: float
    restecg: float
    thalach: float
    exang: float
    oldpeak: float
    ca: float
    thal: float
    slope: float

@app.post("/predict_clinical")
async def predict_clinical(data: ClinicalInput):
    try:
        input_dict = data.model_dump()
        correct_order = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'ca', 'thal', 'slope']
        
        raw_values = np.array([[float(input_dict[k]) for k in correct_order]], dtype=np.float32)
        # df = pd.DataFrame(raw_values, columns=correct_order).astype(np.float32)
        df = pd.DataFrame(raw_values, columns=correct_order)
        df = df.applymap(safe_float).astype(np.float32)

        dice_df_clean = dice_train_df[correct_order + ['target']].apply(pd.to_numeric, errors='coerce').dropna().astype(np.float32)

        # prob = clinical_model.predict_proba(df)[0][1]
        # raw_prob = clinical_model.predict_proba(df)[0][1]
        # prob = safe_float(raw_prob)
        # prediction = int(clinical_model.predict(df)[0])
        print("DEBUG: DF dtypes")
        print(df.dtypes)
        print("DEBUG: DF head")
        print(df.head())

        proba = clinical_model.predict_proba(df)
        proba_raw = clinical_model.predict_proba(df)
        print("DEBUG: raw predict_proba output")
        print(proba_raw, type(proba_raw), proba_raw.dtype)
        proba = np.vectorize(safe_float)(proba)

        prob = float(proba[0][1])
        prediction = int(np.argmax(proba[0]))

        # xgb_comp = clinical_model.named_estimators_['xgb']
        # try:
        #     base_score = xgb_comp.get_booster().attr("base_score")
        #     if base_score is not None and "[" in str(base_score):
        #         clean_score = str(base_score).replace('[', '').replace(']', '')
        #         xgb_comp.get_booster().set_attr(base_score=clean_score)
        # except Exception as e:
        #     print(f"SHAP Hotfix failed (safe to ignore if SHAP works): {e}")
        # explainer = shap.TreeExplainer(xgb_comp)
        
        # shap_vals = explainer.shap_values(df.values) 

        # xgb_comp = clinical_model.named_estimators_['xgb']
        # predict_fn = lambda x: xgb_comp.predict_proba(pd.DataFrame(x, columns=correct_order).astype(np.float32))

        # try:
        #     b_score = xgb_comp.get_booster().attr("base_score")
        #     if b_score and "[" in str(b_score):
        #         clean_score = str(b_score).replace('[', '').replace(']', '')
        #         xgb_comp.get_booster().set_attr(base_score=clean_score)
            
        #     explainer = shap.TreeExplainer(xgb_comp)
        #     shap_vals = explainer.shap_values(df.values)
        # except Exception as e:
        #     print(f"TreeExplainer failed, using KernelExplainer with Lambda: {e}")
        #     background_summary = shap.kmeans(dice_df_clean[correct_order], 5) # Summarize background for speed
        #     explainer = shap.KernelExplainer(predict_fn, background_summary)
        #     shap_vals = explainer.shap_values(df.values)

        # if isinstance(shap_vals, list):
        #     current_shap_vals = shap_vals[prediction]
        #     expected_val = explainer.expected_value[prediction]
        # else:
        #     current_shap_vals = shap_vals
        #     expected_val = explainer.expected_value
        # if len(current_shap_vals.shape) > 1:
        #     current_shap_vals = current_shap_vals[0]
        
        # # feature_importance = dict(zip(correct_order, shap_vals[0]))
        # feature_importance = {
        #     f: safe_float(shap_vals[0][i])
        #     for i, f in enumerate(correct_order)
        # }

        # top_drivers_raw = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        # top_drivers_readable = [FEATURE_NAMES_DISPLAY.get(d[0], d[0]) for d in top_drivers_raw]

        # # plt.figure(figsize=(20, 3))
        # # df_readable = df.rename(columns=FEATURE_NAMES_DISPLAY)
        # # # shap.force_plot(explainer.expected_value, shap_vals[0], df_readable.iloc[0], matplotlib=True, show=False)
        # # shap.force_plot(expected_val, current_shap_vals, df_readable.iloc[0], matplotlib=True, show=False)
        # # shap_img = get_base64_plot()
        # # --- SHAP PLOTTING (EXTREMELY ROBUST VERSION) ---
        # plt.figure(figsize=(20, 3))
        # df_readable = df.rename(columns=FEATURE_NAMES_DISPLAY)

        # # 1. Force expected_val to be a raw scalar no matter what
        # # This handles cases where it's [val], [[val]], or a numpy array
        # clean_expected_val = np.array(expected_val).item() if hasattr(expected_val, "__len__") else expected_val
        
        # # 2. Force shap values to be a flat 1D array
        # clean_shap_vals = np.array(current_shap_vals).flatten()

        # shap.force_plot(
        #     float(clean_expected_val), 
        #     clean_shap_vals, 
        #     df_readable.iloc[0], 
        #     matplotlib=True, 
        #     show=False
        # )
        # shap_img = get_base64_plot()
# --- SHAP CALCULATION (FIXED FOR 26 FEATURE ERROR) ---
        xgb_comp = clinical_model.named_estimators_['xgb']
        model_features = xgb_comp.get_booster().feature_names
        df_aligned = df.reindex(columns=model_features).astype(np.float32)

        try:
            # Fix XGBoost base_score bug
            b_score = xgb_comp.get_booster().attr("base_score")
            if b_score and "[" in str(b_score):
                clean_score = str(b_score).replace('[', '').replace(']', '')
                xgb_comp.get_booster().set_attr(base_score=clean_score)
            
            explainer = shap.TreeExplainer(xgb_comp)
            raw_shap_vals = explainer.shap_values(df_aligned) 
        except Exception as e:
            print(f"TreeExplainer failed: {e}")
            background_summary = shap.kmeans(dice_df_clean[model_features], 5)
            explainer = shap.KernelExplainer(clinical_model.predict_proba, background_summary)
            raw_shap_vals = explainer.shap_values(df_aligned)

        # --- THE FIX FOR THE 26 vs 13 MISMATCH ---
        # If raw_shap_vals is a list (size 2), pick the one for the current prediction
        if isinstance(raw_shap_vals, list):
            current_shap_vals = np.array(raw_shap_vals[prediction]).flatten()
            expected_val = explainer.expected_value[prediction]
        # If it's a 3D array [samples, features, classes], index the last dimension
        elif len(raw_shap_vals.shape) == 3:
            current_shap_vals = raw_shap_vals[0, :, prediction].flatten()
            expected_val = explainer.expected_value[prediction]
        else:
            current_shap_vals = np.array(raw_shap_vals).flatten()
            expected_val = explainer.expected_value

        # Double check the length matches the 13 features
        if len(current_shap_vals) != len(model_features):
            # Fallback: if it's still 26, just take the second half (usually class 1)
            if len(current_shap_vals) == 2 * len(model_features):
                current_shap_vals = current_shap_vals[len(model_features):]
            else:
                raise ValueError(f"Feature mismatch! Model expects {len(model_features)} but got {len(current_shap_vals)}")

        # Clean expected_val for plotting
        clean_expected_val = float(np.array(expected_val).item()) if hasattr(expected_val, "__len__") else float(expected_val)

        # --- FEATURE IMPORTANCE (For top_drivers_readable) ---
        feature_importance = {
            f: float(current_shap_vals[i])
            for i, f in enumerate(model_features)
        }
        top_drivers_raw = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        top_drivers_readable = [FEATURE_NAMES_DISPLAY.get(d[0], d[0]) for d in top_drivers_raw]

        # --- PLOTTING ---
        plt.figure(figsize=(20, 3))
        df_readable = df_aligned.rename(columns=FEATURE_NAMES_DISPLAY)

        shap.force_plot(
            clean_expected_val, 
            current_shap_vals, 
            df_readable.iloc[0], 
            matplotlib=True, 
            show=False
        )
        shap_img = get_base64_plot()

        continuous_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
        modifiable_features = ['trestbps', 'chol', 'thalach', 'fbs', 'exang', 'oldpeak']
        
        d = dice_ml.Data(dataframe=dice_df_clean, continuous_features=continuous_features, outcome_name='target')
        
        # class ModelWrapper:
        #     def __init__(self, model): self.model = model
        #     def predict_proba(self, X):
        #         if isinstance(X, pd.DataFrame):
        #             return self.model.predict_proba(X.astype(np.float32))
        #         return self.model.predict_proba(X.astype(np.float32))

        # m = dice_ml.Model(model=ModelWrapper(clinical_model), backend="sklearn")
        # exp = dice_ml.Dice(d, m, method="random")
        
        # target_class = 0 if prediction == 1 else 1
        
        # try:
        #     dice_exp = exp.generate_counterfactuals(
        #         df, 
        #         total_CFs=3, 
        #         desired_class=target_class,
        #         features_to_vary=modifiable_features
        #     )
        #     dice_data = dice_exp.cf_examples_list[0].final_cfs_df.to_json(orient='records')
        # except Exception as e:
        #     print(f"DiCE failed: {e}")
        #     dice_data = None
        # class ModelWrapper:
        #     def __init__(self, model): 
        #         self.model = model
        #     def predict_proba(self, X):
        #         if isinstance(X, pd.DataFrame):
        #             X = X.astype(np.float32)
        #         probs = self.model.predict_proba(X)
        #         return np.array(probs, dtype=np.float64)
            
        #     def predict(self, X):
        #         if isinstance(X, pd.DataFrame):
        #             X = X.astype(np.float32)
        #         return self.model.predict(X)
        class ModelWrapper:
            def __init__(self, model):
                self.model = model
                self._estimator_type = "classifier"
                self.classes_ = np.array([0, 1])

            def predict_proba(self, X):
                if isinstance(X, np.ndarray):
                    X = pd.DataFrame(X, columns=correct_order)
                return self.model.predict_proba(X.astype(np.float32))

            def predict(self, X):
                if isinstance(X, np.ndarray):
                    X = pd.DataFrame(X, columns=correct_order)
                return self.model.predict(X.astype(np.float32))


        m = dice_ml.Model(model=ModelWrapper(clinical_model), backend="sklearn")
        exp = dice_ml.Dice(d, m, method="random")
        target_class = 0 if prediction == 1 else 1
        try:
            dice_exp = exp.generate_counterfactuals(
                df, 
                total_CFs=3, 
                desired_class=target_class,
                features_to_vary=modifiable_features
            )
            # cf_df = dice_exp.cf_examples_list[0].final_cfs_df
            # for col in cf_df.columns:
            #     cf_df[col] = pd.to_numeric(cf_df[col].to_numpy().flatten(), errors='coerce')
            # dice_data = cf_df.to_dict(orient='records')
            cf_df = dice_exp.cf_examples_list[0].final_cfs_df.copy()
            for col in cf_df.columns:
                cf_df[col] = cf_df[col].apply(safe_float)
            dice_data = cf_df.to_dict(orient="records")
        except Exception as e:
            print(f"DiCE failed: {e}")
            dice_data = "EMPTY" 
        llm_report = get_llm_advice(prediction, prob, input_dict, top_drivers_readable)

        # plt.figure(figsize=(10, 5))
        # sample_data = dice_df_clean[correct_order].sample(n=min(50, len(dice_df_clean)))
        # sample_shap = explainer.shap_values(sample_data.values)
        # shap.summary_plot(sample_shap, sample_data.rename(columns=FEATURE_NAMES_DISPLAY), show=False)
        # summary_img = get_base64_plot()
        plt.figure(figsize=(10, 5))
        sample_size = min(50, len(dice_df_clean))
        sample_data = dice_df_clean[correct_order].sample(n=sample_size)
        raw_sample_shap = explainer.shap_values(sample_data.values)        
        if isinstance(raw_sample_shap, list):
            display_sample_shap = raw_sample_shap[prediction]
        else:
            display_sample_shap = raw_sample_shap
        shap.summary_plot(
            display_sample_shap, 
            sample_data.rename(columns=FEATURE_NAMES_DISPLAY), 
            show=False
        )
        summary_img = get_base64_plot()

        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=dice_df_clean[correct_order].values,
            feature_names=[FEATURE_NAMES_DISPLAY.get(c, c) for c in correct_order],
            mode='classification'
        )
        predict_fn = lambda x: clinical_model.predict_proba(pd.DataFrame(x, columns=correct_order).astype(np.float32))
        exp_lime = lime_explainer.explain_instance(df.values[0], predict_fn, num_features=8)
        lime_img = get_base64_plot(exp_lime.as_pyplot_figure())

        return {
            "prediction": prediction,
            "probability": float(prob),
            "shap_plot": f"data:image/png;base64,{shap_img}",
            "shap_explanation": get_shap_explanation(top_drivers_readable, current_shap_vals.tolist()),
            # "shap_explanation": get_shap_explanation(top_drivers_readable, shap_vals[0].tolist()),
            "lime_plot": f"data:image/png;base64,{lime_img}",
            "lime_explanation": get_lime_explanation(exp_lime.as_list()),
            "summary_plot": f"data:image/png;base64,{summary_img}",
            # "summary_explanation" : get_summary_explanation(top_drivers_readable),
            "dice_data": dice_data,
            "dice_explanation": get_dice_explanation(dice_data, prediction),
            "llm_report": llm_report
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc()) 
        return {"error": str(e)}

def get_llm_advice(prediction, probability, input_data, top_risk_drivers):
    """Generates a comprehensive, SHAP-anchored health report."""
    
    status = "Increased Risk" if prediction == 1 else "Low Risk / Healthy"
    
    drivers_text = ", ".join(top_risk_drivers)
    full_context = ", ".join([f"{FEATURE_NAMES_DISPLAY.get(k, k)}: {v}" for k, v in input_data.items()])

    system_prompt = f"""You are a health coach who simplifies complex SHAP and clinical data into lifestyle advice. Also, consider that the AI flagged {drivers_text} as the main concerns for their {probability*100:.1f}% risk score."""

    prompt = f"""
    You are an empathetic, world-class Cardiac Health Coach. 
    A patient screening shows: {status} ({probability*100:.1f}% risk).
    
    CRITICAL ANALYSIS:
    Our Machine Learning model (SHAP analysis) has identified that the following 3 factors are the primary reasons for this patient's risk score: {drivers_text}.

    PATIENT DATA:
    {full_context}

    TASK:
    Write a comprehensive "Lifestyle Action Plan." 
    Address the top 3 drivers ({drivers_text}) specifically. 
    IMPORTANT: No medical jargon. Interpret 'ST Depression' as 'Heart Stress Recovery' and 'Fluoroscopy' as 'Vessel Clarity'.

    STRUCTURE (MARKDOWN):

    **[Disclaimer]** "NOTE: This report is generated by AI based on clinical data. It is NOT a medical diagnosis. Please consult a cardiologist."

    ### ⚠️ Specific Symptoms to Watch
    List 4 physical sensations to monitor, tailored to their data.

    ### 🥗 Targeted Nutritional Guide
    * **Focus Areas**: Provide 4 food items that specifically help improve {drivers_text}.
    * **Items to Avoid**: Provide 4 items that worsen {drivers_text}.

    ### 🏃 Moving Safely
    Based on their Age and Max Heart Rate, suggest a specific exercise intensity.

    ### ✅ 3 Simple Steps for Tomorrow
    Actionable tasks to specifically address {top_risk_drivers[0]}.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            # max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Advice currently unavailable. Please review the clinical charts."

def get_shap_explanation(drivers, shap_values):
    system_prompt = "You are a Clinical Diagnostic Consultant. Provide concise, evidence-based interpretations of SHAP global/local feature impacts. Avoid conversational filler."
    
    prompt = f"""
    ### CLINICAL DATA OVERVIEW
    Global Risk Drivers: {drivers}
    Specific SHAP Values: {shap_values}

    ### TASK
    Interpret the Global Feature Impact for this patient. 
    1. Relate the primary drivers ({drivers}) to established cardiovascular risk factors.
    2. Explain the 'Global vs. Local' alignment: Does this patient's risk profile follow standard population trends or show unique outliers?
    
    FORMAT: Use a structured bulleted list. 
    """
    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}])
    return response.choices[0].message.content

def get_lime_explanation(lime_data):
    system_prompt = "You are a Senior Cardiologist. Interpret LIME (Local Interpretable Model-agnostic Explanations) for a peer physician."
    
    prompt = f"""
    ### LOCAL FEATURE DEVIATION
    Patient-Specific Weights: {lime_data}

    ### TASK
    Analyze why the model weighted these specific variables for *this* prediction.
    1. Identify the 'Highest Impact' local variables.
    2. Correlate these variables to the patient's acute presentation (e.g., how specific ST/Slope changes influenced this individual decision).
    
    FORMAT: Short, professional paragraphs. Use 'Clinical Correlation' as a header.
    """
    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}])
    return response.choices[0].message.content

# def get_summary_explanation(drivers):
#     prompt = f"""
#     Act as a Senior Clinical Researcher. 
#     Interpret this SHAP Summary Plot data for a cardiology team.
#     The most globally influential features across the entire population are: {drivers}.
    
#     Explain:
#     1. Why these specific features (like Age, CP, or Thalach) are the strongest predictors for this model.
#     2. How a clinician should use this 'Global view' to validate the reliability of the AI's logic compared to standard cardiology guidelines (e.g., AHA/ACC).
#     """
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response.choices[0].message.content

def get_dice_explanation(dice_scenarios, prediction):
    # Determine the "Direction" of the counterfactuals
    is_high_risk = int(prediction) == 1
    
    direction_title = "RISK MITIGATION ANALYSIS" if is_high_risk else "PROGNOSTIC VULNERABILITY ANALYSIS"
    
    goal_state = "Healthy (Low Risk)" if is_high_risk else "High Risk (Diseased)"
    
    system_prompt = "You are a Clinical Strategist. You specialize in interpreting Counterfactual Explanations to determine clinical thresholds."

    prompt = f"""
    ### {direction_title}
    TARGET GOAL: Transition patient to {goal_state} state.
    RAW COUNTERFACTUAL DATA: {dice_scenarios}

    ### TASK
    Analyze the 'Delta' (the difference) between the patient's current clinical state and the 3 generated scenarios.

    1. **Key Thresholds**: For the patient to be classified as {goal_state}, identify the specific thresholds reached in the scenarios (e.g., 'Cholesterol must drop below 200mg/dl' or 'Max Heart Rate must exceed 150bpm').
    2. **Sensitivity Analysis**: Which single variable change caused the most significant shift in the model's prediction? 
    3. **Clinical Feasibility**: Briefly comment on the physiological significance of these changes (e.g., 'The model suggests a high sensitivity to Resting BP, indicating hypertensive management is the priority').

    { "FOCUS: Focus on how reducing these metrics improves cardiac outlook." if is_high_risk else "FOCUS: Identify these as 'danger zones'—if the patient's metrics drift to these levels, their risk status will flip to High Risk." }

    **[Note]** These are algorithmic simulations (DiCE).
    FORMAT: Use concise clinical bullet points. No conversational 'AI' filler.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": system_prompt}, 
            {"role": "user", "content": prompt}
        ],
        temperature=0.3 
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0.0", port=7860)