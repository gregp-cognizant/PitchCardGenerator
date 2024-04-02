1. Introduction

What is Prompt Engineering?

Prompt engineering is the craft of designing, optimizing, and interfacing prompts to effectively utilize Large Language Models (LLMs) for various applications such as question answering and arithmetic reasoning. It encompasses a broad spectrum of skills, enabling enhanced interaction, development, and improvement of LLMs, thereby unlocking new capabilities and improving safety and robustness in their usage.




You can follow the basic structure below on how to create a prompt.

(General Tips on how to Design a Prompt)[https://www.promptingguide.ai/introduction/tips]

```python

def get_prompt():

prompt = """

###Instructions###

You are {chatbot_name}, an HR Department Assistant/Customer Support for Cognizant.
Communicate as if you are a Cognizant employee by using pronouns such as I, we, and Cognizant.
Your tone should be friendly, professional, and patient.

If the user asks questions which do not relate to the topics included in the provided [knowledge base],
politely decline to answer and state the topic is not related to the materials.

Do not engage in any other conversation unrelated to your role as an HR department assistant for topics outside the [knowledge base].

If you get questions about other companies, products, or services that are not related to your expertise, politely decline them and

inform them that you can only help by being an HR department assistant.

###End Instructions###

###knowledge base####

Use this information as your [knowledge base]: {knowledge_base}

Always refer to the content in the [knowledge base], adhering to Cognizant’s policies and procedures first before using the Learning Objective.

Include all links and contact information from the knowledge base so the user has more context and can request extra help.

When asked to create documents or respond to inquiries, use the information and format provided in the knowledge base, including but not limited to official policies, procedures, and approved templates. Do not modify or omit anything from the official documents in the knowledge base.


###End knowledge base###

"""

return prompt

```

To learn more about the basic Prompt Engineering Fundamentals, please refer to the following resources:

(Prompt Engineering Fundamentals)[https://www.promptingguide.ai/introduction]




2. Key concepts and Techniques in Prompt Engineering

- Designing and Developing Prompts

- Techniques to Improve Language Model (LM) Responses

- Optimization Strategies

This link will direct you to the multiple techniques and concepts used in prompt engineering.

(Techniques and Concepts)[https://www.promptingguide.ai/techniques]




3. Interfacing with Large Language Models(LLMs)

This section will provide you with the necessary information to interface with the different LLMs.

- Flan

- ChatGPT

- LLaMa

- GPT-4

- LLM Collection

(Interfacing with LLMs)[https://www.promptingguide.ai/models]




4. Creating Guardrails for LLMs

Crafting effective guardrails is essential for channelizing LLMs towards domain-specific tasks, enhancing their performance. Understanding what to avoid and what to emphasize is crucial in instruction design.

[Check out examples and best practices for creating guardrails](https://www.promptingguide.ai/introduction/tips#to-do-or-not-to-do)

A common tip when designing prompts is to avoid saying what not to do but say what to do instead. This encourages more specificity and focuses on the details that lead to good responses from the model.




Here is an example of a movie recommendation chatbot failing at exactly what I don't want it to do because of how I wrote the instruction -- focusing on what not to do.




**Prompt:**

```The following is an agent that recommends movies to a customer. DO NOT ASK FOR INTERESTS. DO NOT ASK FOR PERSONAL INFORMATION.




Customer: Please recommend a movie based on my interests.

Agent:```




**Output:**

```Sure, I can recommend a movie based on your interests. What kind of movie would you like to watch? Do you prefer action, comedy,

romance, or something else?```




Here is a better way to write the instructions:




**Prompt:**

```The following is an agent that recommends movies to a customer. The agent is responsible to recommend a movie from the top global trending movies. It should refrain from asking users for their preferences and avoid asking for personal information. If the agent doesn't have a movie to recommend, it should respond "Sorry, couldn't find a movie to recommend today.".




Customer: Please recommend a movie based on my interests.

Agent:```




Output:

```Sorry, I don't have any information about your interests. However, here's a list of the top global trending movies right now: [list of movies]. I hope you find something you like!```
