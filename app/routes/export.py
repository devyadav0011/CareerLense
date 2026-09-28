from flask import Blueprint, request, jsonify, session, send_file
from ..services.pdf_service import PDFService
from ..utils.session_store import SessionStore

export_bp = Blueprint('export', __name__, url_prefix='/api/export')

@export_bp.route('/resume', methods=['GET', 'POST'])
def export_resume():
    data = {}
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}

    template = data.get('template') or request.args.get('template', 'modern')
    structured = data.get('resume_data')

    if not structured:
        curr = SessionStore.get_current_resume()
        if curr:
            structured = curr.get('structured_data')

    if not structured:
        return jsonify({'error': 'No resume data available to export. Please build or upload a resume first.'}), 400

    try:
        pdf_stream = PDFService.generate_resume_pdf(structured, template=template)
        name = structured.get('personal_info', {}).get('full_name', 'Resume')
        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip() or 'Resume'
        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{clean_name}_CareerLense.pdf"
        )
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500


@export_bp.route('/report', methods=['GET', 'POST'])
def export_report():
    data = {}
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}

    curr = SessionStore.get_current_resume() or {}
    analysis_data = data.get('analysis') or curr.get('scores') or {}
    resume_data = data.get('resume_data') or curr.get('structured_data') or {}

    # Merge ATS into analysis_data if needed
    if 'ats_style_score' not in analysis_data:
        ats = curr.get('ats', {})
        analysis_data['ats_style_score'] = ats.get('ats_score', 88)

    if not resume_data and not analysis_data:
        return jsonify({'error': 'No resume analysis available to export.'}), 400

    try:
        pdf_stream = PDFService.generate_analysis_report_pdf(analysis_data, resume_data)
        name = resume_data.get('personal_info', {}).get('full_name', 'Analysis')
        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip() or 'Analysis'
        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{clean_name}_CareerLense_Report.pdf"
        )
    except Exception as e:
        return jsonify({'error': f'Report PDF generation failed: {str(e)}'}), 500
