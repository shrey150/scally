import React, { useState } from 'react';
import './App.css';
import Logo from './logo';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dark } from 'react-syntax-highlighter/dist/esm/styles/prism';

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
            console.log(data);
            setGeneratedContent(data.text);
        } catch (error) {
            console.error('Error during fetch:', error);
            setGeneratedContent('Failed to fetch');
        }
    };

    return (
        <div className="container">
            <div className="header">
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
            </div>
            <div id="generatedContent">
                {
                    generatedContent === '' ? "Loading..." : (
                        <ReactMarkdown
                            children={generatedContent}
                            components={{
                                code({ node, inline, className, children, ...props }) {
                                    const match = /language-(\w+)/.exec(className || '')
                                    return !inline && match ? (
                                        <SyntaxHighlighter
                                            children={String(children).replace(/\n$/, '')}
                                            style={dark}
                                            language={match[1]}
                                            PreTag="div"
                                            {...props}
                                        />
                                    ) : (
                                        <code className={className} {...props}>
                                            {children}
                                        </code>
                                    )
                                }
                            }}
                        />
                    )
                }
            </div>
        </div>
    );
}

export default App;
