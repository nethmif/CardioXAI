import React from 'react';
import { Navbar, Container, Nav } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Header = () => (
  <Navbar bg="dark" variant="dark" expand="lg" className="px-4 shadow-sm mb-4 sticky-top">
    <Container>
      <Navbar.Brand as={Link} to="/" className="fw-bold fs-3">CardioXAI</Navbar.Brand>
      <Navbar.Toggle aria-controls="basic-navbar-nav" />
      <Navbar.Collapse id="basic-navbar-nav">
        <Nav className="ms-auto fw-medium">
          <Nav.Link as={Link} to="/">Home</Nav.Link>
          <Nav.Link as={Link} to="/instructions">Instructions</Nav.Link>
          <Nav.Link as={Link} to="/predict">Prediction</Nav.Link>
        </Nav>
      </Navbar.Collapse>
    </Container>
  </Navbar>
);



export default Header;