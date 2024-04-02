# Learn how to use AgentFramework to chat with medical billing codes

This guide will show you a real enterprise use case for a tool like AgentFramework. In this guide we will find the 2024 medical billing codes, embed those and store them in a vector store, then do some prompt engineering to show how a medical biller might be able to use a tool like this to improve their workflow.

## Glossary

You may be unfamiliar with some terms in this example exercise. As you work through the exercise you can come back here for more info about a term.

* **RAG (Retrieval Augmented Generation)**: Retrieval-augmented generation (RAG) is a technique for enhancing the accuracy and reliability of generative AI models with facts fetched from external sources. [Source](https://towardsdatascience.com/rag-retrieval-augmented-generation-improving-openai-gpt-3-with-retrieval-9e14e0b16c51)
* **LLM (Large Language Model)**: A large language model is a type of language model notable for its ability to achieve general-purpose language understanding and generation. [Source](https://www.techtarget.com/search/enterprise-ai/applied-ai-and-machine-learning/large-language-model)
* **Vector Store**: A vector database is a specialized storage system designed to efficiently handle and query high-dimensional vector data, commonly used in AI and machine learning applications for fast and accurate data retrieval. [Source](https://www.mongodb.com/glossary/vector-database)
* **Prompt Engineering**: Prompt engineering is the process of structuring text that can be interpreted and understood by a generative AI model. A prompt is natural language text describing the task that an AI should perform. [Source](https://www.openai.com/blog/prompt-engineering/)

## Getting Setup

First, ensure you've got AgentFramework up and running. We will be using:

* The chat UI: <http://localhost:3000>
* The OpenAPI UI for an easy way to use the API for document processing: <http://localhost:8000/docs>

## Get familiar with the medical billing codes use case

Here are the [2024 ICD-10-CM](https://www.cms.gov/medicare/coding-billing/icd-10-codes/2024-icd-10-cm). This .gov site provides a 120 page document on how to use the billing codes as well as several text files containing lists of nearly 100000 codes. The files we will need for this example have already been placed in the repo here: `/docs/files/medical-billing-exercise.` The lists of codes have been significantly reduced for the purposes of this exercise, as processing such large files can get expensive quickly.

Medical billers must sift through these nearly 100,000 medical billing codes to select the correct code for a visit. Open up [/docs/files/medical-billing-exercise/icd10cm_order_2024.txt](/docs/files/medical-billing-exercise/icd10cm_order_2024.txt) to get an idea of what these codes look like. As you can see, finding the right code is no small task. We've specifically cut down the nearly 100,000 line list to under 900 lines, focusing mostly on knee issues and burns. Imagine you went in for a doctors visit about knee pain after a workout mishap, could you pick out the right code?

### So how will we use Gen AI to help?

We will use a process called RAG (Retrieval Augmented Generation) to more quickly find the correct billing code. Essentially, we will give the LLM the ability to read the entire list of codes, a shorter subset for our example, but it could easily be all 100,000 billing codes. Then we use a chat interface to ask the LLM to lookup the right codes for us. We will also give the LLM the 120 page PDF on Coding Guidelines, this way if the LLM is confused on how to use a code, it can go read the guidelines itself. We will do all this with the functionality already build into AgentFramework.

If you are following along with the Gen AI Training course, this exercise is designed to show you *the art of the possible*, later in the course you will learn all the steps needed to build this sort of solution yourself.

![What is RAG image](/docs/images/rag-basic-architecture.webp)

> *Above - Simple architecture of a RAG application. In our case, we are using OpenAI's GPT-4 as the LLM, hosted in Azure. [Source](https://towardsdatascience.com/rag-vs-finetuning-which-is-the-best-tool-to-boost-your-llm-application-94654b1eaba7)*

## Process the billing documents

The first step is to give the LLM access to read the documents in question. We will do this by embedding the documents and storing them in a vector store *(reference the glossary for more info on embedding and vector stores)*. If you are unfamiliar with these technologies that's no issue, the Gen AI training course will dive into them later or you can go do some Googling yourself before you proceed.

### Run the document processing

We've already got the files downloaded and committed to the repo here `docs/files/medical-billing-exercise`, so no need for you to download them.

Now lets use the OpenAPI webpage to tell AgentFramework to embed and store these into the vector store.

#### First, navigate to: <http://localhost:8000/docs>

#### Now, open up process documents as shown in the gif

![Open process docs](/docs/images/open-process-documents.gif)

#### Next, update the path to where our medical billings docs are at:

Change the following 2 parameters in the API request body:

> source_dir: `/app/docs/files/medical-billing-exercise`
> move_after_processing: false

This path is inside of the docker container, you don't need to worry about this for the current example, but if you want to process docs of your own you'll have to make sure they get mounted to the API container's file system. The move after processing parameter set to false tells AgentFramework to leave our files where they are.

![](/docs/images/Process-medical-billing-codes-execute.png)

### Chat with the codes

Let's validate the LLM really does have access to the medical billing codes now.

Open up the chat UI <http://localhost:3000/> and ask it:
> "You have a subset of the 2024 ICD-10-CM as well as the FY 2024 ICD-10-CM Coding Guidelines (PDF) in the techdocs vector store. Look at these documents and give me some examples of the kind of information you can retrieve."

If you check the terminal where you've run the container, you can see how AgentFramework actually thinks through the question and will run queries against the vector store. AgentFramework is going to take its time on this one, so it may take a minute to respond..

Next up, try asking this:

> "What is the code for a meniscus tear? You have the ICD-10-CM codes in the techdocs vector store. Make sure to quote the code exactly."

Tech docs will query the vector store and should come back with a random sample of codes. These responses might be a bit underwhelming, but they should give you a good idea of the underlying capabilities. AgentFramework is written as a generalist, you can spend time tweaking the various prompts to make it much better.

#### Let's try some basic prompt engineering

Click the `Start new chat` button to get a fresh start.

Your first message will use some basic prompt engineering techniques to improve the utility of the tool for medical billers, setting up the chat.

> "You are an experienced medical biller helping me to determine the correct billing code to use. You will work with me 1 step at a time, asking as many questions as needed, breaking things down step by step until we arrive at the correct code. In the techdocs vector store you have FY 2024 ICD-10-CM Coding Guidelines (PDF) and the list of 2024 ICD-10-CM billing codes. Start the chat by asking me the needed questions so you can find the right code."

Next ask:

> "I have a patient who's come to the doctor for a first visit about knee pain. The doctor has determined it is likely a meniscus tear and has recommended the patient go to PT. What code should I use?"

You'll get a response similar to the one in my screenshot.

![](/docs/images/chat-about-billing-codes.png)

Let's keep going and see if we can get the response to look a bit better.

> "Make this more readable by breaking it out and using markdown"

> "Ask me specific question to help me figure out exactly which code to use."

## Save Your Agent

Now that you've engineered an agent in the prompt, let's save it by creating a custom agent.

Reference the [Make a new chat agent guide](/docs/make-new-chat-agent.md) to save your agent and be able to pick it from the agent selector in the GUI.

#### Now it's your turn!

Start a new chat, tweak the prompts a bit and try asking AgentFramework for help with some contrived scenarios. See how it does and if you can get the outputs to be better just by tweaking your prompts. The vector store has most of the codes related to knee issues and burns but not much else, so watch out for it not having the right codes.

Here is my next tweaking of the prompt:
> "You are an experienced medical biller helping me to determine the correct billing code to use. You will work with me 1 step at a time, asking as many questions as needed one at a time, breaking things down step by step until we arrive at the correct code. In the techdocs vector store you have FY 2024 ICD-10-CM Coding Guidelines (PDF) and the list of 2024 ICD-10-CM billing codes. Start the chat by asking me the needed questions so you can find the right code. Ask me specific question to help me figure out exactly which code to use. If you are not 100% certain, list out all possible codes and keep iterating with the user. Always reply in markdown."


#### What's next?

The example is done now but it's useful to think how we might help a client delivery this in the real world. Here are the first things I'd do. Can you think up any other ideas for improving the tool?

* Start by writing a custom tool for medical code retrieval with better prompting. This can be done in `/backend/src/tools/setup.py`.
* Specify that this agent is specifically deigned for medical code retrieval and should iteratively work with the user to find the correct code by editing the base prompts for the agent found in: `/backend/src/template`
* Use prompt engineering to ensure the agent is working iteratively with the user to find the right code and confirm it is correct
* Give the agent another tool specifically for retrieving and displaying exact lines from the medical billing codes file. This way, the LLM has no chance to hallucinate, but instead finds the appropriate line or lines and serves them directly to the user. This could possibly be coupled with a link to some other tool designed to display all the billing codes.
