import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import PredictECG from './ecg/PredictECG';
import PredictClinical from './clinical/PredictClinical';

const PredictionHub = () => {
const [view, setView] = useState('selection'); 
  const [sideBySide, setSideBySide] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setView('selection');
    setSideBySide(false);
  }, [location.key]); 

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        {view !== 'selection' && (
          <div className="d-flex gap-2">
            <Button 
              variant={sideBySide ? "primary" : "outline-primary"} 
              size="sm" 
              onClick={() => setSideBySide(!sideBySide)}
            >
              {sideBySide ? "Close Split View" : "Side-by-Side View"}
            </Button>
          </div>
        )}
      </div>

      {view === 'selection' && (
        <Row className="g-4 mt-2">
          <Col md={6}>
            <Card className="h-100 p-4 shadow-sm border-0 hover-lift bg-white">
              <Card.Body className="d-flex flex-column">
                <div className="mb-3">
                  <h3 className="fw-bold">ECG Image Analysis</h3>
                </div>
                <p className="text-muted flex-grow-1">
                  An initial screening detects myocardial infarction or other cardiac conditions, followed by refined diagnostic categorization.                </p>
                
                <div className="bg-light rounded-3 p-3 mb-4 text-start">
                  <h6 className="small fw-bold text-uppercase text-primary mb-2">Key Features:</h6>
                  <ul className="small text-muted mb-0 ps-3">
                    <li>Hierarchical Triage</li>
                    <li>Heatmaps identifying cause of the diagnosis</li>
                    <li>Supports JPEG/PNG diagnostic scans</li>
                  </ul>
                </div>

                <Button variant="outline-primary" size="lg" className="py-3 fw-bold" onClick={() => setView('ecg')}>
                  Predict for ECG Image
                </Button>
              </Card.Body>
            </Card>
          </Col>

          <Col md={6}>
            <Card className="h-100 p-4 shadow-sm border-0 hover-lift bg-white">
              <Card.Body className="d-flex flex-column">
                <div className="mb-3">
                  <h3 className="fw-bold">Clinical Risk Assessment</h3>
                </div>
                <p className="text-muted flex-grow-1">
                  Evaluate patient cardiovascular risk based on electronic health records and lab results.
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

                <Button variant="outline-primary" size="lg" className="py-3 fw-bold" onClick={() => setView('clinical')}>
                  Predict for Clinical Features
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {(view === 'ecg' || sideBySide) && (
        <Row className="justify-content-center">
          <Col md={sideBySide ? 6 : 8}>
            <Card className="shadow-sm p-4 border-0 mb-4">
              <h4 className="border-bottom pb-2 mb-2">ECG Analysis</h4>
              <PredictECG isSideBySide={sideBySide} />
            </Card>
          </Col>
          
          {(view === 'clinical' || sideBySide) && (
            <Col md={sideBySide ? 6 : 8}>
              <Card className="shadow-sm p-4 border-0">
                <h4 className="border-bottom pb-2 mb-4">Clinical Features</h4>
                <PredictClinical />
              </Card>
            </Col>
          )}
        </Row>
      )}

      {view === 'clinical' && !sideBySide && ( 
        <Row className="justify-content-center">
           <Col md={8}>
              <Card className="shadow-sm p-4 border-0">
                <h4 className="border-bottom pb-2 mb-4">Clinical Parameters</h4>
                <PredictClinical />
              </Card>
           </Col>
        </Row>
      )}
    </Container>
  );
};
export default PredictionHub;