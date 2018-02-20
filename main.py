import sys
from mattermost_bot.bot import respond_to
from mattermost_bot.bot import listen_to
from mattermost_bot.bot import Bot
import requests
import json
from requests.auth import HTTPBasicAuth
import urllib
from config.config import BUGZILLA_USER, BUGZILLA_PASSWORD
import mattermost_bot_settings
import logging

from lang.lis import eval, parse


def get_bug_comments(bug_id):

    params_str = json.dumps([{
        'ids': [bug_id],
        'Bugzilla_login': BUGZILLA_USER,
        'Bugzilla_password': BUGZILLA_PASSWORD
    }])
    params_str_encoded = urllib.quote_plus(params_str)

    url = "https://intranet.grid5000.fr/bugzilla/jsonrpc.cgi?method=Bug.comments&params=%s" % params_str_encoded
    comments_response = requests.get(url,
                            auth=HTTPBasicAuth(BUGZILLA_USER, BUGZILLA_PASSWORD))
    comments_raw = comments_response.json().get("result", {}).get("bugs", {}).get("%s" % bug_id, {}).get("comments")
    comments = [{"author": x.get("author", "unknown"), "msg": x.get("text", "no text")} for x in comments_raw]

    return comments


def get_bug_info(bug_id, with_comments=False):
    params_str = json.dumps([{
        'id': bug_id,
        'Bugzilla_login': BUGZILLA_USER,
        'Bugzilla_password': BUGZILLA_PASSWORD
    }])
    params_str_encoded = urllib.quote_plus(params_str)

    url = "https://intranet.grid5000.fr/bugzilla/jsonrpc.cgi?method=Bug.search&params=%s" % params_str_encoded
    bug_response = requests.get(url,
                            auth=HTTPBasicAuth(BUGZILLA_USER, BUGZILLA_PASSWORD))

    bug_candidates = bug_response.json().get("result", {}).get("bugs", [])

    for bug_candidate in bug_candidates:
        if with_comments:
            comments = get_bug_comments(bug_id)
        else:
            comments = []
        return {
            "title": bug_candidate.get("summary"),
            "url": "https://intranet.grid5000.fr/bugzilla/show_bug.cgi?id=%s" % bug_id,
            "id": bug_candidate.get("id"),
            "status": bug_candidate.get("status"),
            "comments": comments
        }
    return {
        "title": "Did not found any bug with ID=%s :-(" % bug_id,
        "url": "https://intranet.grid5000.fr/bugzilla/show_bug.cgi?id=%s" % bug_id,
        "id": bug_id,
        "status": "Bug not found",
        "comments": "No comments"
    }


def format_bug(bug_info):
    response = """\n+-----------------------------------
| %s: %s (%s)
+----------------------------------
| link: %s
+----------------------------------""" % (bug_info["id"], bug_info["title"], bug_info["status"], bug_info["url"])

    if len(bug_info["comments"]) > 0:
        cpt = 0
        for comment in bug_info["comments"]:
            if cpt > 0:
                response += "\n|"
            formatted_comment = ["|   "+ x for x in comment["msg"].split("\n")]
            response += "\n| <%s> wrote: \n%s" % (comment["author"], "\n".join(formatted_comment))
            cpt += 1

        response += """\n+----------------------------------"""
    return response


def display_bug(exp):
    result = eval(parse(exp))
    reply_msgs = []
    if not isinstance(result, (list, tuple)):
        result = [result]
    for bug_id in result:
        bug_info = get_bug_info(bug_id, with_comments=False)
        reply_msgs += [format_bug(bug_info)]
    return reply_msgs


def display_comments(exp):
    result = eval(parse(exp))
    reply_msgs = []
    if not isinstance(result, (list, tuple)):
        result = [result]
    for bug_id in result:
        bug_info = get_bug_info(bug_id, with_comments=True)
        reply_msgs += [format_bug(bug_info)]
    return reply_msgs


@respond_to('\(bug.msg (.*)\)')
def respond_messages(message, bug_id):
    reply_msgs = display_comments(bug_id)
    for msg in reply_msgs:
        message.reply(msg)


@listen_to('\(bug.msg (.*)\)')
def listen_messages(message, bug_id):
    reply_msgs = display_comments(bug_id)
    for msg in reply_msgs:
        message.reply(msg)


@respond_to('\(bug (.*)\)')
def respond_bug(message, bug_id):
    reply_msgs = display_bug(bug_id)
    for msg in reply_msgs:
        message.reply(msg)


@listen_to('\(bug (.*)\)')
def listen_bug(message, bug_id):
    reply_msgs = display_bug(bug_id)
    for msg in reply_msgs:
        message.reply(msg)


if __name__ == "__main__":
    logging.basicConfig(**{
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG,
        'stream': sys.stdout,
    })

    Bot().run()
