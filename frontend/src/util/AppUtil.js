import { v4 as uuidv4 } from 'uuid';

function procureMetaData(selectedChatHistoryMetaData, preferredAgent) {

    if (!selectedChatHistoryMetaData) {
      const nowDate = new Date().toISOString()
      const newGuid = uuidv4()
      return {
        date: nowDate,
        chat_history_guid: newGuid,
        chat_agent: preferredAgent,
      }
    } else {
      return selectedChatHistoryMetaData
    }
  }

export { procureMetaData }
