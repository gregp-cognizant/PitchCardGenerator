import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import PreviousChatForm from '../../src/components/PreviousChatForm';

it('renders PreviousChatForm when meta data is null', () => {
  const change = jest.fn();
  const chatHistoryList = [
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
  ];
  const { getByText } = render(<PreviousChatForm
    selectedChatHistoryMetaData={null}
    handleSelectChatHistoryChange={change}
    chatHistoryList={chatHistoryList}
    />);

  expect(getByText('Resume Previous Chat:')).toBeInTheDocument();
  expect(getByText('Pick a previous chat to resume')).toBeInTheDocument();
  expect(getByText('2024-01-25T17:05:00Z | FakeAgent1 | fake-guid-1')).toBeInTheDocument();
  expect(getByText('2024-01-25T17:02:49Z | FakeAgent2 | fake-guid-2')).toBeInTheDocument();
});

it('renders PreviousChatForm if meta data is populated', () => {
  const change = jest.fn();
  const chatHistoryList = [
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
  ];
  const selectedChatHistoryMetaData = {
    "date": "2024-01-25T17:05:00Z",
    "chat_agent": "FakeAgent1",
    "chat_history_guid": "fake-guid-1"
  };
  const { getByText, getByDisplayValue } = render(<PreviousChatForm
    selectedChatHistoryMetaData={selectedChatHistoryMetaData}
    handleSelectChatHistoryChange={change}
    chatHistoryList={chatHistoryList}
    />);

  // Check if the component renders correctly
  expect(getByText('Resume Previous Chat:')).toBeInTheDocument();
  expect(getByText('Pick a previous chat to resume')).toBeInTheDocument();
  expect(getByText('2024-01-25T17:05:00Z | FakeAgent1 | fake-guid-1')).toBeInTheDocument();
  expect(getByText('2024-01-25T17:02:49Z | FakeAgent2 | fake-guid-2')).toBeInTheDocument();
});
