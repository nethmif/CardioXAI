import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Spinner } from 'react-bootstrap';
import PredictECG from './ecg/PredictECG';
import PredictClinical from './clinical/PredictClinical';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const PredictionHub = () => {
  const [view, setView] = useState('selection'); 
  const [sideBySide, setSideBySide] = useState(false);
  const [combinedResult, setCombinedResult] = useState(null);

  const [ecgFile, setEcgFile] = useState(null);
  const [clinicalData, setClinicalData] = useState({});

  const location = useLocation();

  const [ecgResult, setEcgResult] = useState(null);
  const [clinicalResult, setClinicalResult] = useState(null);

  const [loadingCombined, setLoadingCombined] = useState(false);

  useEffect(() => {
    setView('selection');
    setSideBySide(false);
    setCombinedResult(null);
  }, [location.key]); 

const handleCombinedPredict = async () => {
  try {
    if (!ecgFile) {
      alert("Please upload an ECG image.");
      return;
    }

    if (!clinicalData || Object.keys(clinicalData).length === 0) {
      alert("Please enter clinical features.");
      return;
    }

    setLoadingCombined(true);

    const ecgFormData = new FormData();
    ecgFormData.append("file", ecgFile);

    const ecgRes = await axios.post(`${API_URL}/predict`, ecgFormData);

    const clinicalRes = await axios.post(
      `${API_URL}/predict_clinical`,
      clinicalData
    );

    // Save results (for UI display)
    setEcgResult(ecgRes.data);
    setClinicalResult(clinicalRes.data);

    const ecgClass =
      ["Acute MI", "History of MI", "Abnormal"].includes(
        ecgRes.data?.level2_prediction
      )
        ? 1
        : 0;

    const clinicalClass = Number(
      clinicalRes.data?.clinical_prediction ??
      clinicalRes.data?.prediction ??
      0
    );

    const fuseRes = await axios.post(`${API_URL}/fuse_predictions`, {
      ecg_class: ecgClass,
      clinical_prediction: clinicalClass,
    });

    setCombinedResult(fuseRes.data);

  } catch (err) {
    console.error(err);
    alert("Prediction failed. Please check inputs.");
  } finally{
    setLoadingCombined(false);
  }
};
  return (
    <Container className="py-4">
      {/* Header Controls */}
      {view !== 'selection' && (
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div className="d-flex gap-2">
            <Button 
              variant={sideBySide ? "primary" : "outline-primary"} 
              size="sm" 
              onClick={() => setSideBySide(!sideBySide)}
            >
              {sideBySide ? "Close Split View" : "Side-by-Side View"}
            </Button>

            {/* Show Combined Predict only in split view */}
            {sideBySide && (
              <Button 
                variant="success" 
                size="sm" 
                onClick={handleCombinedPredict}
                disabled={loadingCombined}
              >
                {loadingCombined ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Analyzing...
                  </>
                ) : (
                  "Combined Risk Prediction"
                )}
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Selection view */}
      {view === 'selection' && !sideBySide && (
        <Row className="g-4 mt-2">
          <Col md={6}>
            <Card className="h-100 p-4 shadow-sm border-0 hover-lift bg-white">
              <Card.Body className="d-flex flex-column">
                <h3 className="fw-bold mb-3">ECG Image Analysis</h3>
                <p className="text-muted flex-grow-1">
                  Initial screening for myocardial infarction or other cardiac conditions.
                </p>
                <div className="bg-light rounded-3 p-3 mb-4 text-start">
                   <h6 className="small fw-bold text-uppercase text-primary mb-2">Key Features:</h6>
                   <ul className="small text-muted mb-0 ps-3">
                     <li>Hierarchical Triage</li>
                     <li>Heatmaps identifying cause of the diagnosis</li>
                     <li>Supports JPEG/PNG diagnostic scans</li>
                   </ul>
               </div>
                <Button 
                  variant="outline-primary" size="lg" className="py-3 fw-bold" 
                  onClick={() => setView('ecg')}
                >
                  Predict for ECG Image
                </Button>
              </Card.Body>
            </Card>
          </Col>

          <Col md={6}>
            <Card className="h-100 p-4 shadow-sm border-0 hover-lift bg-white">
              <Card.Body className="d-flex flex-column">
                <h3 className="fw-bold mb-3">Clinical Risk Assessment</h3>
                <p className="text-muted flex-grow-1">
                  Evaluate cardiovascular risk based on EHR and lab results.
                </p>
                <div className="bg-light rounded-3 p-3 mb-4 text-start">
                   <h6 className="small fw-bold text-uppercase text-primary mb-2">Key Features:</h6>
                   <ul className="small text-muted mb-0 ps-3">
                     <li>Main factors behind the prediction</li>
                     <li>Visual breakdown of how the decision was made</li>
                     <li>How each patient factor influenced the result</li>
                     <li>Outcome changes under different conditions</li>
                     <li>Confidence score (0–100%)</li>
                   </ul>
                 </div>
                <Button 
                  variant="outline-primary" size="lg" className="py-3 fw-bold" 
                  onClick={() => setView('clinical')}
                >
                  Predict for Clinical Features
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Standalone ECG view */}
      {view === 'ecg' && !sideBySide && (
        <Row className="justify-content-center">
          <Col md={8}>
            <Card className="shadow-sm p-4 border-0 mb-4">
              <h4 className="border-bottom pb-2 mb-4">ECG Analysis</h4>
              <PredictECG
                ecgFile={ecgFile}
                setEcgFile={setEcgFile}
                setResult={(res) => setEcgResult(res)}
                hidePredictButton={false}
                isSideBySide={sideBySide}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Standalone Clinical view */}
      {view === 'clinical' && !sideBySide && (
        <Row className="justify-content-center">
          <Col md={8}>
            <Card className="shadow-sm p-4 border-0 mb-4">
              <h4 className="border-bottom pb-2 mb-4">Clinical Features</h4>
              <PredictClinical
                clinicalData={clinicalData}
                setClinicalData={setClinicalData}
                setResult={(res) => setClinicalResult(res)}
                hidePredictButton={false}
                isSideBySide={sideBySide}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Split view (side-by-side) */}
      {sideBySide && (
        <Row className="justify-content-center g-4">
          {/* Combined result */}
          {combinedResult && (
            <Col md={12}>
              <Card 
                className={`shadow-sm p-4 mt-4 ${
                  combinedResult.label.includes("No") 
                    ? "bg-success text-white" 
                    : "bg-danger text-white"
                }`}
              >
                <h4>Combined Heart Disease Prediction</h4>

                <p>
                  <strong>{combinedResult.label}</strong>
                </p>
              </Card>
            </Col>
          )}
          <Col md={6}>
            <Card className="shadow-sm p-4 border-0">
              <h4 className="border-bottom pb-2 mb-2">ECG Analysis</h4>
              <PredictECG
                ecgFile={ecgFile}
                setEcgFile={setEcgFile}
                result={ecgResult}  
                hidePredictButton={true}
                isSideBySide={sideBySide}
              />
            </Card>
          </Col>
          <Col md={6}>
            <Card className="shadow-sm p-4 border-0">
              <h4 className="border-bottom pb-2 mb-2">Clinical Features</h4>
              <PredictClinical
                clinicalData={clinicalData}
                setClinicalData={setClinicalData}
                result={clinicalResult}  
                hidePredictButton={true}
                isSideBySide={sideBySide}
              />
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default PredictionHub;