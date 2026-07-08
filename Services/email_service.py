import yagmail
from constants import *


def enviar_email(emails, assunto, corpo, anexos):

    yag = yagmail.SMTP(SEU_EMAIL, SENHA_APP)

    yag.send(
        to=emails,
        subject=assunto,
        contents=corpo,
        attachments=anexos
    )
