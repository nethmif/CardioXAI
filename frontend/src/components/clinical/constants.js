export const CLINICAL_MAPPING = {
  age: { label: "Age", unit: "years" },
  sex: { label: "Gender", map: { 1: "Male", 0: "Female" } },
  cp: { 
    label: "Chest Pain Type", 
    map: { 0: "Typical Angina", 1: "Atypical Angina", 2: "Non-anginal", 3: "Asymptomatic" } 
  },
  trestbps: { label: "Resting BP", unit: "mm Hg" },
  chol: { label: "Cholesterol", unit: "mg/dl" },
  fbs: { label: "Fasting Blood Sugar", map: { 0: "< 120mg/dl", 1: "> 120mg/dl" } },
  restecg: { 
    label: "Resting ECG", 
    map: { 0: "Normal", 1: "ST-T Abnormality", 2: "LV Hypertrophy" } 
  },
  thalach: { label: "Max Heart Rate", unit: "bpm" },
  exang: { label: "Exercise Angina", map: { 0: "No", 1: "Yes" } },
  oldpeak: { label: "ST Depression", unit: "mm" },
  slope: { label: "ST Slope", map: { 0: "Upsloping", 1: "Flat", 2: "Downsloping" } },
  ca: { label: "Major Vessels", unit: "" },
  thal: { label: "Thallium Stress", map: { 1: "Normal", 2: "Fixed Defect", 3: "Reversible Defect" } },
  target: { label: "Prediction", map: { 0: "Healthy", 1: "Heart Disease" } }
};