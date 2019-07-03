from six import BytesIO
import unicodecsv
import xlsxwriter

from .tasks import alesco_db_fetch, ALESCO_DB_FIELDS


def department_user_export(fileobj, users):
    """Writes a passed-in queryset of DepartmentUser objects to a file-like object as an
    Excel spreadsheet.
    """
    with xlsxwriter.Workbook(
        fileobj,
        {
            'in_memory': True,
            'default_date_format': 'dd-mmm-yyyy HH:MM',
            'remove_timezone': True,
        },
    ) as workbook:
        users_sheet = workbook.add_worksheet('Department users')
        users_sheet.write_row('A1', (
            'COST CENTRE', 'NAME', 'EMAIL', 'ACCOUNT TYPE', 'POSITION TYPE', 'EXPIRY DATE'
        ))
        row = 1
        for i in users:
            users_sheet.write_row(row, 0, [
                i.cost_centre.code if i.cost_centre else '', i.get_full_name(), i.email, i.get_account_type_display(),
                i.get_position_type_display(), i.expiry_date if i.expiry_date else ''
            ])
            row += 1
        users_sheet.set_column('A:A', 13)
        users_sheet.set_column('B:B', 34)
        users_sheet.set_column('C:C', 46)
        users_sheet.set_column('D:D', 42)
        users_sheet.set_column('E:E', 13)
        users_sheet.set_column('F:F', 17)

    return fileobj


def departmentuser_alesco_descrepancy(fileobj, users):
    """This function is used to find the data differences between the
    Alesco database and the IT Assets database.
    """
    discrepancies = {}
    alesco_records = {}
    alesco_iter = alesco_db_fetch()

    # Get Alesco data.
    for row in alesco_iter:
        record = dict(zip(ALESCO_DB_FIELDS, row))
        eid = record['employee_id']

        if eid not in alesco_records:
            alesco_records[eid] = []
        alesco_records[eid].append(record)

    for key, record in alesco_records.items():
        if not users.filter(employee_id=key).exists():
            continue
        else:
            user = users.get(employee_id=key)
            alesco_record = record[0]  # GROSS ASSUMPTION: the first Alesco record in the list is the newest/most current.

        # Commenting out the check of first name to exclude the many false positives (e.g. Tom != Thomas)
        #if user.given_name:
        #    if alesco_record['first_name'].lower() != user.given_name.lower():
        #        if key not in discrepancies:
        #            discrepancies[key] = []
        #        discrepancies[key].append(
        #            (
        #                user.get_full_name(),
        #                'Given name mismatch',
        #                alesco_record['first_name'],
        #                user.given_name
        #            )
        #        )

        if user.surname:
            if alesco_record['surname'].lower() != user.surname.lower():
                if key not in discrepancies:
                    discrepancies[key] = []
                discrepancies[key].append(
                    (
                        user.get_full_name(),
                        'Surname mismatch',
                        alesco_record['surname'],
                        user.surname
                    )
                )

        if user.title:
            if alesco_record['occup_pos_title'].lower() != user.title.lower():
                if key not in discrepancies:
                    discrepancies[key] = []
                discrepancies[key].append(
                    (
                        user.get_full_name(),
                        'Title mismatch',
                        alesco_record['occup_pos_title'],
                        user.title
                    )
                )

        if user.expiry_date:
            if alesco_record['job_term_date'] != user.expiry_date.date():
                if key not in discrepancies:
                    discrepancies[key] = []
                discrepancies[key].append(
                    (
                        user.get_full_name(),
                        'Expiry date mismatch',
                        alesco_record['job_term_date'].strftime('%d/%b/%Y'),
                        user.expiry_date.strftime('%d/%b/%Y')
                    )
                )

        # NOTE: skip every Alesco CC starting with K (they all differ).
        if user.cost_centre and alesco_record['paypoint'] and alesco_record['paypoint'][0] != 'K':
            # If the CC in Alesco start with R or Z, remove that starting letter before comparing.
            if alesco_record['paypoint'][0] in ['R', 'Z']:
                alesco_cc = alesco_record['paypoint'][1:]
            else:
                alesco_cc = alesco_record['paypoint']
            if alesco_cc not in user.cost_centre.code:
                if key not in discrepancies:
                    discrepancies[key] = []
                discrepancies[key].append(
                    (
                        user.get_full_name(),
                        'Cost centre mismatch',
                        alesco_record['paypoint'],
                        user.cost_centre.code
                    )
                )

        if user.location and alesco_record['location_desc']:
            if alesco_record['location_desc'].lower() not in user.location.name.lower():
                if key not in discrepancies:
                    discrepancies[key] = []
                discrepancies[key].append(
                    (
                        user.get_full_name(),
                        'Location mismatch',
                        alesco_record['location_desc'],
                        user.location.name
                    )
                )
        # TODO: Manager

    with xlsxwriter.Workbook(
        fileobj,
        {
            'in_memory': True,
            'default_date_format': 'dd-mmm-yyyy HH:MM',
            'remove_timezone': True,
        },
    ) as workbook:
        sheet = workbook.add_worksheet('Discrepancies')
        sheet.write_row('A1', ('Employee ID', 'Name', 'Discrepancy type', 'Alesco database', 'IT Assets database'))
        row = 1
        for k, v in discrepancies.items():
            for issue in v:
                sheet.write_row(row, 0, [k, issue[0], issue[1], issue[2], issue[3]])
                row += 1
        sheet.set_column('A:A', 12)
        sheet.set_column('B:C', 25)
        sheet.set_column('D:E', 60)

    return fileobj


