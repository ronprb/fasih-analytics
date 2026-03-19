BASE_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://fasih-sm.bps.go.id",
    "Referer": "https://fasih-sm.bps.go.id/survey-collection/survey",
    "User-Agent": "Mozilla/5.0",
}

payload_survey ={
    "pageNumber": 0,
    "pageSize": 100,
    "sortBy": "CREATED_AT",
    "sortDirection": "DESC",
    "keywordSearch": ""
}

report_user_assignment_url = "https://fasih-sm.bps.go.id/analytic/api/v2/assignment/report-user-assignment"
report_progress_assignment_url = "https://fasih-sm.bps.go.id/analytic/api/v2/assignment/report-progress-assignment"

pemutakhiran_base_url = "https://fasih-sm.bps.go.id/assignment-general/api/assignment-region/datatable?periodeId="
pemutakhiran_payload = {
    "draw": 2,
    "columns": [
        {"data": 0, "name": "", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": 1, "name": "", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": 2, "name": "", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": 3, "name": "", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": 4, "name": "", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
    ],
    "order": [{"column": 0, "dir": "asc"}],
    "start": 0,
    "length": 5000,
    "search": {"value": "", "regex": False}
}
pemutakhiran_status_order = ['SudahTarikSampel', 'SelesaiListing', 'BelumSelesaiListing']

progress_status_order = [
'COMPLETED BY Admin Kabupaten',
'COMPLETED BY ADMIN PROVINSI',
'COMPLETED BY Pengawas',
'clean',
'APPROVED BY ADMIN KABUPATEN',
'APPROVED BY ADMIN PROVINSI',
'APPROVED BY Admin Kabupaten',
'APPROVED BY PENGAWAS',
'APPROVED BY Pengawas',
'SUBMITTED BY PENCACAH',
'SUBMITTED BY Pencacah',
'SUBMITTED RESPONDENT',
'DRAFT',
'EDITED BY Admin Kabupaten',
'EDITED BY ADMIN KABUPATEN',
'EDITED BY Admin Pusat',
'REJECTED BY Admin Kabupaten',
'REJECTED BY PENGAWAS',
'REJECTED BY Pengawas',
'REVOKED BY Admin Kabupaten',
'REVOKED BY PENGAWAS',
'REVOKED BY Pengawas',
'OPEN',
'belum_entry']

assignment_status_order = ['assigned', 'have-not-assigned']

palette_options = {
    "Vivid": {
        'COMPLETED': '#00C853',
        'clean': '#00C853',
        'OPEN': '#D50000',
        'belum_entry': '#D50000',
        'APPROVED': '#9E9E9E',
        'EDITED': '#2962FF',
        'REJECTED': '#C51162',
        'REVOKED': '#AA00FF',
        'SUBMITTED': '#FFD600',
        'DRAFT': '#6200EA',
        'SELESAILISTING': '#9E9E9E',
        'BELUMSELESAILISTING': '#D50000',
        'SUDAHTARIKSAMPEL': '#00C853',
    },
    "Muted": {
        'COMPLETED': '#66BB6A',
        'clean': '#66BB6A',
        'OPEN': '#EF5350',
        'belum_entry': '#EF5350',
        'APPROVED': '#BDBDBD',
        'EDITED': '#64B5F6',
        'REJECTED': '#E57373',
        'REVOKED': '#BA68C8',
        'SUBMITTED': '#FFF176',
        'DRAFT': '#9575CD',
        'SELESAILISTING': '#BDBDBD',
        'BELUMSELESAILISTING': '#EF5350',
        'SUDAHTARIKSAMPEL': '#66BB6A',
    },
    "DarkMode": {
        'COMPLETED': '#2E7D32',
        'clean': '#2E7D32',
        'OPEN': '#C62828',
        'belum_entry': '#C62828',
        'APPROVED': '#424242',
        'EDITED': '#0277BD',
        'REJECTED': '#AD1457',
        'REVOKED': '#6A1B9A',
        'SUBMITTED': '#F9A825',
        'DRAFT': '#4527A0',
        'SELESAILISTING': '#424242',
        'BELUMSELESAILISTING': '#C62828',
        'SUDAHTARIKSAMPEL': '#2E7D32',
    },
    "HighContrast": {
        'COMPLETED': '#00FF00',
        'clean': '#00FF00',
        'OPEN': '#FF0000',
        'belum_entry': '#FF0000',
        'APPROVED': '#AAAAAA',
        'EDITED': '#0099FF',
        'REJECTED': '#FF00FF',
        'REVOKED': '#9900FF',
        'SUBMITTED': '#FFFF00',
        'DRAFT': '#6600CC',
        'SELESAILISTING': '#AAAAAA',
        'BELUMSELESAILISTING': '#FF0000',
        'SUDAHTARIKSAMPEL': '#00FF00',
    },
    'Pastel': {
        'COMPLETED': '#B5EAD7',
        'clean': '#B5EAD7',
        'OPEN': '#E57373',
        'belum_entry': '#E57373',
        'APPROVED': '#D3D3D3',
        'EDITED': '#ADD8E6',
        'REJECTED': '#E57373',
        'REVOKED': '#E57373',
        'SUBMITTED': '#FFF2B2',
        'DRAFT': '#E0BBE4',
        'SELESAILISTING': '#D3D3D3',
        'BELUMSELESAILISTING': '#E57373',
        'SUDAHTARIKSAMPEL': '#B5EAD7',
    }
}
