import React, { useState, useEffect } from 'react';
import { Form, Button, Alert, Spinner, Card, Row, Col } from 'react-bootstrap';
import axios from 'axios';
import jsPDF from 'jspdf';

// const PredictECG = ({ isSideBySide }) => {
// const PredictECG = ({ ecgFile, setEcgFile, hidePredictButton = false, isSideBySide = false}) => {
const PredictECG = ({ ecgFile, setEcgFile, result, setResult, hidePredictButton, isSideBySide }) => {
  const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
  console.log("Predict ECG API URL:", process.env.REACT_APP_API_URL);

  const [stage, setStage] = useState('upload'); 
  const [file, setFile] = useState(null);
  const [fileDetails, setFileDetails] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  // const [result, setResult] = useState(null);
  const [localResult, setLocalResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (result) {
      setLocalResult(result);
      setStage('result');
    }
  }, [result]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    if (!['image/jpeg', 'image/png'].includes(selectedFile.type)) {
      setError("Invalid format. Please upload JPEG or PNG.");
      return;
    }
    setError(null);
    setFile(selectedFile);
    setEcgFile(selectedFile);
    setFileDetails({ name: selectedFile.name, size: (selectedFile.size / 1024).toFixed(2) + " KB", type: selectedFile.type });
    setPreview(URL.createObjectURL(selectedFile));
    setStage('preview');
  };

  const handleUpload = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post(`${API_URL}/predict`, formData);
      setLocalResult(response.data);
      // setResult(response.data);
      // setStage('result');
      
      // setEcgFile(file);
      if (setResult) setResult(response.data);
      setStage('result');
      setEcgFile(file);
      if (setResult) {
        setResult(response.data);
      }
    } catch (err) {
      setError("Analysis failed. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const downloadECGReport = async () => {
    setIsExporting(true);
    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const margin = 15;
      const contentWidth = pageWidth - (margin * 2);
      const headerY = 20;
      const lineY = 32;

      // Title
      pdf.setFont("helvetica", "bold");
      pdf.setFontSize(20);
      pdf.setTextColor(13, 110, 253); 
      pdf.text("CardioXAI Report", margin, headerY);

      // Date
      pdf.setFont("helvetica", "normal");
      pdf.setFontSize(10);
      pdf.setTextColor(120);

      const dateText = `Analysis Date: ${new Date().toLocaleDateString()}`;
      const textWidth = pdf.getTextWidth(dateText);
      pdf.text(dateText, pageWidth - margin - textWidth, headerY);

      // Bottom blue border
      pdf.setDrawColor(13, 110, 253);
      pdf.setLineWidth(1.5);
      pdf.line(margin, lineY, pageWidth - margin, lineY);

      // Original Scan Section
      pdf.setFontSize(14);
      pdf.text("1. Original ECG Scan", margin, 42);
      pdf.addImage(preview, 'JPEG', margin, 45, contentWidth, 60);

      // Triage Results
      pdf.setFontSize(14);
      pdf.text("2. Triage & Diagnosis Assessment", margin, 120);
      
      pdf.setFillColor(240, 240, 240);
      pdf.rect(margin, 125, contentWidth, 35, 'F');
      
      pdf.setFontSize(11);
      pdf.setTextColor(0);
      pdf.text(`Primary Category: ${localResult.level1_prediction}`, margin + 5, 135);
      pdf.text(`Confidence Score: ${(localResult.level1_confidence * 100).toFixed(1)}%`, margin + 5, 142);
      pdf.text(`Specific Diagnosis: ${localResult.level2_prediction}`, margin + 5, 152);

      // Explainability Section (Level 1 Heatmap)
      pdf.setFontSize(14);
      pdf.text("3. Visual Interpretability (Heatmaps)", margin, 175);
      pdf.setFontSize(10);
      pdf.text(`Area of Focus (Triage - ${localResult.level1_prediction}):`, margin, 182);
      pdf.addImage(localResult.heatmap_l1, 'PNG', margin, 185, contentWidth / 2 - 5, 50);
      
      // Explainability Section (Level 2 Heatmap)
      pdf.text(`Area of Focus (Diagnosis - ${localResult.level2_prediction}):`, pageWidth / 2 + 5, 182);
      pdf.addImage(localResult.heatmap_l2, 'PNG', pageWidth / 2 + 5, 185, contentWidth / 2 - 5, 50);

      // Footer
      pdf.setFontSize(9);
      pdf.setTextColor(150);
      pdf.text("This is an AI-generated assessment and should be verified by a medical professional.", margin, 280);

      pdf.save(`ECG_Report_${fileDetails.name.split('.')[0]}.pdf`);
    } catch (err) {
      console.error("PDF Error:", err);
      alert("Failed to generate PDF report.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="mt-3">
      {stage === 'upload' && (
        <div className="p-4 border rounded-3 bg-light text-center border-dashed">
          <Form.Control type="file" onChange={handleFileChange} accept="image/*" className="mb-3" />
          {error && <Alert variant="danger">{error}</Alert>}
          <p className="text-muted small m-0">Drag & drop or select ECG scan</p>
        </div>
      )}

      {stage === 'preview' && (
        <div className="p-3 border rounded-3 bg-white shadow-sm">
          <div className="small text-muted mb-2">
            <div><strong>File name:</strong> {fileDetails.name}</div>
            <div><strong>File size:</strong> {fileDetails.size}</div>
          </div>

          <div className="mb-3 text-center">
            <img
              src={preview}
              alt="Preview"
              className="rounded border"
              style={{ maxHeight: '650px', maxWidth: '100%', objectFit: 'contain' }}
            />
          </div>

          <div className="d-flex justify-content-between align-items-center">
            {/* <Button variant="outline-secondary" size="sm" onClick={() => setStage('upload')}>Back</Button> */}
            {/* <Button variant="primary" size="sm" className="px-3" onClick={handleUpload} disabled={loading}>
              {loading ? <Spinner size="sm" /> : "Predict & Explain"}
            </Button> */}
            {!hidePredictButton && (
              <>
                <Button variant="outline-secondary" size="sm" onClick={() => setStage('upload')}>Back</Button>
                <Button variant="primary" size="sm" className="px-3" onClick={handleUpload} disabled={loading}>
                  {loading ? <Spinner size="sm" /> : "Predict & Explain"}
                </Button>
              </>
            )}
          </div>
        </div>
      )}

      {stage === 'result' && localResult && (
        <div className="text-start">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="fw-bold m-0 text-primary">Diagnostic Results</h5>
            <Button 
                variant="outline-primary" 
                size="sm" 
                className="rounded-pill px-3" 
                onClick={downloadECGReport}
                disabled={isExporting}
            >
              {isExporting ? <Spinner size="sm" /> : 'Download Report'}
            </Button>
          </div>

          <Card className="mb-4 border-0 bg-white shadow-sm overflow-hidden">
            <Card.Header className="bg-secondary text-white border-0 py-3">
              <h6 className="fw-bold m-0">Level 1: Triage Assessment</h6>
            </Card.Header>
            <Card.Body className="p-4">
              <Row className="g-4 align-items-center">
                <Col md={isSideBySide ? 12 : 6}>
                  <div className="text-center bg-dark rounded border overflow-hidden">
                    <img src={localResult.heatmap_l1} className="img-fluid" alt="L1 Heatmap" style={{ height: '220px', width: '100%', objectFit: 'fill' }} />
                  </div>
                </Col>
                <Col md={isSideBySide ? 12 : 6}>
                  <div className="ps-md-3">
                    <small className="text-uppercase fw-bold text-muted d-block mb-1">Primary Classification</small>
                    <div className="h4 fw-bold text-dark m-0">{localResult.level1_prediction}</div>
                    <small className="text-uppercase fw-bold text-muted d-block mt-3 mb-1">Model Confidence</small>
                    <div className="h4 fw-bold text-primary m-0">{(localResult.level1_confidence * 100).toFixed(1)}%</div>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          <Card className="mb-3 border-0 bg-white shadow-sm overflow-hidden">
            <Card.Header className="bg-secondary text-white border-0 py-3">
              <h6 className="fw-bold m-0">Level 2: Specific Diagnosis</h6>
            </Card.Header>
            <Card.Body className="p-4">
              <Row className="g-4 align-items-center">
                <Col md={isSideBySide ? 12 : 6}>
                  <div className="text-center bg-dark rounded border overflow-hidden">
                    <img src={localResult.heatmap_l2} className="img-fluid" alt="L2 Heatmap" style={{ height: '220px', width: '100%', objectFit: 'fill' }} />
                  </div>
                </Col>
                <Col md={isSideBySide ? 12 : 6}>
                  <div className="ps-md-3">
                    <div className="p-3 rounded bg-light border-start border-primary border-4">
                      <small className="text-uppercase fw-bold text-muted d-block mb-1">Detailed Diagnosis</small>
                      <div className="h4 fw-bold text-primary m-0">{localResult.level2_prediction}</div>
                    </div>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          <div className="d-flex justify-content-end mt-4">
            <Button variant="outline-primary" size="sm" className="px-4 rounded-pill" onClick={() => setStage('upload')}>
              + Analyze New Scan
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictECG;