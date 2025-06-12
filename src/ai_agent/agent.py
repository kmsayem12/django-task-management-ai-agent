from langgraph.prebuilt import create_react_agent

from ai_agent import task_tools, init_llm


def get_agent(checkpointer=None):
    llm_model = init_llm()
    agent = create_react_agent(
        model=llm_model,
        tools=task_tools,
        prompt="You are a helpful assistant in managing tasks for a task management application.",
        checkpointer=checkpointer
    )
    return agent
