import React, { useState, useEffect } from 'react';
import { ErrorBoundary } from 'react-error-boundary'
import Chat from './components/Chat';
import './css/App.css';
import NewChatForm from './components/NewChatForm';
import PreviousChatForm from './components/PreviousChatForm';
import { procureMetaData } from './util/AppUtil';


const chat_history_url = "http://localhost:8000/chat/history/"

function App() {
  // new chat state
  const [activeChatAgent, setActiveChatAgent] = useState(null);

  // chat history state
  const [chatHistoryList, setChatHistoryList] = useState([])
  const [selectedChatHistoryMetaData, setSelectedChatHistoryMetaData] = useState()
  const [selectedChatHistoryData, setSelectedChatHistoryData] = useState({});

  // Common function to fetch chat history data
  const fetchChatHistoryData = () => {
    fetch(chat_history_url)
      .then(response => response.json())
      .then(data => {
        if (data && data.chat_history_metadata && data.chat_history_metadata.length) {
          setChatHistoryList(data.chat_history_metadata);
        }
      })
      .catch(error => console.error('Error:', error));
  }

  const handleStartNewChatButtonClick = (chatAgent) => {
    setSelectedChatHistoryMetaData(null)
    setSelectedChatHistoryData({})
    setActiveChatAgent(chatAgent);
    fetchChatHistoryData();
  };

  // get chat history list of metadata
  useEffect(() => {
    fetchChatHistoryData();
  }, []);

  // get chat history data by guid
  useEffect(() => {
    if (selectedChatHistoryMetaData && selectedChatHistoryMetaData.chat_history_guid) {
      fetch(chat_history_url + "?chat_history_guid=" + selectedChatHistoryMetaData.chat_history_guid)
        .then(response => response.json())
        .then(data => {
          if (data) {
            setSelectedChatHistoryData(data);
          }
        })
        .catch(error => console.error('Error:', error));
    }
  }, [selectedChatHistoryMetaData]);

  const handleSelectChatHistoryChange = (event) => {
    const selectedObject = chatHistoryList.find(item => item.chat_history_guid === event.target.value);
    setSelectedChatHistoryMetaData(selectedObject);
  };

  return (
    <div className="App">
      <div className="info-panel">
        <h1>AgentFramework</h1>
        <div>
            <NewChatForm handleStartNewChat={handleStartNewChatButtonClick}/>
            <PreviousChatForm
              selectedChatHistoryMetaData={selectedChatHistoryMetaData}
              handleSelectChatHistoryChange={handleSelectChatHistoryChange}
              chatHistoryList={chatHistoryList}
            />
        </div>

      <hr className="solid"></hr>
      </div>
      <ErrorBoundary>
        <Chat
          chatMetaData={procureMetaData(selectedChatHistoryMetaData, activeChatAgent ? activeChatAgent : 'AgentFramework')}
          chatData={selectedChatHistoryData}
        />
      </ErrorBoundary>
    </div>
  );
}

export default App;
