import React, { useState } from 'react';

const NewChatForm = ({ handleStartNewChat }) => {
    const [chatAgent, setChatAgent] = useState('AgentFramework');

    const handleChatAgentSelectChange = (event) => {
        setChatAgent(event.target.value);
    }

    const handleStartNewChatClick = () => {
        handleStartNewChat(chatAgent);
    };
    return (
        <div className="config_panel" data-testid="new_chat_form">
            <div>
                <h3>Start New Chat:</h3>
            </div>
            <div>
                <span>Chat Agent: </span>
                <select onChange={handleChatAgentSelectChange} data-testid="chat_agent_select">
                    <option value="AgentFramework">AgentFramework</option>
                    <option value="research_agent">research_agent</option>
                    <option value="CodingWizard">CodingWizard</option>
                    <option value="DralphSoftwareConsultant">DralphSoftwareConsultant</option>
                    <option value="KaiburrCrystalBall">KaiburrCrystalBall</option>
                    <option value="GenAISalesGuru">GenAISalesGuru</option>
                    <option value="medical_billing_agent">medical_billing_agent</option>
                    <option value="no_tools_agent">no_tools_agent</option>
                </select>
                <button data-testid="new_chat_button" className="app-button" onClick={handleStartNewChatClick}>Start New Chat</button>
            </div>
        </div>
    );
}

export default NewChatForm;
