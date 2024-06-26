import React, { useState } from 'react';
import './App.css';
import Logo from './logo';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CopyToClipboard } from 'react-copy-to-clipboard';

function App() {
    const [repoUrl, setRepoUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [generatedContent, setGeneratedContent] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
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
            setLoading(false);
        } catch (error) {
            console.error('Error during fetch:', error);
            setGeneratedContent('Failed to fetch');
        }
    };

    return (
        <div className="container">
            <div className="header">
                <Logo />
                <p>Interactive onboarding for engineers.</p>
                <i>Link your pull request, and we'll future-proof your codebase!</i>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        value={repoUrl}
                        onChange={(e) => setRepoUrl(e.target.value)}
                        placeholder="Enter Pull Request URL"
                    />
                    <button type="submit">Go</button>
                    <CopyToClipboard text={generatedContent}>
                        <button onClick={() => alert('Onboarding guide copied to clipboard!')}>💾</button>
                    </CopyToClipboard>
                </form>
            </div>
            
            <div id="generatedContent">
                {
                    loading ? (
                        'Loading...'
                    ) : (
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
