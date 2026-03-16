import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from database import db
from models import Contact, ContactRepository

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
contact_repo = ContactRepository(db)
DEFAULT_GROUPS = ['Друзья', 'Работа', 'Семья', 'Сервис', 'Соседи', 'Другое']

@app.context_processor
def utility_processor():
    return dict(groups=DEFAULT_GROUPS)

@app.route('/')
def index():
    group = request.args.get('group', 'Все')
    search = request.args.get('search', '')
    
    contacts = contact_repo.get_all(group=group, search=search)
    groups = contact_repo.get_groups()
    
    return render_template(
        'index.html',
        contacts=contacts,
        current_group=group,
        search_query=search,
        groups=groups,
        total=len(contacts)
    )

@app.route('/contact/<int:contact_id>')
def view_contact(contact_id):
    contact = contact_repo.get_by_id(contact_id)
    if not contact:
        flash('Контакт не найден', 'error')
        return redirect(url_for('index'))
    
    return render_template('view.html', contact=contact)

@app.route('/contact/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        try:
            contact = Contact(
                id=None,
                last_name=request.form['last_name'],
                first_name=request.form['first_name'],
                middle_name=request.form.get('middle_name', ''),
                phone_number=request.form['phone_number'],
                note=request.form.get('note', ''),
                contact_group=request.form.get('contact_group', 'Друзья'),
                is_favorite='is_favorite' in request.form,
                created_at=None,
                updated_at=None
            )
            
            contact_id = contact_repo.create(contact)
            flash(f'Контакт успешно добавлен!', 'success')
            return redirect(url_for('view_contact', contact_id=contact_id))
        
        except Exception as e:
            flash(f'Ошибка при добавлении: {str(e)}', 'error')
    
    return render_template('add.html', groups=DEFAULT_GROUPS)

@app.route('/contact/<int:contact_id>/edit', methods=['GET', 'POST'])
def edit_contact(contact_id):
    contact = contact_repo.get_by_id(contact_id)
    if not contact:
        flash('Контакт не найден', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            updated_contact = Contact(
                id=contact_id,
                last_name=request.form['last_name'],
                first_name=request.form['first_name'],
                middle_name=request.form.get('middle_name', ''),
                phone_number=request.form['phone_number'],
                note=request.form.get('note', ''),
                contact_group=request.form.get('contact_group', contact.contact_group),
                is_favorite='is_favorite' in request.form,
                created_at=contact.created_at,
                updated_at=None
            )
            
            contact_repo.update(contact_id, updated_contact)
            flash('Контакт успешно обновлён!', 'success')
            return redirect(url_for('view_contact', contact_id=contact_id))
        
        except Exception as e:
            flash(f'Ошибка при обновлении: {str(e)}', 'error')
    
    return render_template('edit.html', contact=contact, groups=DEFAULT_GROUPS)

@app.route('/contact/<int:contact_id>/delete', methods=['POST'])
def delete_contact(contact_id):
    try:
        contact_repo.delete(contact_id)
        flash('Контакт удалён', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/contact/<int:contact_id>/favorite', methods=['POST'])
def toggle_favorite(contact_id):
    try:
        contact_repo.toggle_favorite(contact_id)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return redirect(request.referrer or url_for('index'))

@app.route('/api/contacts')
def api_contacts():
    group = request.args.get('group', 'Все')
    search = request.args.get('search', '')
    
    contacts = contact_repo.get_all(group=group, search=search)
    return jsonify([{
        'id': c.id,
        'full_name': c.full_name,
        'phone': c.formatted_phone,
        'group': c.contact_group,
        'is_favorite': c.is_favorite
    } for c in contacts])

@app.errorhandler(404)
def not_found_error(error):
    return render_template(
        'error.html',
        error_code=404,
        title='Страница не найдена',
        message='Запрошенная страница не существует или была перемещена.',
        action_url=url_for('index'),
        action_text='Вернуться на главную'
    ), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template(
        'error.html',
        error_code=500,
        title='Ошибка сервера',
        message='Во время обработки запроса произошла внутренняя ошибка. Попробуйте повторить действие позже.',
        action_url=url_for('index'),
        action_text='Открыть главную'
    ), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
