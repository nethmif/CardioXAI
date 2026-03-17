import React, { useState } from 'react';
import { Form, Row, Col, Button, Spinner, InputGroup } from 'react-bootstrap';
import axios from 'axios';
import ClinicalResultsView from './ClinicalResultsView';

// const PredictClinical = () => {
const PredictClinical = ({ clinicalData, setClinicalData, hidePredictButton = false, isSideBySide = false}) => {
  const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

  const [formData, setFormData] = useState({
    age: '', sex: '1', cp: '0', trestbps: '', chol: '', fbs: '0',
    restecg: '0', thalach: '', exang: '0', oldpeak: '', slope: '0', ca: '0', thal: '1'
  });
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [validated, setValidated] = useState(false);

  // const handleInputChange = (e) => {
  //   const { name, value } = e.target;
  //   setFormData(prev => ({ ...prev, [name]: value }));
  // };
  const handleInputChange = (e) => {
    const { name, value } = e.target;

    const updated = { ...formData, [name]: value };
    setFormData(updated);

    const numericData = {};
    Object.keys(updated).forEach(k => {
      numericData[k] = Number(updated[k]);
    });

    setClinicalData(numericData);
  };

  const handlePredict = async (e) => {
    const form = e.currentTarget;
    e.preventDefault();
    
    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setLoading(true);
    try {
      const submissionData = {};
      Object.keys(formData).forEach(key => {
        submissionData[key] = Number(formData[key]);
      });
      console.log(submissionData);
      // const res = await axios.post('http://localhost:8000/predict_clinical', submissionData);
      const res = await axios.post(`${API_URL}/predict_clinical`, submissionData);
      console.log("Predict Clinical API URL:", process.env.REACT_APP_API_URL);
      console.log("Predict Clinical res",res.data);
      console.log("end")
      setResult(res.data);
      setClinicalData(submissionData); 
    } catch (err) {
      console.error(err);
      alert("Error: Could not connect to the diagnostic engine.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="clinical-container p-3">
      {!result ? (
        <Form noValidate validated={validated} onSubmit={handlePredict}>
          <h5 className="mb-4 border-bottom pb-2">Patient Clinical Data Entry</h5>
          
          <Row className="g-3">
            {/* Demographic Info */}
            <Col md={4}>
              <Form.Label className="small fw-bold">Age (Years)</Form.Label>
              <Form.Control 
                required type="number" name="age" min="1" max="150"
                placeholder="e.g. 45" onChange={handleInputChange} 
              />
              <Form.Control.Feedback type="invalid">Please enter a valid age (1-150).</Form.Control.Feedback>
            </Col>

            <Col md={4}>
              <Form.Label className="small fw-bold">Gender</Form.Label>
              <Form.Select name="sex" onChange={handleInputChange}>
                <option value="1">Male</option>
                <option value="0">Female</option>
              </Form.Select>
            </Col>

            <Col md={4}>
              <Form.Label className="small fw-bold">Chest Pain Type</Form.Label>
              <Form.Select name="cp" onChange={handleInputChange}>
                <option value="0">Typical Angina</option>
                <option value="1">Atypical Angina</option>
                <option value="2">Non-anginal</option>
                <option value="3">Asymptomatic</option>
              </Form.Select>
            </Col>

            {/* Vital Signs */}
            <Col md={4}>
              <Form.Label className="small fw-bold">Resting BP (mm Hg)</Form.Label>
              <Form.Control 
                required type="number" name="trestbps" min="80" max="250"
                placeholder="e.g. 120" onChange={handleInputChange} 
              />
              <Form.Control.Feedback type="invalid">Enter pressure between 80-250.</Form.Control.Feedback>
            </Col>

            <Col md={4}>
              <Form.Label className="small fw-bold">Serum Cholestrol (mg/dl)</Form.Label>
              <Form.Control 
                required type="number" name="chol" min="100" max="600"
                placeholder="e.g. 200" onChange={handleInputChange} 
              />
              <Form.Control.Feedback type="invalid">Enter value between 100-600.</Form.Control.Feedback>
            </Col>

            <Col md={4}>
              <Form.Label className="small fw-bold">Fasting Blood Sugar {'>'} 120mg/dl</Form.Label>
              <Form.Select name="fbs" onChange={handleInputChange}>
                <option value="0">False (Normal)</option>
                <option value="1">True (Elevated)</option>
              </Form.Select>
            </Col>

            {/* Cardiac Performance */}
            <Col md={6}>
              <Form.Label className="small fw-bold">Resting ECG Results</Form.Label>
              <Form.Select name="restecg" onChange={handleInputChange}>
                <option value="0">Normal</option>
                <option value="1">ST-T Wave Abnormality</option>
                <option value="2">Left Ventricular Hypertrophy</option>
              </Form.Select>
            </Col>

            <Col md={6}>
              <Form.Label className="small fw-bold">Max Heart Rate Achieved</Form.Label>
              <Form.Control 
                required type="number" name="thalach" min="60" max="220"
                placeholder="e.g. 150" onChange={handleInputChange} 
              />
              <Form.Control.Feedback type="invalid">Valid range: 60-220 bpm.</Form.Control.Feedback>
            </Col>

            <Col md={4}>
              <Form.Label className="small fw-bold">Exercise Induced Angina</Form.Label>
              <Form.Select name="exang" onChange={handleInputChange}>
                <option value="0">No</option>
                <option value="1">Yes</option>
              </Form.Select>
            </Col>

            <Col md={4}>
              <Form.Label className="small fw-bold">ST Depression (Oldpeak)</Form.Label>
              <Form.Control 
                required type="number" step="0.1" name="oldpeak" min="0" max="6"
                placeholder="0.0 - 6.0" onChange={handleInputChange} 
              />
              <Form.Control.Feedback type="invalid">Please enter a value between 0 and 6.</Form.Control.Feedback>
            </Col>

            <Col md={4}>
              <Form.Label className="small fw-bold">Peak ST Slope</Form.Label>
              <Form.Select name="slope" onChange={handleInputChange}>
                <option value="0">Upsloping</option>
                <option value="1">Flat Sloping</option>
                <option value="2">Downsloping</option>
              </Form.Select>
            </Col>

            {/* Diagnostic Tests */}
            <Col md={6}>
              <Form.Label className="small fw-bold">Major Vessels (Fluoroscopy)</Form.Label>
              <Form.Select name="ca" onChange={handleInputChange}>
                <option value="0">0 Vessels</option>
                <option value="1">1 Vessel</option>
                <option value="2">2 Vessels</option>
                <option value="3">3 Vessels</option>
              </Form.Select>
            </Col>

            <Col md={6}>
              <Form.Label className="small fw-bold">Thallium Stress Test</Form.Label>
              <Form.Select name="thal" onChange={handleInputChange}>
                <option value="1">Normal</option>
                <option value="2">Fixed Defect</option>
                <option value="3">Reversible Defect</option>
              </Form.Select>
            </Col>
          </Row>

          {/* <div className="d-flex justify-content-end mt-4">
            <Button variant="primary" type="submit" disabled={loading} className="px-5 py-2 fw-bold shadow">
              {loading ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Analyzing...
                </>
              ) : "Predict & Explain Clinical Risk"}
            </Button>
          </div> */}
          {!hidePredictButton && (
            <div className="d-flex justify-content-end mt-4">
              <Button variant="primary" type="submit" disabled={loading} className="px-5 py-2 fw-bold shadow">
                {loading ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Analyzing...
                  </>
                ) : "Predict & Explain Clinical Risk"}
              </Button>
            </div>
          )}
        </Form>
      ) : (
        <ClinicalResultsView 
            result={result} 
            reset={() => {
                setResult(null);
                setValidated(false);
            }} 
        />
      )}
    </div>
  );
};

export default PredictClinical;