import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../src/App';
import Chat from '../src/components/Chat';
import fetchMock from 'jest-fetch-mock';

jest.mock('../src/components/Chat', () => jest.fn(() => null));

fetchMock.enableMocks();

beforeEach(() => {
  const happyChatHistoryMetaDataResponseJson = {
    chat_history_metadata: [
      {
        "date": "2024-01-25T17:05:00Z",
        "chat_agent": "FakeAgent1",
        "chat_history_guid": "fake-guid-1"
      },
      {
        "date": "2024-01-25T17:02:49Z",
        "chat_agent": "FakeAgent2",
        "chat_history_guid": "fake-guid-2"
      },
  ]}

  const happyResponse = () => Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve(happyChatHistoryMetaDataResponseJson),
  });

  global.fetch = jest.fn(happyResponse);
});

afterEach(() => {
  fetch.mockClear();
  jest.clearAllMocks();
})

it('has components we expect"', async () => {
  render(<App />);

  const headingElement = screen.getByRole('heading', { name: /AgentFramework/ });
  await waitFor(() => expect(headingElement).toBeInTheDocument());

  const previousChatFormElement = screen.getByTestId('previous_chat_form');
  expect(previousChatFormElement).toBeInTheDocument();

  const newChatFormElement = screen.getByTestId('new_chat_form');
  expect(newChatFormElement).toBeInTheDocument();
});


it('chat_history_select is populated on page load', async () => {
  render(<App />);
  const selectElement = screen.getByTestId('chat_history_select');
  expect(selectElement.children.length).toBe(1);

  await waitFor(() => expect(selectElement.children.length).toBe(3));

  expect(selectElement.value).toBe('');
});

it('updates selectedChatHistory when select input is changed', async () => {
  const { getByTestId } = render(<App />);
  const selectElement = getByTestId('chat_history_select');

  await waitFor(() => expect(selectElement.children.length).toBe(3));

  // default value empty
  expect(selectElement.value).toBe('');

  fireEvent.change(selectElement, { target: { value: 'fake-guid-2' } });

  await waitFor(() => expect(selectElement.value).toBe('fake-guid-2'));
});

it('updates chatAgent when select input is changed', async () => {
  const { getByTestId } = render(<App />);
  const selectElement = getByTestId('chat_agent_select');

  expect(selectElement.value).toBe('AgentFramework');

  fireEvent.change(selectElement, { target: { value: 'research_agent' } });

  await waitFor(() => expect(selectElement.value).toBe('research_agent'));
});

it('calls Chat with the correct props', async () => {
  const { getByTestId } = render(<App />);
  const selectElement = getByTestId('chat_agent_select');

  // change the agent
  fireEvent.change(selectElement, { target: { value: 'research_agent' } });

  const buttonElement = getByTestId('new_chat_button');
  fireEvent.click(buttonElement);

  await waitFor(() => expect(selectElement.value).toBe('research_agent'));

  expect(Chat).toHaveBeenCalled();

  // expect the first argument to be the chatMetaData object
  const originalGuid = Chat.mock.calls[0][0].chatMetaData.chat_history_guid;
  const newGuid = Chat.mock.calls[1][0].chatMetaData.chat_history_guid;
  const originalAgent = Chat.mock.calls[0][0].chatMetaData.chat_agent;
  const newAgent = Chat.mock.calls[1][0].chatMetaData.chat_agent;
  expect(originalGuid).not.toBe(newGuid);
  expect(originalAgent).not.toBe(newAgent);
});
