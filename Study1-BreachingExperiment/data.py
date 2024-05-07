
def get_condition_data(emails, condition):
    data = []
    for email in emails:
        if condition == "All":
            # All
            email_data = {
                'date': email.date,
                'sender': email.sender,
                'to': email.to,
                'subject': email.subject,
                'body': email.body
            }
        elif condition == "Sender":
            email_data = {
                'date': email.date,
                'sender': None,
                'to': email.to,
                'subject': email.subject,
                'body': email.body
            }
        elif condition == "Title":
            email_data = {
                'date': email.date,
                'sender': email.sender,
                'to': email.to,
                'subject': None,
                'body': email.body
            }
        elif condition == "Body":
            email_data = {
                'date': email.date,
                'sender': email.sender,
                'to': email.to,
                'subject': email.subject,
                'body': None
            }
        elif condition == "Date":
            email_data = {
                'date': None,
                'sender': email.sender,
                'to': email.to,
                'subject': email.subject,
                'body': email.body
            }
        else:
            # Others TODO
            email_data = {
                'date': email.date,
                'sender': email.sender,
                'to': email.to,
                'subject': email.subject,
                'body': email.body
            }
        data.append(email_data)
    return data


