import React, { useState, useEffect, useRef } from 'react';
import cogAvatar from '../img/cog-avatar.png';
import { ErrorBoundary } from 'react-error-boundary'

//CSS
import '../css/Chat.css';

// Custom Component Imports
import SpinnerWithTimer from './SpinnerWithTimer';
import ErrorComponent from './ErrorComponent';

// Component Imports
// ToDo: relative imports
import MarkdownComponent from './MarkdownComponent';

const url_chat = "http://localhost:8000/chat/"

const Chat = ({ chatMetaData, chatData }) => {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState(null);
    const [isErrorDialogOpen, setIsErrorDialogOpen] = useState(false);

    const handleErrorClose = (errorIndex) => {
        setErrors(prevErrors => prevErrors.filter((error, index) => index !== errorIndex));
        if(errors.length <= 1) {
            setIsErrorDialogOpen(false);
        }
    }

    const handleError = (error) => {
        console.error("error: ", error);

        const newError = {
          type: "Sending Chat",
          message: error.message
        };

        // Check if 'errors' array exists, if not create it, otherwise append to it
        if (!errors) {
          setErrors([newError]);
        } else {
          setErrors(prevErrors => [...prevErrors, newError]);
        }

        // Open the error dialog
        setIsErrorDialogOpen(true);
      };

    const messagesEndRef = useRef(null);

    const handleSend = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        const message = event.target.elements.message.value;
        setMessages([...messages, {
            type: 'human',
            data: {
                content: message
            }
        }]);

        // Clear the input field before sending the message
        event.target.reset();

        try {
            const response = await fetch(url_chat, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_input: message,
                    chat_agent: chatMetaData.chat_agent,
                    chat_history_guid: chatMetaData.chat_history_guid
                }),
                timeout: 240000 // 4 minutes in milliseconds
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const botMessage = await response.json();
            setMessages([...messages,
                { type: 'human', data: {content: message}},
                { type: 'ai', data: {content: botMessage.response}}]
            );

        } catch (error) {
            handleError(error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        setMessages(chatData && chatData.chat_history_contents ? chatData.chat_history_contents : []);
      }, [chatData]);

    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

    return (
        <>
            <div data-testid="chat">
                <p data-testid="chatDate">Chat Date: {chatMetaData && chatMetaData.date ? chatMetaData.date : 'unknown'}</p>
                <p data-testid="chatAgent">Chat Agent: {chatMetaData && chatMetaData.chat_agent ? chatMetaData.chat_agent : 'unknown'}</p>
                <p data-testid="chatGuid">Chat ID: {chatMetaData && chatMetaData.chat_history_guid ? chatMetaData.chat_history_guid : 'unknown'}</p>

                <div className="chat">

                    <div className="chat-messages-container">
                        <ul className="chat-messages" data-testid="chat-history">
                            {messages.map((message, index) => (
                                <li key={index} className={`chat-message chat-message-${message.type}`}>
                                    {message.type === 'ai' ? <img src={cogAvatar} alt="Bot Avatar" className="bot-avatar" /> : null}
                                    <ErrorBoundary>
                                        <MarkdownComponent
                                            content={message.data.content}
                                        />
                                    </ErrorBoundary>
                                </li>
                            ))}
                            <div ref={messagesEndRef} />
                        </ul>
                    </div>
                    {isLoading && <SpinnerWithTimer />}
                    <div className="chat-form-container">
                        <div className="chat-form-wrapper">
                            <form onSubmit={handleSend} className="chat-form">
                                {/* Consider using MUI for a text area which auto handles hight scaling out of the box */}
                                <textarea id="message" rows={5} data-testid="prompt" name="message" className="chat-input" placeholder="Enter your message" ></textarea>
                                <button type="submit" className="app-button" disabled={isLoading}>Send</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            <ErrorComponent
                open={isErrorDialogOpen}
                handleClose={handleErrorClose}
                errors={errors}
            />
        </>
    );
}

export default Chat;
