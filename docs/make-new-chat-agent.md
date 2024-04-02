# How to make a new chat agent

## Create a new agent template

In the [/backend/src/template](/backend/src/template) dir, clone one of the existing agents, such as AgentFramework, by duplicating the directory and renaming it to your desired name, such as `billing_agent`. You will see we already have a `medical_billing_agent` and several other examples in here.

You must create a `prefix.txt`. You can optionally update several other files txt files used to build the final prompt, but if you don't have a good reason to change these, best not to create them in your new agent. Default values will be assumed.

Likely you'll want to create a `config.json` to specify a custom list of tools, otherwise your bot will use the default tools list.

* `prefix.txt`
* `config.json` (*optional*)
* `react_cot.txt` (*optional*)
* `suffix.txt` (*optional*)

![Copy the dir](/docs/images/create-new-agent-guides/clone-agent-dir.png)

If you are creating a prompt from scratch, reference some of the other prompt templates for good patterns. Importantly, notice how they all end with something like `You have access to the following tools:`. You will likely want to add something along these lines to your prompt as well, this will improve you agent's tool usage as the LangChain tools are inserted into he prompt right after the prefix.txt

## Update GUI to add the new agent to the dropdown list

*Note: There is a backlog item to create an API for listing available agents and using this to populate the GUI [kanban item](https://github.com/orgs/Tech-Modernization/projects/35/views/1?pane=issue&itemId=50308429)*

Now you'll want to add your new agent to the list of agents available in the GUI.

Open up [/frontend/src/components/NewChatForm.jsx](/frontend/src/components/NewChatForm.jsx) and look for `Chat Agent: ` with ctrl+f. Update this list with the exact name of the new folder you made for your agent.

![Add a new agent to GUI](/docs/images/create-new-agent-guides/add-new-agent-to-gui.png)

## Test the new agent

Finally, you will need to restart the API and UI to pickup your new agent.

The API can be hot reloaded by opening any .py file in the `/backend/` and saving it with no changes to trigger a hot reload.

Now you can refresh the UI and you should see your new agent.

You should select your agent from the dropdown, as shown in the screenshot, and then start a new chat to being testing.

![Select new agent from dropdown](/docs/images/create-new-agent-guides/select-new-agent-from-dropdown.png)
