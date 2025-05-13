import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import pandas as pd
import secrets
import io

app = Flask(__name__, static_folder='static', template_folder='static')
app.secret_key = secrets.token_hex(16) # For session management

UPLOAD_FOLDER = '/tmp/excel_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Clear session data when returning to the main page
    session.pop('uploaded_file_path', None)
    session.pop('original_filename', None)
    session.pop('full_df_json', None)
    session.pop('search_results_df_json', None) # Clear previous search results
    session.pop('search_query', None)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("لم يتم تحديد أي ملف", "error")
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash("لم يتم تحديد أي ملف", "error")
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        # Consider using werkzeug.utils.secure_filename for security
        filename = file.filename 
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['uploaded_file_path'] = filepath
        session['original_filename'] = filename
        session.pop('search_results_df_json', None) # Clear any previous search results from session
        session.pop('search_query', None)

        try:
            df = pd.read_excel(filepath, engine='openpyxl')
            # Store the DataFrame in session as JSON to be accessible by search and export
            session['full_df_json'] = df.to_json(orient='split', date_format='iso')

            data_html = df.to_html(classes='table table-striped', index=False, border=0, justify='right')
            return render_template('view_excel.html', data_table=data_html, filename=filename)
        except Exception as e:
            flash(f"خطأ في قراءة الملف: {str(e)}", "error")
            return redirect(url_for('index'))
    else:
        flash("نوع الملف غير مسموح به. يرجى رفع ملفات xls أو xlsx فقط.", "error")
        return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search_data():
    search_query = request.form.get('search_query')
    session['search_query'] = search_query # Store search query in session
    filepath = session.get('uploaded_file_path')
    original_filename = session.get('original_filename')
    full_df_json = session.get('full_df_json')

    if not filepath or not original_filename or not full_df_json:
        flash("الرجاء رفع ملف أولاً.", "error")
        return redirect(url_for('index'))

    try:
        df = pd.read_json(full_df_json, orient='split')
        if not search_query: # If search query is empty, show full table
            session.pop('search_results_df_json', None) # Clear search results if query is empty
            data_html = df.to_html(classes='table table-striped', index=False, border=0, justify='right')
            flash("عرض كامل محتويات الملف.", "info")
            return render_template('view_excel.html', data_table=data_html, filename=original_filename, search_query=search_query)

        search_query_str = str(search_query)
        # Ensure all data is treated as string for searching to avoid type errors
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query_str, case=False, na=False).any(), axis=1)
        results_df = df[mask]
        
        session['search_results_df_json'] = results_df.to_json(orient='split', date_format='iso')

        if results_df.empty:
            results_html = "<p>لا توجد نتائج مطابقة لبحثك.</p>"
        else:
            results_html = results_df.to_html(classes='table table-striped', index=False, border=0, justify='right')
        
        return render_template('view_excel.html', data_table=results_html, filename=original_filename, search_query=search_query)
    except Exception as e:
        flash(f"خطأ أثناء البحث: {str(e)}", "error")
        # Attempt to show the full table again if search fails
        try:
            df_fallback = pd.read_json(full_df_json, orient='split')
            data_html_fallback = df_fallback.to_html(classes='table table-striped', index=False, border=0, justify='right')
            return render_template('view_excel.html', data_table=data_html_fallback, filename=original_filename, error_message=f"خطأ أثناء البحث: {str(e)}", search_query=search_query)
        except Exception as e_inner:
            flash(f"خطأ فادح عند محاولة عرض البيانات الأصلية: {str(e_inner)}", "error")
            return redirect(url_for('index'))

@app.route('/export')
def export_data():
    original_filename = session.get('original_filename', 'exported_data')
    search_results_df_json = session.get('search_results_df_json')
    full_df_json = session.get('full_df_json')
    search_query = session.get('search_query')

    df_to_export = None

    if search_results_df_json:
        df_to_export = pd.read_json(search_results_df_json, orient='split')
        export_filename = f"نتائج_بحث_{search_query}_{original_filename}"
    elif full_df_json:
        df_to_export = pd.read_json(full_df_json, orient='split')
        export_filename = f"كامل_الملف_{original_filename}"
    else:
        flash("لا توجد بيانات لتصديرها. يرجى رفع ملف والبحث أولاً إذا لزم الأمر.", "warning")
        return redirect(url_for('index'))

    if df_to_export.empty:
        flash("لا توجد بيانات في النتائج الحالية لتصديرها.", "info")
        # Redirect back to the view page, trying to preserve context
        data_html = "<p>لا توجد بيانات لتصديرها.</p>"
        if original_filename:
             return render_template('view_excel.html', data_table=data_html, filename=original_filename, search_query=search_query)
        else:
            return redirect(url_for('index'))

    try:
        # Create an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_to_export.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)
        
        # Ensure the filename is filesystem-safe and has .xlsx extension
        safe_export_filename = "".join([c if c.isalnum() or c in (".", "_", "-") else "_" for c in export_filename])
        if not safe_export_filename.lower().endswith(('.xlsx', '.xls')):
            safe_export_filename += '.xlsx'

        return send_file(output, 
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                         as_attachment=True, 
                         download_name=safe_export_filename)
    except Exception as e:
        flash(f"حدث خطأ أثناء تصدير الملف: {str(e)}", "error")
        # Redirect back to the view page, trying to preserve context
        data_html = df_to_export.to_html(classes='table table-striped', index=False, border=0, justify='right') if not df_to_export.empty else "<p>خطأ أثناء محاولة عرض البيانات قبل التصدير.</p>"
        if original_filename:
            return render_template('view_excel.html', data_table=data_html, filename=original_filename, search_query=search_query, error_message=f"خطأ في التصدير: {str(e)}")
        else:
            return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

