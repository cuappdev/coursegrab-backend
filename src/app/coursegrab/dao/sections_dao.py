from . import *


def get_section_by_catalog_num(catalog_num):
    return Section.query.get(catalog_num)


def update_status_by_catalog_num(catalog_num, status):
    section = get_section_by_catalog_num(catalog_num)
    if section and section.status != status:
        section.status = status
        db.session.add(section)
        db.session.commit()
        return section
    return None


def create_sections(course, section_lst):
    sections = []
    (subject_code, course_num, title) = course
    course_id = courses_dao.create_course(subject_code, course_num, title).id

    for (catalog_num, section, status) in section_lst:
        optional_section = get_section_by_catalog_num(catalog_num)

        if optional_section:
            sections.append(optional_section)
        else:
            section = Section(catalog_num=catalog_num, section=section, status=status, course_id=course_id)
            sections.append(section)
            db.session.add(section)
    db.session.commit()
    return sections
