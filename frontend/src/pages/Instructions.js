import React from 'react';
import { Container, Card, Row, Col } from 'react-bootstrap';

const Instructions = () => (
  <Container className="py-5">
    <Card className="shadow-sm p-4 border-0 bg-white">
      <h2 className="mb-4 text-primary fw-bold">System Overview & Guide</h2>
      <p className="text-secondary">CardioXAI supports clinical decision-making by providing hierarchical myocardial diagnoses and predicting the presence or absence of heart disease from clinical features.</p>
      
      <Row className="mt-4 g-4">
        <Col md={6}>
          <div className="p-4 rounded-3 bg-light border-start border-primary border-4">
            <h5 className="fw-bold pb-2">Stepwise ECG Assessment</h5>
            <ol className="small text-muted">
              <li>Upload an ECG image (JPG/PNG).</li>
              <li>Verify details in the <strong>Preview</strong> stage.</li>
              <li>Analyze hierarchical triage (L1) and diagnosis (L2).</li>
              <li>Examine Heatmaps for spatial evidence.</li>
            </ol>
          </div>
        </Col>
        <Col md={6}>
          <div className="p-4 rounded-3 bg-light border-start border-info border-4">
            <h5 className="fw-bold pb-2">Clinical Feature Prediction</h5>
            <ol className="small text-muted">
              <li>Enter patient clinical and laboratory data.</li>
              <li>Review predicted cardiac risk and feature-level explanations to understand key clinical drivers.</li>
              <li>Explore actionable insights and patient-friendly lifestyle recommendations.</li>
            </ol>
          </div>
        </Col>
      </Row>
    </Card>
  </Container>
);
export default Instructions;