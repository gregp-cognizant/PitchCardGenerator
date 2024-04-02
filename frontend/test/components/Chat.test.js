import React from 'react';
import { render, fireEvent, waitFor, screen, act } from '@testing-library/react';
import Chat from '../../src/components/Chat';
import CogAvatar from '../src/img/cog-avatar.png';

// Create Happy Path Mock the fetch API
const happyResponseJson = {
  response: "I am bot",
  chat_history_guid: "1234",
  agent_name: "HappyAgent",
  agent_tools: [
    "tool1",
    "tool2"
  ]
}

const happyResponse = () => Promise.resolve({
  ok: true,
  status: 200,
  json: () => Promise.resolve(happyResponseJson),
});

// Create Fail Path Mock the fetch API
const failResponse = () => Promise.resolve({
  ok: false,
  status: 401,
  json: () => Promise.resolve({ error: 'Unauthorized' }),
});


beforeEach(() => {
  global.fetch = jest.fn(happyResponse);

  // Mock scrollIntoView
  Object.defineProperty(window.HTMLElement.prototype, 'scrollIntoView', {
    writable: true,
    value: jest.fn(),
  });
});

afterEach(() => {
  fetch.mockClear();
  jest.clearAllMocks();
})

const getFakeChatData = () => {
  return {
    chat_history_contents: [
      { type: "human", data: { content: "Tell me about History." } },
      { type: "ai", data: { content: "History is great!" } },
    ],
  };
};

const getFakeChatMetaData = () => {
  return {
  chat_history_guid: "myChatId",
  chat_agent: "MyChatAgent"
}}

const getChat = () => {
  const fakeChatMetaData = getFakeChatMetaData();
  const fakeChatData = getFakeChatData();
  return <Chat chatMetaData={fakeChatMetaData} chatData={fakeChatData}/>;
}

it('renders expected components', () => {
  render(getChat());
  const chatDateElement = screen.getByText(/chat date/i);
  expect(chatDateElement).toBeInTheDocument();

  const chatAgentElement = screen.getByText(/chat agent/i);
  expect(chatAgentElement).toBeInTheDocument();

  const chatIdElement = screen.getByText(/chat id/i);
  expect(chatIdElement).toBeInTheDocument();

  const sendElement = screen.getByText(/send/i);
  expect(sendElement).toBeInTheDocument();
});

it('send button triggers a fetch with our expected request payload', async () => {
  render(getChat());
  const inputElement = screen.getByTestId('prompt');
  fireEvent.change(inputElement, { target: { value: 'Who are you?' } });
  fireEvent.click(screen.getByText(/send/i));

  // Wait for the fetch call to complete
  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));

  // Check if the fetch was called with the correct arguments
  expect(fetch).toHaveBeenCalledWith(expect.any(String), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_input: 'Who are you?',
      chat_agent: "MyChatAgent",
      chat_history_guid: 'myChatId',
    }),
    "timeout": 240000,
  });
});

