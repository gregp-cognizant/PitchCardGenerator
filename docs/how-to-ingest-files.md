# How to Ingest Data Into a New Collection

In this guide we will cover ingesting files into the AgentFramework for RAG.

There are two ways you might ingest files.

1. Into the default techdocs collection
    * This is useful when ingesting general documents you want to be able to RAG over
    * Ideal for creating pair programming partners over docs
    * Ideal for chatting over large sets of documentation
    * No need to create custom agents to interface with new data

2. Into a new collection
    * You will make a specific collection for your data, not mixing it with everything else ingested into techdocs
    * Ideal for client demos, segmented data makes it easy to have a stable PoC type demo
    * Useful for increasing retrieval accuracy over a static set of files, not chance of getting file ingested for another purpose
    * Allows for exporting and sharing of collection for specific use cases, such as client demos

If you aren't already familiar with qdrant and vector stores, you can think of a collection like a table. Do you want your data in an existing store, or segregated off on it's own.

## Instructions for Ingestion

In these instructions we will use a set of Cognizant Gen AI sales materials as examples.

1. Look for the `src/scraper/scraped_data/filedrop` directory, if it doesn't exist, create it.

2. Create a new directory inside of this directory for your new set of files

3. Inside of the folder, paste the document or documents you want to ingest.

4. Navigate to the OpenAPI spec page at `http://localhost:8000/docs`, then go to the `POST /process-documents/` endpoint.

5. Change the `source_dir` to the path of where you created that folder, use the example below:

  ```bash
  src/scraper/scraped_data/filedrop
  ```

  * *Optionally: change the `collection_name` from the default, only do this if you have a good reason and understand why you are doing it, otherwise just stick with techdocs.*

    ```bash
    {
      "source_dir": "src/scraper/scraped_data/filedrop",
      "collection_name": "cog_gen_ai_sales_materials",
      "move_after_processing": false,
      "re_process_files": false,
      "extensions_to_process": [
        ".md",
        ".pdf",
        ".docx",
        ".txt",
        ".pptx"
      ]
    }
    ```

6. Click execute and you should see a response of `200` and the list of successfully processed files

7. The default agents will now have access to this data, if you put it into the techdocs collection. You may start a new chat, tell the bot it has xyz data in `techdocs`, and ask questions about it
    * Note: If you put your data into another collection then the default agents will not see it. You will need to make a new tool to give access to this data.
    * (Optional): You may further refine the usage of your data by creating a new tool or updating an existing tool to give context to the LLM what data you ingested. For more details about that, check the [How to Create a New RAG Agent with a Separate Collection](docs/create-a-new-rag-agent-with-custom-data-store.md) docs, which discuss create a new agent with a new tool. You can create a new tool and simply assign it to an existing agent, or create a whole new specialized agent.
