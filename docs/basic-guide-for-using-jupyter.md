# Basic Guide for Using Jupyter Notebooks

The Gen AI training course leverage Jupyter notebooks at some points for training materials.

> The Jupyter Notebook is a web-based interactive computing platform. The notebook combines live code, equations, narrative text, visualizations, interactive dashboards and other media.


## Launch Jupyter Notebooks

When you startup AgentFramework with `make run` Jupyter notebooks also spins up in a container.

Jupyter requires a Password/Token which is generated at startup in order to be opened. Run `docker-compose logs jupyter` and scroll to top the of logs to see this token. Ctrl+f for a log line saying `is running at:` and then Ctrl+click on the url `127.0.0.1:8888/lab?token-abcdefg12345....`

This screenshot shows what the logs should looks like:
![](/docs/images/open-jupytr.png)

## What to do once you are in Jupyter

We have a series of lessons and starters in Jupyter. Let's start by trying out the most simple starter.

In the left-hand side, you have a file browser. Make you are scoped to the root directory and double click `basic-azure-openai-api-use.ipynb` to open it.

### Running code in a notebook

The steps below show the basic process of running code in a notebook:
![](/docs/images/Basic-Use-of-Jupyter.webp)

First, we will run the code as is, then we will try editing it.

We need to make sure we start at the top:
* Select the first cell and click the run arrow in the menu bar at the top of the pane
* Notice that the next cell is now highlighted, any code in the cell you selected has been run

Run the full notebook:
* Keep clicking run until all the cells have been run
* You should now see some output. We've called the Azure OpenAI API chat completion endpoint and gotten a response

Try editing the code:
* In the last cell, instead of *Translate the following English text to French* put *Translate the following English text to Spanish*
* Click the run button again

That's all there is too it. You can write and execute any python code right from this interface. When you save the code, it'll get versioned in the Git repo.

## Using Jupyter to do Gen AI Learning Course Exercises

Jupyter is a convenient way to do many of the coding exercises in the learning course. Follow these instructions to best organize your work:

* In `/Learning-Exercises-Scratch-Space/` make any files you wish
* There is a .gitignore on this directory to prevent any work done in here from being committed
* Organize your work however you wish in this directory


## Using AgentFramework Jupyter to Test LangChain and LLama_Index docs

Much of the LangChain and Llama_Index docs are written as Jupyter notebooks.

### Example copying a Llama_Index notebook into our localhost Jupyter

#### First, download the notebook and save it into Jupyter's directory
This page of the llama_index docs is about making a basic Q&A bot over documents put into a vector store. <https://docs.llamaindex.ai/en/latest/understanding/putting_it_all_together/q_and_a.html#>

You'll notice near the top they have a section for guides. Click on the Notebook link.

The notebook is here in GitHub for Llama_Index, you can navigate the file structure to find many other example notebooks. <https://github.com/run-llama/llama_index/blob/main/docs/examples/vector_stores/SimpleIndexDemo.ipynb>

Click on the download button which is in the top right of the code pane, download the file into the git repo into `jupyter/src/Learning-Exercises-Scratch-Space`

Now in Jupyter you should be able to open up and the notebook.

#### Update the standard OpenAI API setup code for our Azure OpenAI code

Just copy our setup code form the beginning of any of the other Jupyter notebooks and replace their key setup cell.
