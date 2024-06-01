import React, { useState } from 'react';
import './App.css';
import Logo from './logo';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [generatedContent, setGeneratedContent] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Use fetch or another method to send repoUrl to backend for processing
    const response = await fetch('http://localhost:5000/api/generate-tutorials', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ repoUrl }),
    });
    const data = await response.json();
    setGeneratedContent(data.generatedContent);
  };

  return (
    <div className="container">
      <Logo />
      <p>Generate onboarding tutorials for Github repositories</p>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="Enter GitHub repo URL"
        />
        <button type="submit">Go</button>
      </form>
      <div id="generatedContent">
        {generatedContent}
      </div>
    </div>
  );
}

export default App;
