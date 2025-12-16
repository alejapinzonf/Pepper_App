#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import qi
import sys

session = qi.Session()
pepper = {}

GESTURES = {

    "greetings": {
        "hey1": "animations/Stand/Gestures/Hey_1",
        "hey3": "animations/Stand/Gestures/Hey_3",
        "hey4": "animations/Stand/Gestures/Hey_4",
        "hey6": "animations/Stand/Gestures/Hey_6"
    },

    "emotions_positive": {
        "enthusiastic4": "animations/Stand/Gestures/Enthusiastic_4",
        "enthusiastic5": "animations/Stand/Gestures/Enthusiastic_5",
        "happy4": "animations/Stand/Emotions/Positive/Happy_4",
        "hysterical1": "animations/Stand/Emotions/Positive/Hysterical_1"
    },

    "calm": {
        "calm1": "animations/Stand/Gestures/CalmDown_1",
        "calm5": "animations/Stand/Gestures/CalmDown_5",
        "calm6": "animations/Stand/Gestures/CalmDown_6"
    },

    "thinking": {
        "think1": "animations/Stand/Gestures/Thinking_1",
        "think3": "animations/Stand/Gestures/Thinking_3",
        "think4": "animations/Stand/Gestures/Thinking_4",
        "think6": "animations/Stand/Gestures/Thinking_6",
        "think8": "animations/Stand/Gestures/Thinking_8",
        "wait1": "animations/Stand/Waiting/Think_1",
        "wait2": "animations/Stand/Waiting/Think_2",
        "wait3": "animations/Stand/Waiting/Think_3"
    },

    "desperate": {
        "des1": "animations/Stand/Gestures/Desperate_1",
        "des2": "animations/Stand/Gestures/Desperate_2",
        "des4": "animations/Stand/Gestures/Desperate_4",
        "des5": "animations/Stand/Gestures/Desperate_5"
    },

    "responses_yes": {
        "yes1": "animations/Stand/Gestures/Yes_1",
        "yes2": "animations/Stand/Gestures/Yes_2",
        "yes3": "animations/Stand/Gestures/Yes_3"
    },

    "responses_no": {
        "no1": "animations/Stand/Gestures/No_1",
        "no2": "animations/Stand/Gestures/No_2",
        "no3": "animations/Stand/Gestures/No_3",
        "nothing": "animations/Stand/Gestures/Nothing_2"
    },

    "understanding": {
        "understand1": "animations/Stand/Gestures/YouKnowWhat_1",
        "understand2": "animations/Stand/Gestures/YouKnowWhat_2",
        "understand3": "animations/Stand/Gestures/YouKnowWhat_3",
        "understand5": "animations/Stand/Gestures/YouKnowWhat_5"
    },

    "not_understanding": {
        "dontknow1": "animations/Stand/Gestures/IDontKnow_1",
        "dontknow2": "animations/Stand/Gestures/IDontKnow_2",
        "dontknow3": "animations/Stand/Gestures/IDontKnow_3"
    },

    "please": {
        "please1": "animations/Stand/Gestures/Please_1"
    }
}

def connect_pepper():
    try:
        session.connect("tcp://127.0.0.1:9559")
    except RuntimeError:
        print("Could not connect to Pepper")
        sys.exit(1)

    pepper["motion"]   = session.service("ALMotion")
    pepper["posture"]  = session.service("ALRobotPosture")
    pepper["animated"] = session.service("ALAnimatedSpeech")
    pepper["audio"]    = session.service("ALAudioDevice")
    pepper["animation"]= session.service("ALAnimationPlayer")
    pepper["tablet"]   = session.service("ALTabletService")

    print("Connected to Pepper")

class PepperHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        parsed = urlparse.urlparse(self.path)
        path = parsed.path

        length = int(self.headers.getheader("content-length", 0))
        data = self.rfile.read(length)
        params = urlparse.parse_qs(data)

        if path == "/say":
            text = params.get("text", [""])[0]
            if text:
                pepper["animated"].say(text)

        elif path == "/audio/up":
            v = pepper["audio"].getOutputVolume()
            pepper["audio"].setOutputVolume(min(100, v + 5))

        elif path == "/audio/down":
            v = pepper["audio"].getOutputVolume()
            pepper["audio"].setOutputVolume(max(0, v - 5))

        elif path == "/motion/wake":
            pepper["motion"].wakeUp()

        elif path == "/motion/rest":
            pepper["motion"].rest()

        elif path == "/motion/stop":
            pepper["motion"].stopMove()

        elif path == "/posture/standinit":
            pepper["posture"].goToPosture("StandInit", 0.5)

        elif path == "/posture/standzero":
            pepper["posture"].goToPosture("StandZero", 0.5)

        elif path == "/posture/crouch":
            pepper["posture"].goToPosture("Crouch", 0.5)

        elif path == "/move/forward":
            pepper["motion"].move(0.2, 0.0, 0.0)

        elif path == "/move/backward":
            pepper["motion"].move(-0.2, 0.0, 0.0)

        elif path == "/move/left":
            pepper["motion"].move(0.0, 0.0, 0.35)

        elif path == "/move/right":
            pepper["motion"].move(0.0, 0.0, -0.35)

        elif path == "/move/stop":
            pepper["motion"].stopMove()

        elif path.startswith("/gesture/"):
            parts = path.split("/")
            if len(parts) == 4:
                cat = parts[2]
                name = parts[3]
                if cat in GESTURES and name in GESTURES[cat]:
                    pepper["animation"].run(GESTURES[cat][name])

        elif path == "/tablet/image":
            url = params.get("url", [""])[0]
            if url:
                pepper["tablet"].showImage(url)

        elif path == "/tablet/web":
            url = params.get("url", [""])[0]
            if url:
                pepper["tablet"].showWebview(url)

        elif path == "/tablet/reload":
            pepper["tablet"].reload()

        elif path == "/tablet/show":
            pepper["tablet"].show()

        elif path == "/tablet/hide":
            pepper["tablet"].hide()

        elif path == "/tablet/clear":
            pepper["tablet"].clear()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write("ok")

if __name__ == "__main__":
    connect_pepper()
    server = HTTPServer(("0.0.0.0", 5000), PepperHandler)
    print("Pepper backend server running on port 5000")
    server.serve_forever()