it('send button updates the chat history on promise success', async () => {
  render(getChat());

  // Find the input field and button
  const input = screen.getByTestId('prompt');
  const button = screen.getByText('Send');

  // Type a message into the input field and click the Send button
  fireEvent.change(input, { target: { value: 'Who are you?' } });
  fireEvent.click(button);

  // Wait for the response to be rendered
  await waitFor(() => screen.getByText('I am bot'));

  // Check if fetch was called
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('logs errors to the console and displays them', async () => {
  global.fetch = jest.fn(failResponse);

  // Mock console.error
  console.error = jest.fn();

  render(getChat());

  // Find the input field and button
  const input = screen.getByTestId('prompt');
  const button = screen.getByText('Send');

  // Type a message into the input field and click the Send button
  fireEvent.change(input, { target: { value: 'Who are you?' } });
  fireEvent.click(button);

  // Wait for console.error to be called
  await waitFor(() => expect(console.error).toHaveBeenCalled());

  // Get the error message from the Alert component
  const errorMessage = await screen.findByText('Error Sending Chat');

  // Assert that console.error was called
  expect(console.error).toHaveBeenCalledWith("error: ", new Error('HTTP error! status: 401'));

  // Assert that error message is displayed
  expect(errorMessage).toBeInTheDocument();
});

it('displays multiple errors', async () => {
  global.fetch = jest.fn(failResponse);

  // Mock console.error
  console.error = jest.fn();

  render(getChat());

  // Find the input field and button
  const input = screen.getByTestId('prompt');
  const button = screen.getByText('Send');

  // Trigger error once
  fireEvent.change(input, { target: { value: 'Who are you?' } });
  fireEvent.click(button);
  await waitFor(() => expect(console.error).toHaveBeenCalled());

  // Trigger error twice
  fireEvent.change(input, { target: { value: 'Who are you?' } });
  fireEvent.click(button);
  await waitFor(() => expect(console.error).toHaveBeenCalled());

  // Get the error message from the Alert component
  const errorMessage1 = screen.getAllByText('Error Sending Chat')[0];
  const errorMessage2 = screen.getAllByText('Error Sending Chat')[1];

  // Assert that both error messages are displayed
  expect(errorMessage1).toBeInTheDocument();
  expect(errorMessage2).toBeInTheDocument();
});

it('removes error when close button is clicked', async () => {
  // Mock fetch to return an error
  global.fetch = jest.fn(() => Promise.reject(new Error('HTTP error! status: 401')));

  // Mock console.error
  console.error = jest.fn();

  render(getChat());

  // Find the input field and button
  const input = screen.getByTestId('prompt');
  const button = screen.getByText('Send');

  // Type a message into the input field and click the Send button
  fireEvent.change(input, { target: { value: 'Who are you?' } });
  fireEvent.click(button);

  // Wait for console.error to be called
  await waitFor(() => expect(console.error).toHaveBeenCalled());

  // Get the error message from the Alert component
  const errorMessage = await screen.findByText('HTTP error! status: 401');

  // Assert that error message is displayed
  expect(errorMessage).toBeInTheDocument();

  // Find the close button and click it
  const closeButton = screen.getByRole('button', { name: /close/i });
  fireEvent.click(closeButton);

  // Assert that error message is no longer in the document
  await waitFor(() => expect(errorMessage).not.toBeInTheDocument());
});

it('send button disables the send button while waiting on the promise', async () => {
  render(getChat());

  // Find the input field and buttons
  const input = screen.getByTestId('prompt');
  const sendButton = screen.getByText('Send');

  // Type a message into the input field and click the Send button
  fireEvent.change(input, { target: { value: 'Who are you?' } });
  fireEvent.click(sendButton);

  // Check if the send button is disabled
  expect(sendButton).toBeDisabled();

  // Wait for the response to be rendered
  await waitFor(() => screen.getByText('I am bot'));

  // Check if the send button is enabled
  expect(sendButton).not.toBeDisabled();
});

it('send button clears the input prompt on submit', async () => {
  render(getChat());

  // Find the input field and button
  const input = screen.getByTestId('prompt');
  const button = screen.getByText('Send');

  // Type a message into the input field and click the Send button
  fireEvent.change(input, { target: { value: 'Who are you?' } });
  fireEvent.click(button);

  // Wait for the response to be rendered
  await waitFor(() => screen.getByText('I am bot'));

  // Check if fetch was called
  expect(fetch).toHaveBeenCalledTimes(1);

  // Check if the input prompt is clear
  expect(input.value).toBe('');
});

it('updates messages when chatData changes', async () => {
  const initialChatData = {
    chat_history_contents: [
      { type: 'human', data: {content: 'Hello'}},
    ],
  };

  const { rerender } = render(<Chat chatData={initialChatData} />);

  const newChatData = {
    chat_history_contents: [
      { type: 'human', data: {content: 'Hello' }},
      { type: 'ai', data: {content: 'Hi' }},
    ],
  };

  await act(async () => {
    rerender(<Chat chatData={newChatData} />);
  });

  const aiMessageElement = screen.getByText('Hi');
  expect(aiMessageElement).toBeInTheDocument();
});

it('handles chatData being null', () => {
  render(<Chat chatData={null} />);
  const chatHistoryElement = screen.getByTestId('chat-history');
  expect(chatHistoryElement.children.length).toBe(1);
});

it('handles chatMetaData being null', () => {
  render(<Chat chatMetaData={null} />);
  const chatDateElement = screen.getByTestId('chatDate');
  expect(chatDateElement).toHaveTextContent('Chat Date: unknown');
  const chatAgentElement = screen.getByTestId('chatAgent');
  expect(chatAgentElement).toHaveTextContent('Chat Agent: unknown');
  const chatGuidElement = screen.getByTestId('chatGuid');
  expect(chatGuidElement).toHaveTextContent('Chat ID: unknown');
});

// handles chatMetaData.date or chatAgent or chatGuid being null
it('handles chatMetaData properties being null or undefined', () => {
  const chatMetaData = {
    chat_history_guid: null,
    chat_agent: null,
    date: null,
  };
  render(<Chat chatMetaData={chatMetaData} />);
  const chatDateElement = screen.getByTestId('chatDate');
  expect(chatDateElement).toHaveTextContent('Chat Date: unknown');
  const chatAgentElement = screen.getByTestId('chatAgent');
  expect(chatAgentElement).toHaveTextContent('Chat Agent: unknown');
  const chatGuidElement = screen.getByTestId('chatGuid');
  expect(chatGuidElement).toHaveTextContent('Chat ID: unknown');
});

it('renders an image for messages with type ai', () => {
  const chatData = {
    chat_history_contents: [
      { type: 'ai', data: {content: 'Hello'}},
    ],
  };
  render(<Chat chatData={chatData} />);
  const aiMessageElement = screen.getByText('Hello');
  const imgElement = screen.getByAltText('Bot Avatar');
  expect(imgElement.tagName).toBe('IMG');
  expect(imgElement.src).toContain(CogAvatar);
  expect(imgElement.alt).toBe('Bot Avatar');
  expect(imgElement.className).toBe('bot-avatar');
  expect(aiMessageElement.parentElement.className).toContain('markdown-container');
});

it('does not render an image for messages with type human', () => {
  const chatData = {
    chat_history_contents: [
      { type: 'human', data: {content: 'Hello'}},
    ],
  };
  render(<Chat chatData={chatData} />);
  const humanMessageElement = screen.getByText('Hello');
  expect(humanMessageElement.previousElementSibling).toBeNull();
  expect(humanMessageElement.parentElement.className).not.toContain('bot-avatar');
});

it('renders chat date', () => {
  const chatMetaData = {
    date: '2022-01-01',
  };
  render(<Chat chatMetaData={chatMetaData} />);
  const dateElement = screen.getByTestId('chatDate');
  expect(dateElement).toHaveTextContent('Chat Date: 2022-01-01');
});
