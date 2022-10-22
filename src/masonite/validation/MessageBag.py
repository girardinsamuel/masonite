"""The Message Bag Module"""

import json


class MessageBag:
    def __init__(self, items={}):
        self.items = items

    def add(self, error, message):
        """Adds an error and message to the message bag

        Arguments:
            error {string} -- The error to add
            message {string} -- The message to add
        """

        if error in self.items:
            self.items[error].append(message)
        else:
            self.items.update({error: [message]})

    def all(self):
        """Get all errors and messages"""
        return self.items.values()

    def any(self):
        """If the messagebag has any errors"""
        return len(self.items) > 0

    def has(self, key):
        """If the messagebag has any errors"""
        return key in self.items

    def empty(self):
        """If the messagebag has any errors"""
        return not self.any()

    def first(self, key):
        """Gets the first error and message"""
        if self.has(key):
            return self.get(key)[0]
        else:
            return None

    def count(self):
        """Gets the amount of errors"""
        return len(self.items)

    def json(self):
        """Gets the amount of errors"""
        return json.dumps(self.items)

    def amount(self, key):
        """Gets the amount of messages

        Arguments:
            key {string} -- the error to get the amount of.

        Returns:
            int -- Returns the amount of messages
        """
        return len(self.items[key])

    def get(self, key):
        """Gets all the messages for a specific error.

        Arguments:
            key {string} -- the error to get the messages for

        Returns:
            list -- list of errors
        """
        return self.items.get(key)

    def errors(self):
        """Gets a list of errors"""
        return self.items

    def messages(self):
        """Gets a list of all the messages"""
        messages_list = []
        for message in self.items.values():
            if isinstance(message, list):
                for submessage in message:
                    messages_list.append(message)
            else:
                messages_list += message

        return messages_list

    def reset(self):
        """Gets a list of all the messages"""
        self.items = {}

    def merge(self, dictionary):
        """Merge a dictionary into the message bag.

        Arguments:
            dictionary {dict} -- dictionary of errors and messages.

        Returns:
            dictionary -- Returns a dictionary of the new errors.
        """
        self.items.update(dictionary)
        return self.any()

    def new(self, dictionary):
        return self.__class__(dictionary)

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return json.dumps(self.items)

    def get_response(self):
        return json.dumps(self.items)

    @staticmethod
    def view_helper(errors={}):
        if errors:
            return MessageBag(errors)

        from wsgi import application

        return MessageBag(application.make("request").session.get("errors") or {})

    def helper(self):
        return self
