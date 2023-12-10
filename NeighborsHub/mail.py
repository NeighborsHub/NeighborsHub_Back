class SendEmail:
    def __int__(self):
        # some config is here
        pass

    def run(self, mail_destination, title, body):
        print(mail_destination, title, body)
        return {'to': mail_destination, 'title': title, 'body': body}
