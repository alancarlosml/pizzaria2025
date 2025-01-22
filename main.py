from flask import Flask, render_template, redirect, url_for # importando a biblioteca flask
from flask_sqlalchemy import SQLAlchemy # importando a biblioteca sqlalchemy
from flask_wtf import FlaskForm # importando a biblioteca flask_wtf
from wtforms import StringField, FileField, FloatField, SelectField, TextAreaField, SubmitField
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__) # criando uma instância da classe Flask
app.config['SECRET_KEY'] = 'pode_ser_qualquer_coisa' # configurando a chave de segurança da aplicação
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizzaria.db' # configurando o banco de dados
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app) # criando uma instância da classe SQLAlchemy

class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    tamanho = db.Column(db.String(1), nullable=False)
    sabores = db.Column(db.String(250), nullable=False)
    imagem = db.Column(db.String(250), nullable=False)
    
class CadastroForm(FlaskForm):
    nome = StringField('Nome')
    preco = FloatField('Preço')
    tamanho = SelectField('Tamanho', 
                          choices=[('P', 'Pequena'), ('M', 'Média'), ('G', 'Grande')])
    sabores = TextAreaField('Sabores')
    imagem = FileField('Imagem')
    submit = SubmitField('Cadastrar')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroForm()
    if form.validate_on_submit():
        imagem = form.imagem.data
        image_path = f'{app.config["UPLOAD_FOLDER"]}/{secure_filename(imagem.filename)}'
        pizza = Pizza(nome=form.nome.data, 
                      preco=form.preco.data, 
                      tamanho=form.tamanho.data, 
                      imagem=image_path,
                      sabores=form.sabores.data)
        imagem.save(image_path)
        db.session.add(pizza)
        db.session.commit()
        return redirect(url_for('listagem'))
    return render_template('cadastro.html', form=form)

@app.route('/listagem', methods=['GET'])
def listagem():
    pizzas = Pizza.query.all()
    return render_template('listagem.html', pizzas=pizzas)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    pizza = Pizza.query.get(id)
    form = CadastroForm(obj=pizza)
    if form.validate_on_submit():
        imagem = form.imagem.data
        image_path = f'{app.config["UPLOAD_FOLDER"]}/{secure_filename(imagem.filename)}'
        pizza.nome = form.nome.data
        pizza.preco = form.preco.data
        pizza.tamanho = form.tamanho.data
        pizza.imagem = image_path
        pizza.sabores = form.sabores.data
        db.session.commit()
        imagem.save(image_path)
        return redirect(url_for('listagem'))
    return render_template('cadastro.html', form=form, pizza=pizza)

@app.route('/excluir/<int:id>')
def excluir(id):
    pizza = Pizza.query.get(id)
    db.session.delete(pizza)
    db.session.commit()
    return redirect(url_for('listagem'))

if __name__ == '__main__':
    with app.app_context(): 
        db.create_all()
    app.run(debug=True)