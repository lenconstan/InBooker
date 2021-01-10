from app import sendgrid
from app import ApiKeys

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class MailClient():

    def send_grid(customer, customer_emailaddress, sender, orderid):
        subject = 'Uw bestelling van {} staat klaar om afgehaald te worden'.format(sender)
        html = """\
        <html>

          <body>
            <p>Hallo %s,<br>
             <br>
               Je bestelling van %s met ordernummer %s staat klaar om afgehaald te worden.<br>
               Onze openingstijden zijn: <br>
               <br>
               met vriendelijke groet,<br>
               <br>
               Stan<br>
               <img src="https://d27i7n2isjbnbi.cloudfront.net/careers/photos/118582/normal_photo_1560943732.png" alt="BR8LOGO" width="150" height="150">

            </p>
          </body>
        </html>
        """ % (customer, sender, orderid)

        message = Mail(
        from_email='kruize.cl@gmail.com',
        to_emails= customer_emailaddress,
        subject=subject,
        html_content=html)
        try:
            sg = SendGridAPIClient(ApiKeys.SENDGRID_API_KEY)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)