import React, { useState } from 'react';
import './App.css';
import Logo from './logo';
import ReactMarkdown from 'react-markdown';

function App() {
    const [repoUrl, setRepoUrl] = useState('');
    const [generatedContent, setGeneratedContent] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            console.log('Sending request to backend...');
            const response = await fetch('http://localhost:8000/generate', { // Use port 8000
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ "url": repoUrl }),
            });
            console.log('Received response from backend');
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }
            const data = await response.json();
            setGeneratedContent(data.message);
        } catch (error) {
            console.error('Error during fetch:', error);
            setGeneratedContent('Failed to fetch');
        }
    };

    return (
        <div className="container">
            <Logo />
            <p>Generate onboarding tutorials for Pull Requests</p>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="Enter Pull Request URL"
                />
                <button type="submit">Go</button>
            </form>
            <div id="generatedContent">
                <ReactMarkdown>{generatedContent}</ReactMarkdown>
            </div>
        </div>
    );
}

export default App;
