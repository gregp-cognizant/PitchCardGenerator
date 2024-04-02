import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import NewChatForm from '../../src/components/NewChatForm';

it('renders components we expect', () => {
  const handleChange = jest.fn();
  const { getByText, getByDisplayValue } = render(<NewChatForm handleStartNewChat={handleChange} />);

  const select = getByDisplayValue('AgentFramework');
  expect(select).toBeInTheDocument();

  const button = getByText('Start New Chat');
  expect(button).toBeInTheDocument();

  const values = Array.from(select.children).map(option => option.value);
  expect(values).toContain('AgentFramework');
  expect(values).toContain('research_agent');
  expect(values).toContain('medical_billing_agent');

  fireEvent.click(button);
  expect(handleChange).toHaveBeenCalled();
});

it('changes the value of the select', () => {
  const handleChange = jest.fn();
  const { getByDisplayValue } = render(<NewChatForm handleStartNewChat={handleChange} />);

  const select = getByDisplayValue('AgentFramework');
  fireEvent.change(select, { target: { value: 'research_agent' } });
  expect(select.value).toBe('research_agent');
});
