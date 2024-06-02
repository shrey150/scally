import React from 'react';
import './Logo.css';

function Logo() {
  return (
    <div className="logo">
      {/* <span className="logo-text">Scally</span> */}
      <img alt="" src='./public/favicon.ico'></img>
      <span className="logo-highlight">ScallyAI</span>
    </div>
  );
}

export default Logo;