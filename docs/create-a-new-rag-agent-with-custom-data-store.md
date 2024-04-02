# How to Create a New RAG Agent with a Separate Collection

[![](/docs/images/create-new-agent-guides/create-chat-agent-with-your-data-guide-video-thumbnail.png)](https://cognizantonline.sharepoint.com/:v:/r/sites/CommunitiesCognizant/Shared%20Documents/Generative%20AI%20Engineering/Videos/How%20to%20Make%20a%20Chat%20Agent%20with%20Your%20Data%20in%20AgentFramework-20240216_174348-Meeting%20Recording.mp4?csf=1&web=1&e=72edP5&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D)

[Video Guide for how to make a chat agent with your data in agentFramework](https://cognizantonline.sharepoint.com/:v:/r/sites/CommunitiesCognizant/Shared%20Documents/Generative%20AI%20Engineering/Videos/How%20to%20Make%20a%20Chat%20Agent%20with%20Your%20Data%20in%20AgentFramework-20240216_174348-Meeting%20Recording.mp4?csf=1&web=1&e=72edP5&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D)

In AgentFramework you can ingest your data into the default techdocs vector store, or you might have cause to create a separate data store for a RAG process. A more specific data store, even with a with a naive ingestion and retrieval process, can have a higher retrieval accuracy.

In this guide we will cover:

* Ingesting files into the vector store collection
* Creating a new tool to target your collection
* Creating a new agent to interface with your data
* Exporting your collection for sharing

## Ingesting your files

As it stands, the only way to ingest files is by copying them into the file system. There is a future work item to create an API for ingesting files, but for now you must copy them into your file system.

### Create a New Collection for Your Data

Follow this guide, ensure that you specify a new collection instead of the default when you run the data ingestion process.

[How to ingest files](/docs/how-to-ingest-files.md)

## Create a New Tool for Searching Through Your New Collection

Follow the [how to create a new tool](/docs/how-to-create-a-tool.md) documentation. Specifically the section for `How to Create a New Tool to Query Data Ingested Into a New Collection`

## Create a new Chat Agent Using Your New Search Tool

Follow the [Make a New Chat Agent](/docs/make-new-chat-agent.md) documentation.
