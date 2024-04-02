import React from 'react';
import { render, screen } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import SpinnerWithTimer from '../../src/components/SpinnerWithTimer';

jest.useFakeTimers();

test('increments seconds after 1 second', async () => {
  render(<SpinnerWithTimer />);

  // Initially, the seconds should be 0
  expect(screen.getByText('0 seconds')).toBeInTheDocument();

  // Advance timers by 1 second
  act(() => {
    jest.advanceTimersByTime(1000);
  });

  // After 1 second, the seconds should be 1
  expect(screen.getByText('1 seconds')).toBeInTheDocument();
});
