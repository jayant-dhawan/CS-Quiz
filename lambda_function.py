import requests
import json
import random

def lambda_handler(event, context):
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event, context)
    elif event['request']['type'] == "IntentRequest":
        return intent_router(event, context)


def intent_router(event, context):
    # Custom Intents
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_end(event['request'], event['session'])
    # Required Intents
    if intent == "AMAZON.CancelIntent":
        return cancel_intent()
    if intent == "AMAZON.HelpIntent":
        return help_intent()
    if intent == "AMAZON.StopIntent":
        return stop_intent()


def on_launch(launch_request, session):
    return get_welcome_response()


def on_intent(intent_request, session):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    global name
    if intent_name == "startQuiz":
        return get_welcome_response(intent, session)
    elif intent_name == "modeIntent":
        return modeSelection(intent, session)
    elif intent_name == "AnswerIntent":
        return Answer(intent, session)
    elif intent_name == "AMAZON.YesIntent":
        return on_yes(intent, session)
    elif intent_name == "AMAZON.NoIntent":
        return on_session_ended(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.StopIntent":
        return on_session_ended(intent, session)
    elif intent_name == "AMAZON.CancelIntent":
        return on_session_ended(intent, session)
    elif intent == "SessionEndedRequest":
        return on_session_end()
    else:
        raise ValueError("Invalid intent")


def get_welcome_response():
    session_attributes = {"count" : 1, "questions" : "", "score" : 0}
    card_title = "Welcome"
    speech_output = "Welcome to C.S. Quiz, " \
                    "A Computer Science quiz. " \
                    "Start the quiz by saying the mode in which you want to play that is, easy, medium or hard."
                    
    reprompt_text = "This is a Computer Science quiz. " \
                    "Start the quiz by saying the mode in which you want to play that is easy, medium or hard."

    should_end_session = False
    smallLink = None
    largeLink = None
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, smallLink, largeLink, should_end_session))


def getQuestions(mode):
	url = "https://opentdb.com/api.php?amount=10&category=18&difficulty=" + mode + "&type=multiple"
	myResponse = requests.get(url, verify=True)
	jData = json.loads(myResponse.content)
	count = 1
	questions = {1 : {"question" : "", "correctOption" : "", "incorrectOption" : ""}, 2 : {"question" : "", "correctOption" : "", "incorrectOption" : ""}, 
		3 : {"question" : "", "correctOption" : "", "incorrectOption" : ""}, 4 : {"question" : "", "correctOption" : "", "incorrectOption" : ""}, 
		  5 : {"question" : "", "correctOption" : "", "incorrectOption" : ""}, 6 : {"question" : "", "correctOption" : "", "incorrectOption" : ""}, 
		    7 : {"question" : "", "correctOption" : "", "incorrectOption" : ""}, 8 : {"question" : "", "correctOption" : "", "incorrectOption" : ""}, 
		      9 : {"question" : "", "correctOption" : "", "incorrectOption" : ""}, 10 :{"question" : "", "correctOption" : "", "incorrectOption" : ""}}
	for key in jData["results"]:
		questions[count]["question"] = key["question"]
		questions[count]["correctOption"] = key["correct_answer"]
		questions[count]["incorrectOption"] = key["incorrect_answers"]
		count += 1

	return questions

def buildQuestion(questions, count):
	rand = random.randint(1,4)
	ques = {"question" : "", "options" : [], "correctOption" : ""}
	ques["question"] = questions[count]["question"]
	index = 0
	for i in range(1,5):
		if i == rand:
			ques["options"].insert(i-1,questions[count]["correctOption"])
			ques["correctOption"] = rand
		else:
		    try:
		        ques["options"].insert(i-1,questions[count]["incorrectOption"][index])
		        index += 1
		    except IndexError as error:
		        	raise error
	return ques

def chechAns(intent, session):
	ansIntent = intent["slots"]["answer"]["value"].lower()
	if ansIntent == "a" or ansIntent == "one" or ansIntent == "option a" or ansIntent == "first":
		if session["attributes"]["correctOption"] == 1:
			return 1
	elif ansIntent == "b" or ansIntent == "two" or ansIntent == "option b" or ansIntent == "second":
		if session["attributes"]["correctOption"] == 2:
			return 1
	elif ansIntent == "c" or ansIntent == "three" or ansIntent == "option c" or ansIntent == "third":
		if session["attributes"]["correctOption"] == 3:
			return 1
	elif ansIntent == "d" or ansIntent == "four" or ansIntent == "option d" or ansIntent == "fourth":
		if session["attributes"]["correctOption"] == 4:
			return 1
	else:
	    return 0

