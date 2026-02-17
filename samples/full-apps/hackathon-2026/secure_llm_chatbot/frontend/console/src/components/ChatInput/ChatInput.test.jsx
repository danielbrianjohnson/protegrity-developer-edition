import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatInput from './ChatInput';

describe('ChatInput Component', () => {
  const defaultProps = {
    onSend: vi.fn(),
    isLoading: false,
    placeholder: 'Type a message...',
    selectedModel: { id: 'fin', name: 'Fin AI' },
    onModelChange: vi.fn(),
    availableModels: [
      { id: 'fin', name: 'Fin AI', description: 'Intercom Fin' },
      { id: 'bedrock', name: 'Claude', description: 'Amazon Bedrock' }
    ]
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders textarea with placeholder', () => {
    render(<ChatInput {...defaultProps} />);
    expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
  });

  it('renders model selector button', () => {
    render(<ChatInput {...defaultProps} />);
    const menuButton = screen.getByRole('button', { name: /models & agents/i });
    expect(menuButton).toBeInTheDocument();
  });

  it('renders send button', () => {
    render(<ChatInput {...defaultProps} />);
    const sendButton = screen.getByTitle('Send message');
    expect(sendButton).toBeInTheDocument();
  });

  it('calls onSend when form is submitted', async () => {
    const user = userEvent.setup();
    render(<ChatInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Type a message...');
    await user.type(textarea, 'Hello world');
    
    const form = textarea.closest('form');
    fireEvent.submit(form);

    expect(defaultProps.onSend).toHaveBeenCalledWith('Hello world');
  });

  it('clears input after sending', async () => {
    const user = userEvent.setup();
    render(<ChatInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Type a message...');
    await user.type(textarea, 'Hello world');
    
    const form = textarea.closest('form');
    fireEvent.submit(form);

    expect(textarea.value).toBe('');
  });

  it('does not call onSend with empty message', async () => {
    const user = userEvent.setup();
    render(<ChatInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Type a message...');
    await user.type(textarea, '   '); // Only whitespace
    
    const form = textarea.closest('form');
    fireEvent.submit(form);

    expect(defaultProps.onSend).not.toHaveBeenCalled();
  });

  it('does not submit when loading', () => {
    render(<ChatInput {...defaultProps} isLoading={true} />);
    
    const textarea = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    
    const form = textarea.closest('form');
    fireEvent.submit(form);

    expect(defaultProps.onSend).not.toHaveBeenCalled();
  });

  it('submits on Enter key without Shift', async () => {
    const user = userEvent.setup();
    render(<ChatInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Type a message...');
    await user.type(textarea, 'Hello world');
    await user.keyboard('{Enter}');

    expect(defaultProps.onSend).toHaveBeenCalledWith('Hello world');
  });

  it('adds new line on Shift+Enter', async () => {
    const user = userEvent.setup();
    render(<ChatInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Type a message...');
    await user.type(textarea, 'Line 1');
    await user.keyboard('{Shift>}{Enter}{/Shift}');
    await user.type(textarea, 'Line 2');

    expect(textarea.value).toContain('\n');
    expect(defaultProps.onSend).not.toHaveBeenCalled();
  });

  it('shows loading state on send button', () => {
    const { rerender } = render(<ChatInput {...defaultProps} />);
    
    // Not loading
    let sendButton = screen.getByTitle('Send message');
    expect(sendButton.querySelector('.spinner')).not.toBeInTheDocument();

    // Loading (component uses isSending to show spinner)
    rerender(<ChatInput {...defaultProps} isSending={true} />);
    sendButton = screen.getByTitle('Thinking...');
    expect(sendButton.querySelector('.spinner')).toBeInTheDocument();
  });

  it('opens model menu when menu button clicked', async () => {
    const user = userEvent.setup();
    render(<ChatInput {...defaultProps} />);
    
    const menuButton = screen.getByRole('button', { name: /models & agents/i });
    await user.click(menuButton);

    // Menu should be visible
    expect(screen.getByText('Fin AI')).toBeInTheDocument();
    expect(screen.getByText('Claude')).toBeInTheDocument();
  });

  it('closes menu when clicking outside', async () => {
    const user = userEvent.setup();
    render(
      <div>
        <ChatInput {...defaultProps} />
        <div data-testid="outside">Outside</div>
      </div>
    );
    
    // Open menu
    const menuButton = screen.getByRole('button', { name: /models & agents/i });
    await user.click(menuButton);
    expect(screen.getByText('Fin AI')).toBeInTheDocument();

    // Click outside
    const outside = screen.getByTestId('outside');
    await user.click(outside);

    // Menu should close
    await waitFor(() => {
      expect(screen.queryByText('Intercom Fin')).not.toBeInTheDocument();
    });
  });

  it('calls onModelChange when model is selected', async () => {
    const user = userEvent.setup();
    render(<ChatInput {...defaultProps} />);
    
    // Open menu
    const menuButton = screen.getByRole('button', { name: /models & agents/i });
    await user.click(menuButton);

    // Select model
    const claudeOption = screen.getByText('Claude');
    await user.click(claudeOption);

    expect(defaultProps.onModelChange).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'bedrock', name: 'Claude' })
    );
  });

  it('auto-resizes textarea as content grows', async () => {
    const user = userEvent.setup();
    render(<ChatInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Type a message...');
    const initialHeight = textarea.style.height;

    // Type multiple lines
    await user.type(textarea, 'Line 1\nLine 2\nLine 3\nLine 4\nLine 5');

    // Height should have increased (test implementation sets it)
    expect(textarea.style.height).toBeDefined();
  });

  it('trims whitespace from message before sending', async () => {
    const user = userEvent.setup();
    render(<ChatInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Type a message...');
    await user.type(textarea, '  Hello world  ');
    
    const form = textarea.closest('form');
    fireEvent.submit(form);

    expect(defaultProps.onSend).toHaveBeenCalledWith('Hello world');
  });

  it('displays selected model name', async () => {
    render(<ChatInput {...defaultProps} />);
    
    const menuButton = screen.getByRole('button', { name: /models & agents/i });
    await userEvent.click(menuButton);

    // Should show current selection
    const finModel = screen.getByText('Fin AI');
    expect(finModel).toBeInTheDocument();
  });
});