def departmentuser_csv_report():
    """Output data from all DepartmentUser objects to a CSV, unpacking the
    various JSONField values.
    Returns a BytesIO object that can be written to a response or file.
    """
    from .models import DepartmentUser
    FIELDS = [
        'email', 'username', 'given_name', 'surname', 'name', 'preferred_name', 'title',
        'name_update_reference', 'employee_id', 'active', 'telephone', 'home_phone',
        'mobile_phone', 'other_phone', 'extension', 'expiry_date', 'org_unit',
        'cost_centre', 'parent', 'executive', 'vip', 'security_clearance',
        'in_sync', 'contractor', 'ad_deleted', 'o365_licence', 'shared_account',
        'populate_primary_group', 'notes', 'working_hours', 'sso_roles', 'org_data', 'alesco_data',
        'ad_data', 'extra_data', 'date_created', 'date_ad_updated', 'date_updated', 'ad_dn',
        'ad_guid']

    # Get any DepartmentUser with non-null alesco_data field.
    # alesco_data structure should be consistent to all (or null).
    du = DepartmentUser.objects.filter(alesco_data__isnull=False)[0]
    alesco_fields = du.alesco_data.keys()
    org_fields = {
        'department': ('units', 0, 'name'),
        'tier_2': ('units', 1, 'name'),
        'tier_3': ('units', 2, 'name'),
        'tier_4': ('units', 3, 'name'),
        'tier_5': ('units', 4, 'name')
    }

    header = [f for f in FIELDS]
    # These fields appended manually:
    header.append('account_type')
    header.append('position_type')
    header += org_fields.keys()
    header += alesco_fields

    # Get any DepartmentUser with non-null org_data field for the keys.
    if DepartmentUser.objects.filter(org_data__isnull=False).exists():
        du = DepartmentUser.objects.filter(org_data__isnull=False)[0]
        cc_keys = du.org_data['cost_centre'].keys()
        header += ['cost_centre_{}'.format(k) for k in cc_keys]
        location_keys = du.org_data['location'].keys()
        header += ['location_{}'.format(k) for k in location_keys]
        header.append('secondary_location')

    # Get any DepartmentUser with non-null ad_data field for the keys.
    if DepartmentUser.objects.filter(ad_data__isnull=False).exists():
        du = DepartmentUser.objects.filter(ad_data__isnull=False)[0]
        ad_keys = du.ad_data.keys()
        if 'mailbox' in ad_keys:
            ad_keys.remove('mailbox')  # Remove the nested object.
        header += ['ad_{}'.format(k) for k in ad_keys]

    # Write data for all DepartmentUser objects to the CSV
    stream = BytesIO()
    wr = unicodecsv.writer(stream, encoding='utf-8')
    wr.writerow(header)
    for u in DepartmentUser.objects.all():
        record = []
        for f in FIELDS:
            record.append(getattr(u, f))
        try:  # Append account_type display value.
            record.append(u.get_account_type_display())
        except:
            record.append('')
        try:  # Append position_type display value.
            record.append(u.get_position_type_display())
        except:
            record.append('')
        for o in org_fields:
            try:
                src = u.org_data
                for x in org_fields[o]:
                    src = src[x]
                record.append(src)
            except:
                record.append('')

        for a in alesco_fields:
            try:
                record.append(u.alesco_data[a])
            except:
                record.append('')
        for i in cc_keys:
            try:
                record.append(u.org_data['cost_centre'][i])
            except:
                record.append('')
        for i in location_keys:
            try:
                record.append(u.org_data['location'][i])
            except:
                record.append('')
        if u.org_data and 'secondary_location' in u.org_data:
            record.append(u.org_data['secondary_location'])
        else:
            record.append('')
        for i in ad_keys:
            try:
                record.append(u.ad_data[i])
            except:
                record.append('')

        # Write the row to the CSV stream.
        wr.writerow(record)

    return stream.getvalue()


def user_account_export(fileobj, users):
    """Writes a passed-in queryset of DepartmentUser objects to a file-like object as an
    Excel spreadsheet.
    """
    with xlsxwriter.Workbook(
        fileobj,
        {
            'in_memory': True,
            'default_date_format': 'dd-mmm-yyyy HH:MM',
            'remove_timezone': True,
        },
    ) as workbook:
        users_sheet = workbook.add_worksheet('Department users')
        users_sheet.write_row('A1', (
            'ACCOUNT NAME', 'COST CENTRE', 'CONTACT NUMBER', 'OFFICE LOCATION', 'SHARED/ROLE-BASED ACCOUNT?', 'ACCOUNT ACTIVE?'
        ))
        row = 1
        for i in users:
            users_sheet.write_row(row, 0, [
                i.get_full_name(),
                i.cost_centre.code if i.cost_centre else '',
                i.telephone,
                i.location.name if i.location else '',
                i.shared_account,
                i.active,
            ])
            row += 1
        users_sheet.set_column('A:A', 30)
        users_sheet.set_column('B:B', 15)
        users_sheet.set_column('C:C', 22)
        users_sheet.set_column('D:D', 50)
        users_sheet.set_column('E:E', 29)
        users_sheet.set_column('F:F', 17)

    return fileobj
