from euriai.langchain import create_chat_model

def get_chat_model(api_key:str):
    return create_chat_model(api_key=api_key,model="gpt-4.1-nano",temperature=0.7)

def ask_chat_model(model,query:str)->str:
    response = model.invoke(query)
    return response.content

