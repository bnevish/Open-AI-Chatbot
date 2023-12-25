import openai
import json
import os

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Mock functions for appointment booking
def greet():
    return "Hello! Welcome to our dental clinic. How can I assist you today?"

def ask_ailment():
    return "What type of ailment are you experiencing?"

def check_available_slots(parameters):
    day = parameters.get("day")
    # Mock logic to check available slots based on the given day
    return f"We have available slots on {day}: 10:00 AM, 11:00 AM, 2:00 PM."

def book_appointment(parameters):
    day = parameters.get("day")
    time = parameters.get("time")
    # Mock logic to book the appointment
    return f"Your appointment on {day} at {time} has been booked successfully."

def run_conversation():
    responses = []
    response = greet()
    responses.append(response)

    while True:
        user_input = input(response + '\n')

        if user_input.lower() == 'exit':
            responses.append("Goodbye!")
            break

        messages = [{"role": "user", "content": user_input}]
        functions = [
            {"name": "greet"},
            {"name": "ask_ailment"},
            {
                "name": "check_available_slots",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "day": {"type": "string", "description": "The day for appointment"}
                    },
                    "required": ["day"]
                }
            },
            {
                "name": "book_appointment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "day": {"type": "string", "description": "The day for appointment"},
                        "time": {"type": "string", "description": "The time for appointment"}
                    },
                    "required": ["day", "time"]
                }
            }
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=functions,
            function_call="auto"
        )

        response_message = response["choices"][0]["message"]
        responses.append(response_message)

        if response_message.get("function_call"):
            available_functions = {
                "greet": greet,
                "ask_ailment": ask_ailment,
                "check_available_slots": check_available_slots,
                "book_appointment": book_appointment,
            }

            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions.get(function_name)

            if function_to_call:
                function_args = json.loads(response_message["function_call"]["arguments"])
                function_response = function_to_call(parameters=function_args)
                responses.append(function_response)
                response = function_response

                # Check if the function response indicates a successful booking
                if "Your appointment" in function_response and "has been booked successfully" in function_response:
                    responses.append("Appointment booked successfully. Exiting...")
                    break  # Exit the loop if appointment booked successfully
            else:
                responses.append("Function not available or defined")
                response = "Function not available or defined"
                break  # Exit the loop if function not available
        else:
            responses.append("No function call found in the response")
            response = "No function call found in the response"
            break  # Exit the loop if no function call found

    print("\n".join(str(r) for r in responses))

# Run the conversation function
run_conversation()