def modeSelection(intent, session):
    modeIntent = intent["slots"]["mode"]["value"].lower()
    if modeIntent != "easy" and modeIntent != "medium" and modeIntent != "hard":
        return errorMessage()
    else:
        session_attributes = {"count" : 1, "questions" : "", "score" : 0}
        speech_output = "Your Selected Mode is " + modeIntent +". If correct say yes to start the quiz."
        reprompt_text = "Your Selected Mode is " + modeIntent +". If correct say yes to start the quiz."
        card_title = "CS Quiz"
        should_end_session = False
        smallLink = None
        largeLink = None
        session_attributes["questions"] = getQuestions(modeIntent)
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, smallLink, largeLink,
                                                   should_end_session))

def startQuiz(intent, session):
    if session["attributes"]["count"] > 10:
        speech_output = "You've answered all the questions. Your score is " + str(session["attributes"]["score"]) + " out of 10."
        reprompt_text = "You've answered all the questions. Your score is " + str(session["attributes"]["score"]) + " out of 10."
        card_title = "CS Quiz"
        should_end_session = True
        smallLink = None
        largeLink = None
    else:
        question = buildQuestion(session["attributes"]["questions"],str(session["attributes"]["count"]))
        session_attributes = {"count" : 1, "questions" : "", "score" : 0, "correctOption" : 0}
        session_attributes["questions"] = session["attributes"]["questions"]
        session_attributes["score"] = session["attributes"]["score"]
        speech_output = question["question"] + "\n" + "(a) " + question["options"][0] + "\n" + "(b) " + question["options"][1] + "\n" + "(c) " + question["options"][2] + "\n" + "(d) " + question["options"][3]
        reprompt_text = question["question"] + "\n" + "(a) " + question["options"][0] + "\n" + "(b) " + question["options"][1] + "\n" + "(c) " + question["options"][2] + "\n" + "(d) " + question["options"][3]
        card_title = "CS Quiz"
        should_end_session = False
        smallLink = None
        largeLink = None
        session_attributes["count"] = session["attributes"]["count"] + 1
        session_attributes["correctOption"] = question["correctOption"]
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, smallLink, largeLink,
                                                   should_end_session))	

def Answer(intent, session):
    session_attributes = {"count" : 1, "questions" : "", "score" : 0, "correctOption" : 0}
    session_attributes["count"] = session["attributes"]["count"]
    session_attributes["score"] = session["attributes"]["score"]
    session_attributes["questions"] = session["attributes"]["questions"]
    card_title = "CS Quiz"
    should_end_session = False
    smallLink = None
    largeLink = None
    if intent["slots"]["answer"]["value"] == "score":
        session_attributes["score"] = session["attributes"]["score"]
        speech_output = "Your score is " + str(session["attributes"]["score"]) + "."
        reprompt_text = "Your score is " + str(session["attributes"]["score"]) + "."
    elif chechAns(intent, session):
        session_attributes["score"] = session["attributes"]["score"] + 1
        speech_output = "Your answer is correct. You Got 1 point. "
        reprompt_text = "Your answer is correct. You Got 1 point. "
    else:
        session_attributes["score"] = session["attributes"]["score"]
        speech_output = "Your answer is incorrect. Correct answer is option " + str(session["attributes"]["correctOption"]) + ". You Got 0 point. "
        reprompt_text = "Your answer is incorrect. Correct answer is option " + str(session["attributes"]["correctOption"]) + "You Got 0 point. "
        
    if session["attributes"]["count"] > 10:
        speech_output = speech_output + "You've answered all the questions. Your score is " + str(session["attributes"]["score"]) + " out of 10. Thankyou for playing."
        reprompt_text = reprompt_text + "You've answered all the questions. Your score is " + str(session["attributes"]["score"]) + " out of 10. Thankyou for playing."
        should_end_session = True
    else:
        speech_output = speech_output + " Ready for next question?"
        reprompt_text = reprompt_text + " Ready for next question?"
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, smallLink, largeLink,
                                                   should_end_session))

def errorMessage():
    speech_output = "Didn't catch that. Speak again."
    reprompt_text = "Didn't catch that. Speak again."
    smallLink = None
    largeLink = None
    card_title = "CS Quiz"
    should_end_session = False
    session_attributes = {}
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, smallLink, largeLink,
                                                   should_end_session))

def on_yes(intent, session):
    if session["attributes"]["questions"] == "":
        return errorMessage()
    else:
        return startQuiz(intent, session)

def on_session_ended(session_ended_request, session):
    speech_output = "Thankyou for playing C.S. Quiz. See You Again."
    reprompt_text = "Thankyou for playing C.S. Quiz. See You Again."
    card_title = "Thankyou"
    session_attributes = session
    should_end_session = True
    smallLink = None
    largeLink = None
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, smallLink, largeLink,
                                                   should_end_session))


def on_session_end():
    speech_output = None
    reprompt_text = None
    card_title = None
    session_attributes = None
    should_end_session = True
    smallLink = None
    largeLink = None
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, smallLink, largeLink,
                                                   should_end_session))


def build_speechlet_response(title, output, reprompt_text, smallLink, largeLink, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Standard',
            'title': title,
            'text': output,
            "image": {
                "smallImageUrl": smallLink,
                "largeImageUrl": largeLink
            }
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }