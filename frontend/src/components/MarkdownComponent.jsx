import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import PropTypes from 'prop-types';
import hljs from 'highlight.js';
import '../css/night-owl.css';
import '../css/MarkdownComponent.css';

const CopyButton = ({ code }) => {
    const [buttonText, setButtonText] = useState('Copy');

    const copyToClipboard = (code) => {
      navigator.clipboard.writeText(code).then(() => {
        setButtonText('Copied!');
        setTimeout(() => setButtonText('Copy'), 2000); // Reset button text after 2 seconds
      }).catch(err => {
        console.error('Error copying text: ', err);
      });
    };

    return (
      <button className="copy-button" onClick={() => copyToClipboard(code)} title="Copy to clipboard">
        {buttonText}
      </button>
    );
};


const MarkdownComponent = ({ content }) => {

    useEffect(() => {
        // Apply highlighting to all code blocks
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }, [content]);

    const components = {
      code({node, inline, className, children, ...props}) {
        if (inline) {
            return <code className={className}>{children}</code>;
        }
        return (
            <div style={{ position: 'relative' }}>
                <CopyButton code={String(children).replace(/\n$/, '')} />
                <pre className={className} {...props}>
                    <code>{children}</code>
                </pre>
            </div>
        );
    },
        img: ({ src, alt }) => {
            return <img src={src} alt={alt} className="markdown-img" />;
        },
    };
    return (
        <div className="markdown-container">
            <ReactMarkdown
                components={components}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
};

MarkdownComponent.propTypes = {
    content: PropTypes.string.isRequired,
};

export default MarkdownComponent;
