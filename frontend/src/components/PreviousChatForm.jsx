import React from 'react';

const PreviousChatForm = ({ selectedChatHistoryMetaData, handleSelectChatHistoryChange, chatHistoryList }) => {
  return (
    <div className="config_panel" data-testid="previous_chat_form">
      <h3>Resume Previous Chat: </h3>
      <select data-testid="chat_history_select"
          value={selectedChatHistoryMetaData ? selectedChatHistoryMetaData.chat_history_guid : ''}
          onChange={handleSelectChatHistoryChange}
        >
          <option value="" disabled>Pick a previous chat to resume</option>
          {chatHistoryList.map((item, index) => {
            const value = item.chat_history_guid;
            const label = `${item.date } | ${item.chat_agent } | ${item.chat_history_guid}`;

            return (
              <option key={index} value={value}>
                {label}
              </option>
            );
          })}
      </select>
    </div>
  );
}

export default PreviousChatForm;
