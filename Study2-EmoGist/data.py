def get_condition_data(emails, condition):
    data = []
    for email in emails:
        if condition == "Proposed":
            # All
            email_data = {
                'date': email.date,
                'sender': email.sender,
                'to': email.to,
                'subject': email.subject,
                'body': None,
                'emoji': email.emoji
            }
        elif condition == "Baseline":
            email_data = {
                'date': email.date,
                'sender': email.sender,
                'to': email.to,
                'subject': email.subject,
                'body': email.body,
                'emoji': None
            }
        data.append(email_data)
    return data


