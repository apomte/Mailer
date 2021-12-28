from flask import (
    Blueprint,render_template,request,flash,url_for,redirect,current_app
)
import sendgrid
from sendgrid.helpers.mail import * #nos ayuda a crear correos mas facil

from app.db import get_db
#querio que muestre la raiz por eso solo dejo un slash
bp = Blueprint('mail', __name__,url_prefix='/')

@bp.route('/', methods=['GET'])
def index():
    search = request.args.get('search')#buscamos el parametro search que se encuentr en la url
    db, c = get_db()
    if search is None:
        c.execute('SELECT * FROM email')
    else:
        c.execute('SELECT * FROM email WHERE content LIKE %s', ('%' + search + '%', ))
    mails = c.fetchall()
    #print(mails)
    return render_template('mails/index.html',mails=mails)

@bp.route('/create',methods=['GET','POST'])
#crea el correo y lo guarda y muestra en la base de datos
def create():
    if request.method=='POST':
        email = request.form.get('email')
        subject = request.form.get('subject')
        content = request.form.get('content')
        #print(email,subject,content)
        errors=[]
        if not email:
            errors.append('email es obligatorio') #los campos no pueden ser null hay que validar que no vengan vacios
        if not subject:
            errors.append('Asunto es obligatorio')
        if not content:
            errors.append('Contenido es obligatorio')    
        #print(errors)
        # si el usuario tiene mas de 1 error nesesitamos mostrarle al usuario donde se equivoco
        if len(errors)==0:
            send(email,subject,content)
            db, c = get_db()
            c.execute('INSERT INTO email (email, subject, content) VALUES (%s, %s, %s)',(email,subject,content))
            db.commit()
            return redirect(url_for('mail.index'))
        else:
            for error in errors:
                flash(error)
    return render_template('mails/create.html')

# funcion para enivar correo electronico
# to : aquien va el correo, subject : asunto del correo , content: contenido del correo
def send(to, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_KEY'])#importamos los modulos de sendgrid
    from_email = Email(current_app.config['FROM_EMAIL'])#el correo electronico que vamos a utilizar para enviar correos electronicos
    to_email = To(to)# a quien se le envia el correo
    content = Content('text/plain',content)#correo texto plano + el contenido de content
    mail = Mail(from_email, to_email,subject,content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response)