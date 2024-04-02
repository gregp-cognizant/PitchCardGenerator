import { v4 as uuidv4 } from 'uuid';
import { procureMetaData } from '../../src/util/AppUtil';
jest.mock('uuid', () => ({
  v4: jest.fn(() => 'mock-uuid'),
}));

describe('procureMetaData', () => {
  it('returns new metadata when selectedChatHistoryMetaData is not provided', () => {
    const result = procureMetaData(null, 'Agent Smith');
    expect(result).toEqual({
      date: expect.any(String), // We can't know the exact date string, so we just check that it's a string
      chat_history_guid: 'mock-uuid',
      chat_agent: 'Agent Smith',
    });
  });

  it('returns selectedChatHistoryMetaData when it is provided', () => {
    const mockMetaData = {
      date: '2022-01-01T00:00:00Z',
      chat_history_guid: 'existing-uuid',
      chat_agent: 'Agent Smith',
    };
    const result = procureMetaData(mockMetaData, 'Agent Smith');
    expect(result).toEqual(mockMetaData);
  });
});
