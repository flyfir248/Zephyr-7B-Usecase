import os
import chainlit as cl
from langchain.llms import CTransformers
from langchain import PromptTemplate, LLMChain

local_llm = "zephyr-7b-alpha.Q8_0.gguf"  # local model in the same directory

config = {
    "max_new_tokens": 1024,
    "repetition_penalty": 1.1,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 0.9,
    "stream": True,
    "threads": int(os.cpu_count() / 2)
}
# This parameter limits the maximum number of newly generated tokens in the output, ensuring the response does not exceed a certain length, in this case, 1024 tokens.

# 1.1 standard penalty
# This setting discourages the model from generating repeated phrases by penalizing the probability of generating the same token again, with 1.1 being a moderate penalty factor.

# want it to be creative
# The temperature parameter controls the randomness of the generated output; lower values like 0.5 make the output more focused and deterministic, whereas higher values introduce more randomness, making the output more creative and diverse.

# specifies the number of top elements or results to consider in a given operation, such as limiting vocabulary in text generation or selecting top recommendations in recommendation systems.

# This parameter in language modeling refers to nucleus sampling, where the model generates words until the cumulative probability of the next word reaches 90%.

# This setting enables continuous streaming of data or results, typically used in scenarios where real-time processing and output are required without waiting for the entire computation to complete.

# This parameter sets the number of threads to be used for parallel processing, utilizing half of the available CPU cores to optimize computational efficiency.


llm_init = CTransformers(
    model=local_llm,
    model_type="zephyr",
    lib="avx2",
    **config
)

template = """Question: {question}

Answer: Please refer to factual information and don't make up fictional data/information.
"""

@cl.on_chat_start
def main():
    prompt = PromptTemplate(template=template, input_variables=['question'])
    llm_chain = LLMChain(prompt=prompt, llm=llm_init, verbose=True)
    cl.user_session.set("llm_chain", llm_chain)

@cl.on_message
async def main(message: str):
    llm_chain = cl.user_session.get("llm_chain")
    res = await llm_chain.acall(message, callbacks=[cl.AsyncLangchainCallbackHandler()])
    await cl.Message(content=res["text"]).send()
