
example="""
{{#user~}}
max_questions : 4
Current summary:
The interviewee introduced themselves as Jack, they shared their experience working with Python in a udemy course. The interviewer then asks the interviewee about what they learned in the course. 
Last response by interviewer: What did you learn in this Python course?
Interview goals: {Python : {current_state: discussing, key_points:[udemy], questions_asked:3}, Git and Github : [current_state:not discussed, key_points:[], questions_asked:0],  OpenAI API : [current_state:not discussed, key_points:[], questions_asked:0]}

New lines of conversation:
Interviewee response to last question: I learned about OOP in Python and requests module, I also learned about web scraping using BS4.
Interviewer next response: Can you share more details about your experience with the requests module?

New summary:
{{~/user}}

{{#assistant~}}
The interviewee introduced themselves as Jack, Python has been discussed, no need for further questions related to Python. 
Last response by interviewer: Can you share more details about your experience with the requests module?
Interview goals: {Python : {current_state: discussed, key_points:[udemy, requests, bs4, webscraping], questions_asked:4}, Git and Github : [current_state:discussing, key_points:[], questions_asked:0],  OpenAI API : [current_state:not discussed, key_points:[], questions_asked:0]}
{{~/assistant}}
"""

INTERVIEWER_SUMMARIZER_TEMPLATE = """
{{#system~}}
You are a helpful and terse assistant.
{{~/system}}

{{#user~}}
Progressively summarize the lines of conversation provided, adding onto the previous summary returning a new summary.
{{~/user}}

{{#assistant~}}
Ok, I will do that. Let's do a practice round
{{~/assistant}}

"""+example+"""

{{#user~}}
That was great. Lets do another one. Do not use information from the example. 
The points to cover in the interview are: {{interview_goals}}
If noquestions_asked >= max_questions, set current_state as "discussed".
If a state for a point is marked as "discussed" remove all information related to that point from current summary 
and replace it with "(point name) has been discussed, no need for further questions".

max_questions: {{max_questions}}
Current summary:
{{summary}}

New lines of conversation:
{{ new_lines }}

New summary:
{{~/user}}

{{#assistant~}}
{{gen 'result' temperature=0}}
{{~/assistant}}
"""