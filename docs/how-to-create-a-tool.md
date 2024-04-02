# How to Add a Third Party Tool

In this document we will provide 3 examples:

* How to add a new tool for doing RAG over a collection other than techdocs

* How to add a new tool for allowing the Agent to make Google search

* How to create a static data tool which always returns a predefined string

## Create a New Tool for Retrieving Data From a New Collection

This pattern is useful for creating new agents designed to RAG over specific data sets. The example we will continue from the [how to ingest files](/docs/how-to-ingest-files.md) docs is for creating an agent which chats about Cognizant Gen AI offerings.

Before following along, make sure you've created a new qdrant collection by reading: [how to ingest files](/docs/how-to-ingest-files.md) and following the section for creating a new collection.

### How to Create a New Tool to Query Data Ingested Into a New Collection

* Navigate to the [/backend/src/tools/setup.py](/backend/src/tools/setup.py) file

* Duplicate one of the existing vector store query tools in the `tools_available` array and point it to your new collection

    ```python
    # Existing search tool
    Tool(
        name="search_techdocs",
        func=lambda query: search_qdrant(query=query, collection="techdocs"),
        description="This tool enables the querying of a specialized vector store named [’techdocs’] a repository with valuable technical documentation...",
    ),
    # New Search Tool
    Tool(
        name="search_cognizant_gen_ai_sales_materials",
        func=lambda query: search_qdrant(query=query, collection="cog_gen_ai_sales_materials"),
        description="Useful for searching through Cognizant's Gen AI sales materials. Gives access to a vector store containing documents explaining Cognizant's Gen AI offerings, use cases for Gen AI, and more.",
    ),
    ```

### Give the New Tool to an Agent

Now the tool is made, you must configure an agent to use the new tool:

* Navigate to [/backend/src/template](/backend/src/template) and open the directory for the agent you'd like to give this new tool to
* Open the config.json file for that agent
* Add the exact name of the new tool to the `agent_tools_names` list
  * Example:
  ```yaml
    {
        "agent_tools_names": [
            "search_cognizant_gen_ai_sales_materials"
        ]
    }
  ```
* Restart the API container with `docker compose restart fastapi` and the agent should now have access to your new tool

## Creating a Google Search Engine Tool using SerpApi

For this example we will be adding the Google search engine tool using [SerpApi](https://serpapi.com/). SerpApi is a tool which sits between the various Google search APIs and makes them easier to use. SerpApi provides a free tier which you will be using.

### Initial setup

* Obtain a SerpApi key. You can get one here [SerpApi](https://serpapi.com/)
* Add your API key in the [/key.env](/key.env) file on the `SERPAPI_API_KEY=` line

### Create a LangChain tool for SerpApi

[LangChain](https://python.langchain.com/docs/get_started/introduction) is the framework we are using to give LLMs "tools." Allowing LLMs to interface with the outside world for tasks such as doing web searches, querying databases, using APIs, etc.

* Go to the [/backend/src/tools/setup.py](/backend/src/tools/setup.py) file.
* Find the Tools list and add this tool:

    ```python
    Tool(
        name="search_google",
        func=search_google,
        description="""This is a tool that conducts Google searches via the SerpAPI to retrieve real-time search
        results programmatically, allowing for efficient extraction and analysis of search data to obtain current
        and relevant web information for a given query."""
    ),
    ```

* The Google search tool is defined previously in the same setup.py file called `search_google`. We are adding this tool to the tools array so the agents can access it.

### Give the New Tool to an Agent

Now the tool is made, you must configure an agent to use the new tool:

* Navigate to [/backend/src/template](/backend/src/template) and open the directory for the agent you'd like to give this new tool to
* Open the config.json file for that agent
* Add the exact name of the new tool to the `agent_tools_names` list
  * Example:
  ```yaml
    {
        "agent_tools_names": [
            "search_techdocs",
            "search_google"
        ]
    }
  ```
* Restart the API container with `docker compose restart fastapi` and the agent should now have access to your new tool

#### Implement Other Tools Which Call 3rd Party APIs

You can follow that same format for any other third party tool like Wolfram alpha. Here is a list of third party tools you can use [Third Party Tool list](https://python.langchain.com/docs/integrations/tools)

![Picture of LangChain tools list](/docs/images/how-to-create-a-tool/LangChain-tools-list.png)

## How to Create a Static Data Tool

Imagine you have a set of data which you know remain the same for a long period of time. You may want to hard code this into a tool. This can be quite useful for testing purposes. This example demonstrates how to do that.

*Note: To make this production ready, you could expand on this to retrieve that data from some other data source, such as a DB, to retrieve up to date data from a specific source.*

1. Create a function that returns static data. In the example below it returns a string for prices of textbooks.

    ```python
        def get_pricing_data(query: str) -> str:
            PRICING_DATA = """
            The following is a list of prices for textbooks:
            1. Bronze Health Plan: $200
            2. Silver Health plan: $500
            3. Gold Health Plan: $1000

        return PRICING_DATA
        """
    ```

2. Go to the [/backend/src/tools/setup.py](/backend/src/tools/setup.py)

3. Add this to the following tool list

```python
    Tool(
    name="Pricing_Tool",
    func=lambda _: PRICING_DATA,
    description="use this tool for any pricing of related questions on the workout plan",
    return_direct=True,
    ),
```

4. Now the tool is made, you must configure an agent to use the new tool
    * Navigate to [/backend/src/template](/backend/src/template) and open the directory for the agent you'd like to give this new tool to
    * Open the config.json file for that agent
    * Add the exact name of the new tool to the `agent_tools_names` list
        * Example:
        ```yaml
        {
            "agent_tools_names": [
                "search_techdocs",
                "Pricing_Tool"
            ]
        }
        ```

5. Restart the API container with `docker compose restart fastapi` and the agent should now have access to your new tool
