#This Project is created with AI Agent and OpenAI SDK. This project is for creating automated SAles Agent. And using the automated sales agent it will send Message in email format over PushOver.

#Important Concepts:
#1. Creating Agent using OpenAI SDK
#2. Creating multiple Sales agent and selecting the best email from generated from the 3 agents and sending it over Pushover.
#3. It will use Tool and Agent as tool concepts


from dotenv import load_dotenv
import os
import openai
from agents import Agent, Runner, trace, function_tool
import requests
import asyncio
from bs4 import BeautifulSoup

load_dotenv(override = True)
openai_client = os.getenv("OPENAI_API_KEY")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

async def push(message):
    payload = {"user":pushover_user, "token":pushover_token, "message":message}
    requests.post(pushover_url, data=payload)
    print("Pushover Successfull")

@function_tool
async def send_push_alert(message: str):
    "Send the email using Pushover as Push Notification"
    push_message = BeautifulSoup(message, "html.parser").get_text()
    print(push_message)
    await push(push_message)

instruction1 = f"""You are a very efficient Sales Person. You have to draft an email for sale of a product specified by user.\
    You have to draft a cold email in a very casual format providing all required detail for the product specified by user. Use all general property of the product.\
    Your email body should not be more than 5 lines. The signature should be polite. The email should be addressed as Dear User.\
    Be very polite and draft an email."""

instruction2 = f"""You are a very efficient Sales Person. You have to draft an email for sale of a product specified by user.\
    You have to draft a cold email in a very professional format providing all required detail for the product specified by user. Use all general property of the product.\
    Your email body should not be more than 5 lines. The signature should be polite. The email should be addressed as Dear User.\
    Be very polite, Very professional and draft a crisp email."""

instruction3 = f"""You are a very efficient Sales Person. You have to draft an email for sale of a product specified by user.\
    You have to draft a cold email in a format such that it becomes most likely for a customer to respond providing all required detail for the product specified by user. Use all general property of the product.\
    Your email body should not be more than 5 lines. The signature should be polite. The email should be addressed as Dear User.\
    Be very polite, Very professional and draft a crisp email."""


sale_agent1 = Agent(
    name = "Sales Agent 1",
    instructions = instruction1,
    model = "gpt-5.4-mini"
)
sale_agent2 = Agent(
    name = "Sales Agent 2",
    instructions = instruction2,
    model = "gpt-5.4-mini"
)
sale_agent3 = Agent(
    name = "Sales Agent 3",
    instructions = instruction3,
    model = "gpt-5.4-mini"
)

description = "Write an email"
tool1 = sale_agent1.as_tool(tool_name= "Agent1", tool_description=description)
tool2 = sale_agent2.as_tool(tool_name= "Agent2", tool_description=description)
tool3 = sale_agent3.as_tool(tool_name= "Agent3", tool_description=description)

tools = [tool1, tool2, tool3]

#Now, create a Sale_Manager agent that will use all the above tool. It will generate three emails and select the best email out of it. The agent will use tool to convert the best email from plain email to html email. It will return the email which will then be sent as a pushover notification.

Subject_agent = Agent(
    name = "Subject writer Agent",
    instructions = "You are a subject writer agent. You have to write a subject for an email.",
    model = "gpt-5.4-mini"
)

subject_tool = Subject_agent.as_tool(tool_name = "Subject_Tool", tool_description = "Write a subject for an email")
email_sender_tool = [subject_tool, send_push_alert]



email_sender_promt = f"""You are a push notification sender agent. You have to use your tools Subject_agent to create a subject for the email.\
    Then you have to use generated subject as heading for the push message and your tool send_push_alert to send the push notification."""



email_sender_agent = Agent(
    name = "Push Notification Sender Agent",
    instructions = email_sender_promt,
    tools = email_sender_tool,
    handoff_description = "Send the push notification to the customer",
    model = "gpt-5.4-mini"
)

handoffs = [email_sender_agent]

Sale_Manager_promt = f""" You are a Sale Manager of a compnay A.K Enterprise. You have a new Product. Take the product name from input message.\
    You have to use your tool to generate sale email for the product. You will generate 3 emails using your 3 different sale_agent tools and then you will select the best of the 3 emails generated.\
    You have to only use your tools to generate your emails and you should not generate it yourself.\
    You have to be very creative and effiecient. But you should only use your tools for generating emails\
    After selecting the best email you will handoff the email to email_sender_agent for generating subject and sending the email or push notification."""

async def launch_manager(product):
    sale_manager = Agent(
        name = "Sales Manager",
        instructions= Sale_Manager_promt,
        tools=tools,
        handoffs=handoffs,
        model ="gpt-5.4-mini"
    )

    messages="Send the sales email as Abhinaw, CEO A.K Enterprises"
    messages += f"Product Name is {product}"

    await Runner.run(sale_manager,messages)

async def main():
    print("Enter the Product Name for Sales Email")
    product_name = input()
    with trace("Sales_Manager_Final"):
        await launch_manager(product_name)

if __name__ == "__main__":
    asyncio.run(main())


