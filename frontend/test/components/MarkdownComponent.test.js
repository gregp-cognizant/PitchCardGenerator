import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import MarkdownComponent from '../../src/components/MarkdownComponent';
import { act } from 'react-dom/test-utils';
import hljs from 'highlight.js';


// Setup the mock for clipboard
beforeEach(() => {
  global.navigator.clipboard = {
    writeText: jest.fn().mockResolvedValue(undefined),
  };
  // mock console error
  console.error = jest.fn();
});

afterEach(() => {
  jest.resetAllMocks();
});

// Mock hljs.highlightElement
jest.mock('highlight.js', () => ({
  highlightElement: jest.fn(),
}));

// Mock 'highlight.js/styles/night-owl.css'
jest.mock('highlight.js/styles/night-owl.css', () => ({}));

jest.useFakeTimers();


describe('MarkdownComponent Tests', () => {

  it('renders markdown content', () => {
    const markdownContent = "# Test Header";
    render(<MarkdownComponent content={markdownContent} />);
    expect(screen.getByText('Test Header')).toBeInTheDocument();
  });

  it('applies highlight to code blocks', () => {
    const codeContent = '```js\nconsole.log("Hello, world!")\n```';
    render(<MarkdownComponent content={codeContent} />);
    expect(hljs.highlightElement).toHaveBeenCalled();
  });

  it('renders code block with copy button', () => {
    const codeContent = '```js\nconsole.log("Hello, world!")\n```';
    render(<MarkdownComponent content={codeContent} />);
    expect(screen.getByText('Copy')).toBeInTheDocument();
    // More assertions to check if the code block is rendered properly
  });

  it('copy button changes text on click and resets after timeout', async () => {
    const codeContent = '```js\nconsole.log("Hello, world!")\n```';
    render(<MarkdownComponent content={codeContent} />);


    await waitFor(() => screen.getByText('Copy'));

    const copyButton = screen.getByText('Copy');

    // click the copy button
    fireEvent.click(copyButton);

    await waitFor(() => screen.getByText('Copied!'));

    // assert that
    expect(global.navigator.clipboard.writeText).toHaveBeenCalledWith('console.log("Hello, world!")');

    expect(copyButton.textContent).toBe('Copied!');

    // Advance timers by 2000 milliseconds
    jest.advanceTimersByTime(2000);

    // Check if the button text has reset to 'Copy'
    await waitFor(() => screen.getByText('Copy'));
  });

  it('renders an image with the correct src and alt text', () => {
    const imageUrl = 'http://example.com/image.png';
    const imageAlt = 'Example Image';
    const markdownWithImage = `![${imageAlt}](${imageUrl})`;

    render(<MarkdownComponent content={markdownWithImage} />);

    const imageElement = screen.getByAltText(imageAlt);
    expect(imageElement).toBeInTheDocument();
    expect(imageElement).toHaveAttribute('src', imageUrl);
    expect(imageElement).toHaveClass('markdown-img');
  });

  it('handles error on clipboard copy failure', async () => {
    // Mock clipboard to reject
    global.navigator.clipboard = {
      writeText: jest.fn().mockRejectedValue(new Error('Clipboard error')),
    };

    // Spy on console.error
    const errorSpy = jest.spyOn(console, 'error');

    const codeContent = '```js\nconsole.log("Hello, world!")\n```';
    render(<MarkdownComponent content={codeContent} />);

    const copyButton = screen.getByText('Copy');

    // Wrap the click event in act()
    // Wrap the click event and timers in act
    await act(async () => {
      fireEvent.click(copyButton);

      // Advance timers by 2000 milliseconds
      jest.advanceTimersByTime(2000);
    });

    // Assert that console.error was called
    expect(errorSpy).toHaveBeenCalledWith('Error copying text: ', expect.any(Error));

    // Clean up
    errorSpy.mockRestore();
  });

  it('renders inline code element', () => {
    const inlineCodeContent = '`inline code`';
    render(<MarkdownComponent content={inlineCodeContent} />);

    const codeElement = screen.getByText('inline code');
    expect(codeElement).toBeInTheDocument();
    expect(codeElement.tagName).toBe('CODE');
  });

  it('renders images with alt text', () => {
    const imageMarkdown = '![alt text](http://example.com/image.png)';
    render(<MarkdownComponent content={imageMarkdown} />);
    const image = screen.getByAltText('alt text');
    expect(image).toHaveAttribute('src', 'http://example.com/image.png');
  });
});
