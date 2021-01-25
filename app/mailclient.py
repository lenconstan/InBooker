from app import ApiKeys
import os

from app import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app import postmarker
from postmarker.core import PostmarkClient
postmark = PostmarkClient(server_token=ApiKeys.POSTMARK_SERVER_TOKEN)


class MailClient():

    def send_grid(customer, customer_emailaddress, sender, orderid):
        subject = 'Uw bestelling van {} staat klaar om afgehaald te worden'.format(sender)
        html = """\
        <html>

          <body>
            <p>Hallo %s,<br>
             <br>
               Je bestelling bij %s met referentie %s staat klaar om afgehaald te worden in ons magazijn.<br>
               U kunt een afspraak maken door op de link te klikken: https://br8.nl/bestelling-afhalen-bij-br8-te-montfoort. <br>
               <br>
               met vriendelijke groet,<br>
               <br>
               De magazijnmannen van BR8<br>
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
            print('sendgrid:')
            print(response)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)

    def post_mark(customer, customer_emailaddress, sender, orderid):
        subject = 'Uw bestelling van {} staat klaar om afgehaald te worden'.format(sender)
        html = """\
        <html>

          <body>
            <p>Hallo %s,<br>
             <br>
               Je bestelling bij %s met referentie %s staat klaar om afgehaald te worden in ons magazijn.<br>
               Maak een ophaalafspraak door op de volgende link te klikken: https://br8.nl/bestelling-afhalen-bij-br8-te-montfoort. <br>
               <br>
               met vriendelijke groet,<br>
               <br>
               De magazijnmannen van BR8<br>
               <img src="https://d27i7n2isjbnbi.cloudfront.net/careers/photos/118582/normal_photo_1560943732.png" alt="BR8LOGO" width="150" height="150">

            </p>
          </body>
        </html>
        """ % (customer, sender, orderid)



        # Send an email
        postmark.emails.send(
          From=ApiKeys.POSTMARK_MAIL_ADRESS,
          To=customer_emailaddress,
          Subject=subject,
          HtmlBody=html
        )
