import React from 'react';
import { Container, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Home = () => (
  <Container className="text-center py-5">
    <div className="py-5 bg-white rounded-4 shadow-sm">
      <h1 className="display-4 fw-bold text-primary mb-3">Empowering Precision Cardiology</h1>
      <p className="lead fs-4 text-muted mx-auto mb-5" style={{ maxWidth: '800px' }}>
        A decision support system for heart disease assessment using ECG analysis and clinical risk factors.
      </p>
      <Link to="/predict" className="btn btn-primary btn-lg px-5 py-3 shadow">Get Started</Link>
    </div>
  </Container>
);

export default Home;