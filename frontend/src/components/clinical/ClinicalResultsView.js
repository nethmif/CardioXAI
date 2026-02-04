import React, { useRef, useState } from 'react';
import { Alert, Button, Tabs, Tab, Row, Col, Card, Badge, OverlayTrigger, Tooltip, Spinner } from 'react-bootstrap';
import DiceTable from './DiceTable';
import VerticalDiceTable from './VerticalDiceTable'
import ReactMarkdown from 'react-markdown';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const ClinicalResultsView = ({ result, reset }) => {
  const [isExporting, setIsExporting] = useState(false);
  const section1Ref = useRef();
  const section2Ref = useRef();
  const section3Ref = useRef();
  // const section4Ref = useRef();
  const section5Ref = useRef();

  const handleDownloadPDF = async () => {
    setIsExporting(true);
    const pdf = new jsPDF('p', 'mm', 'a4'); 
    // const sections = [section1Ref, section2Ref, section3Ref, section4Ref, section5Ref];
    const sections = [section1Ref, section2Ref, section3Ref, section5Ref];

    
    try {
      for (let i = 0; i < sections.length; i++) {
        const element = sections[i].current;

        element.style.display = 'block';
        element.style.position = 'absolute';
        element.style.left = '-9999px'; 
        element.style.top = '0';
        element.style.width = '1200px';
        element.style.zIndex = '-1';

        const tableWrapper = element.querySelector('.table-responsive');
        const table = element.querySelector('table');
        
        if (tableWrapper && table) {
            tableWrapper.style.overflow = 'visible';
            tableWrapper.style.display = 'block';
            tableWrapper.style.width = '100%';
            
            table.style.width = 'auto'; 
            table.style.tableLayout = 'auto';
            table.style.minWidth = '1100px'; 
        }

        await new Promise(resolve => setTimeout(resolve, 800));

        const canvas = await html2canvas(element, {
          scale: 2,
          useCORS: true,
          logging: false,
          width: element.offsetWidth, 
          windowWidth: element.scrollWidth 
        });      

        const imgData = canvas.toDataURL('image/png');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const margin = 10;
        const imgWidth = pdfWidth - (margin * 2);
        
        const imgHeight = (canvas.height * imgWidth) / canvas.width;

        if (i > 0) pdf.addPage();
        
        pdf.addImage(imgData, 'PNG', margin, margin, imgWidth, imgHeight);
      
        element.style.display = 'none';
        element.style.position = 'static';
        element.style.width = 'auto'; 
      }
      pdf.save(`CardioXAI_Clinical_Report_${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (error) {
      console.error("PDF Generation Failed:", error);
    } finally {
      setIsExporting(false);
    }
  };

  const renderTooltip = (text) => <Tooltip id="button-tooltip">{text}</Tooltip>;

  const prob = Number(result?.probability);

  const riskPercent = Number.isFinite(prob)
    ? (prob * 100).toFixed(1)
    : "N/A";

  return (
    <div className="animate__animated animate__fadeIn">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3 className="fw-bold m-0 text-primary">Analysis Results</h3>
        <div>
          <Button
            variant="primary"
            size="sm"
            onClick={handleDownloadPDF}
            disabled={isExporting}
            className="rounded-pill me-2 shadow-sm"
          >
            {isExporting ? (
              <>
                <Spinner size="sm" animation="border" className="me-2" />
                Generating PDF...
              </>
            ) : 'Download Full Report'}
          </Button>
          <Button variant="outline-dark" size="sm" onClick={reset} className="rounded-pill">New Patient</Button>
        </div>
      </div>

      <Alert variant={result.prediction === 1 ? "danger" : "success"} className="shadow-sm border-0 mb-4 p-4">
        <Row className="align-items-center">
          <Col md={8}>
            <h5 className="text-uppercase mb-1 small fw-bold" style={{opacity: 0.8}}>Risk Assessment</h5>
            <h2 className="m-0 fw-bold">
                {/* {(result.probability * 100).toFixed(1)}% — {result.prediction === 1 ? "High Risk Detected" : "Low Risk / Healthy"} */}
                {riskPercent}% — {result.prediction === 1 ? "High Risk" : "Low Risk / Healthy"}
            </h2>
          </Col>
        </Row>
      </Alert>

      <Tabs defaultActiveKey="ai_advice" id="clinical-tabs" className="mb-4 custom-tabs border-0">

        {/* Lifestyle Tab*/}
        <Tab eventKey="ai_advice" title="Lifestyle Guide">
          <Card className="border-0 shadow-sm mt-3">
            <Card.Body className="p-4 bg-light rounded">
              <div className="small text-muted">
                <ReactMarkdown>{result.llm_report}</ReactMarkdown>
              </div>
            </Card.Body>
          </Card>
        </Tab>

        {/* Local Analysis*/}
        <Tab eventKey="local" title="Local Explanations">
          <Row className="mt-3">
            <Col lg={12} className="mb-4">
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white d-flex align-items-center">
                  <span className="fw-bold me-2">Key Patient Factors Influencing Risk</span>
                  <OverlayTrigger placement="right" overlay={renderTooltip("Shows how this patient’s clinical measurements increase or reduce cardiac risk compared to an average patient.")}>
                    <Badge pill bg="secondary" style={{ cursor: 'help' }}>?</Badge>
                  </OverlayTrigger>
                </Card.Header>

                <Card.Body className="text-center overflow-auto">
                   <div className="alert alert-info py-2 small text-start mb-3">
                    <strong>How to read this: </strong>  
                    Factors shown in <strong>red</strong> increase the patient’s cardiac risk, while factors in <strong>blue</strong> reduce it.  
                    The final score reflects the model’s estimated risk level for this patient.
                   </div>
                  <img src={result.shap_plot} className="img-fluid" alt="SHAP Plot" style={{ minWidth: '600px' }} />
                  <div className="text-start small text-muted">
                    <ReactMarkdown>{result.shap_explanation}</ReactMarkdown>
                  </div>
                </Card.Body>
              </Card>
            </Col>
        
            <Col lg={12}>
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white d-flex align-items-center">
                  <span className="fw-bold me-2">Most Influential Factors For This Patient</span>
                  <OverlayTrigger placement="right" overlay={renderTooltip("Highlights which clinical features most strongly influenced this specific prediction.")}>
                    <Badge pill bg="secondary" style={{ cursor: 'help' }}>?</Badge>
                  </OverlayTrigger>
                </Card.Header>

                <Card.Body className="text-center">
                   <div className="alert alert-info py-2 small text-start mb-3">
                    <strong>Clinical interpretation: </strong>  
                    Features are ordered by how strongly they influenced the model’s decision for this patient.  
                    Longer bars indicate greater clinical influence on the risk estimate.
                  </div>
                  <img src={result.lime_plot} className="img-fluid" alt="LIME Plot" />
                  <div className="text-start small text-muted">
                    <ReactMarkdown>{result.lime_explanation}</ReactMarkdown>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>

        {/* Global Analysis*/}
        {/* <Tab eventKey="global" title="Population Level Insights">
          <Card className="border-0 shadow-sm mt-3">
            <Card.Header className="bg-white fw-bold">  Common Risk Factors Observed Across Patients</Card.Header>
            <Card.Body className="text-center">
              <div className="alert alert-info py-2 small text-start mb-3">
                This view summarizes which clinical factors most commonly influence cardiac risk across the entire patient population.  
                It helps clinicians verify whether this patient’s risk profile aligns with known population trends.
              </div>
              <img src={result.summary_plot} className="img-fluid" alt="Summary Plot" />
              <div className="text-start small text-muted">
                <ReactMarkdown>
                  {result.summary_explanation}
                </ReactMarkdown>
              </div>
            </Card.Body>
          </Card>
        </Tab> */}

        {/* Counterfactuals */}
        <Tab eventKey="dice" title="Risk Reduction Scenarios">
          <Card className="border-0 shadow-sm mt-3">
            <Card.Header className="bg-white d-flex justify-content-between align-items-center">
              <span className="fw-bold">Potential Interventions to Reduce Risk</span>
            </Card.Header>
            <Card.Body>
              <div className="alert alert-info py-2 small text-start mb-3">
                This table shows <strong>clinically achievable changes</strong> that could potentially reduce the patient’s predicted cardiac risk.  
                These scenarios are intended to support treatment planning, not replace clinical judgment.
              </div>
              <DiceTable diceData={result.dice_data} />
              <div className="text-start small text-muted">
                <ReactMarkdown>{result.dice_explanation}</ReactMarkdown>
              </div>
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>

      <div style={{ position: 'absolute', top: 0, left: 0, height: 0, overflow: 'hidden' }}>
        <div ref={section1Ref} className="p-5 bg-white" style={{ width: '800px', display: 'none' }}>
            <div className="d-flex justify-content-between border-bottom pb-4 mb-4" style={{borderBottom: '2px solid #0d6efd !important'}}>
                <h1 style={{color: '#0d6efd', fontWeight: 'bold'}}>CardioXAI Report</h1>
                <div className="text-end small text-muted">Analysis Date: {new Date().toLocaleDateString()}</div>
            </div>

            <div className={`p-4 rounded-3 mb-4 ${result.prediction === 1 ? 'bg-danger' : 'bg-success'}`} style={{color: 'white'}}>
                <h2 className="mb-0">{(result.probability * 100).toFixed(1)}% Risk Score</h2>
                <p className="mb-0 fw-bold">{result.prediction === 1 ? "Increased Cardiac Risk Detected" : "Low Risk / Healthy Status"}</p>
            </div>
            <h4 className="border-bottom pb-2 mb-3" style={{color: '#0d6efd'}}>1. Lifestyle Guide</h4>
            <div className="small text-muted">
              <ReactMarkdown>{result.llm_report}</ReactMarkdown>
            </div>
        </div>

        <div ref={section2Ref} className="p-5 bg-white" style={{ width: '800px', display: 'none' }}>
            <h4 className="border-bottom pb-2 mb-4" style={{color: '#0d6efd'}}>2. Local Explanations</h4>
            <h6 className="fw-bold text-muted mt-3">Key Patient Factors Influencing Risk</h6>
            <div className="alert alert-info py-2 small text-start mb-3">
              <strong>How to read this: </strong>  
              Factors shown in <strong>red</strong> increase the patient’s cardiac risk, while factors in <strong>blue</strong> reduce it.  
              The final score reflects the model’s estimated risk level for this patient.
            </div>
            <img src={result.shap_plot} className="img-fluid mb-5 border p-2" alt="SHAP" />
            <div className="small text-muted">
              <ReactMarkdown>{result.shap_explanation}</ReactMarkdown>
            </div>
        </div>

        <div ref={section3Ref} className="p-5 bg-white" style={{ width: '800px', display: 'none' }}>
            <h6 className="fw-bold text-muted">Most Influential Factors For This Patient</h6>
            <div className="alert alert-info py-2 small text-start mb-3">
              <strong>Clinical interpretation: </strong>  
              Features are ordered by how strongly they influenced the model’s decision for this patient.  
              Longer bars indicate greater clinical influence on the risk estimate.
            </div>
            <img src={result.lime_plot} className="img-fluid border p-2" alt="LIME" />
            <div className="small text-muted">
              <ReactMarkdown>{result.lime_explanation}</ReactMarkdown>
            </div>
        </div>

        {/* <div ref={section4Ref} className="p-5 bg-white" style={{ width: '800px', display: 'none' }}>
            <h4 className="border-bottom pb-2 mb-4" style={{color: '#0d6efd'}}>3. Population Level Insights</h4>
            <div className="alert alert-info py-2 small text-start mb-3">
                This view summarizes which clinical factors most commonly influence cardiac risk across the entire patient population.  
                It helps clinicians verify whether this patient’s risk profile aligns with known population trends.
            </div>
            <img src={result.summary_plot} className="img-fluid border p-2" alt="Global" />
            <div className="small text-muted">
              <ReactMarkdown>{result.summary_explanation}</ReactMarkdown>
            </div>
        </div> */}

        <div ref={section5Ref} className="p-5 bg-white" style={{ width: '800px', display: 'none' }}>
            <h4 className="border-bottom pb-2 mb-4" style={{color: '#0d6efd'}}>3. Risk Reduction Scenarios</h4>
            <div className="alert alert-info py-2 small text-start mb-3">
              This table shows <strong>clinically achievable changes</strong> that could potentially reduce the patient’s predicted cardiac risk.  
              These scenarios are intended to support treatment planning, not replace clinical judgment.
            </div>
            <VerticalDiceTable diceData={result.dice_data} />
            <div className="small text-muted">
              <ReactMarkdown>{result.dice_explanation}</ReactMarkdown>
            </div>
            <footer className="mt-5 p-3 bg-light border text-center rounded small text-muted">
                This report is for clinical support only. CardioXAI Diagnostics {new Date().getFullYear()}.
            </footer>
        </div>
      </div>
    </div>
  );
};

export default ClinicalResultsView;