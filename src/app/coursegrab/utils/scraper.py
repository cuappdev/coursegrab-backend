import bs4
import requests
import threading
from datetime import datetime
from app.coursegrab.dao import courses_dao, sections_dao, semesters_dao
from app.coursegrab.utils.constants import OPEN, CLOSED, WAITLISTED, ARCHIVED, INVALID, ROOT_URL
from app.coursegrab.notifications.push_notifications import notify_users

on_startup = True


def start_update():
    global on_startup
    try:
        print("[{0}] Updating course statuses".format(datetime.now()))
        try:
            if not on_startup:
                updated_sections = update_all_statuses()
                for section in updated_sections:
                    notify_users(section)
            else:
                on_startup = False
                threading.Thread(None, refresh_classes).start()
        except:
            pass
    finally:
        # Scrape every 20 minutes as requested by CIT
        # TODO: Switch from webscraping to the API detailed below
        # https://classes.cornell.edu/content/SP22/api-details
        threading.Timer(60 * 20, start_update).start()


def refresh_classes():
    try:
        print("[{0}] Checking for new semester".format(datetime.now()))
        tracking = semesters_dao.get_current_semester()
        current = current_semester()

        # new semester in roster
        if tracking is None or tracking != current:
            print("[{0}] Clearing information from previous semester".format(datetime.now()))
            courses_dao.clear_table()
            sections_dao.clear_table()
            semesters_dao.update_current_semester(current)

        try:
            print("[{0}] Scraping classes".format(datetime.now()))
            catalog_tuples = scrape_classes()
            for course, sections in catalog_tuples:
                sections_dao.create_sections(course, sections)
        except:
            pass
    finally:
        threading.Timer(60 * 60 * 24, refresh_classes).start()


def current_semester():
    req = requests.get(ROOT_URL)
    req.raise_for_status()
    return req.url.strip("/").split("/")[-1]


def all_subject_codes():
    req = requests.get(ROOT_URL)
    roster_bs4 = bs4.BeautifulSoup(req.text, "html.parser")
    subject_tags = roster_bs4.select(".browse-subjectcode")
    return [str(tag.getText()) for tag in subject_tags]


def scrape_classes():
    semester = current_semester()
    catalog_tuples = []
    # Iterate through each subject
    for subject_code in all_subject_codes():
        subject_req = requests.get(ROOT_URL + "/browse/roster/" + semester + "/subject/" + subject_code)
        subject_bs4 = bs4.BeautifulSoup(subject_req.text, "html.parser")
        course_tags = subject_bs4.find_all("div", class_="node")
        if len(course_tags) == 0:
            continue
        course_tags.pop(0)

        # Iterate through each course
        for tag in course_tags:
            course_num = tag["data-catalog-nbr"]
            course_title = tag.find_all("div", class_="title-coursedescr")[0].getText()
            course = (subject_code, course_num, course_title)

            section_tags = tag.find_all("ul", class_="section")
            sections_arr = []

            # Iterate through each section
            for section_tag in section_tags:
                section = str(section_tag["aria-label"]).replace(
                    "Class Section ", ""
                )  # Get section type + section number
                pattern = section_tag.find_all("li", class_="meeting-pattern")[0]
                days_tag = pattern.find_all("span", class_="pattern-only")
                time_tag = pattern.find_all("time", class_="time")
                mode_tag = section_tag.find_all("span", class_="instr-mode")
                mode = mode_tag[0].getText()[18:] if mode_tag else None  # Exclude "Instruction Mode: "
                schedule = []
                if days_tag:
                    schedule.append(days_tag[0].getText().strip())
                if time_tag:
                    time = time_tag[0].getText()
                    end_index = time.find("-")
                    schedule.append(time[:end_index].strip())
                section += " / " + (" ".join(schedule) if time_tag else "TBA")  # section type + section number + time

                catalog_tag = section_tag.find_all("strong", class_="tooltip-iws")[0]
                catalog_num = int(catalog_tag.getText().strip())

                instructor_tag = pattern.find_all("li", class_="instructors")
                instructors = []
                if instructor_tag:
                    for p in instructor_tag[0].find_all("p"):
                        name = p.find("span").get("data-content") if p.find("span") else p.text
                        instructors.append(name)
                instructor_str = ",".join(instructors) if instructors else None

                open_status = section_tag.find_all("li", class_="open-status")[0].find_all("span")[0].contents[0]["class"][-1]
                status = INVALID
                if "open-status-open" in open_status:
                    status = OPEN
                if "open-status-closed" in open_status:
                    status = CLOSED
                if "open-status-warning" in open_status:
                    status = WAITLISTED
                if "open-status-archive" in open_status:
                    status = ARCHIVED

                sections_arr.append((catalog_num, section, status, instructor_str, mode))
            catalog_tuples.append((course, sections_arr))
    return catalog_tuples


def update_all_statuses():
    semester = current_semester()
    updated_sections = []
    # Iterate through each subject
    for subject_code in all_subject_codes():
        subject_req = requests.get(ROOT_URL + "/browse/roster/" + semester + "/subject/" + subject_code)
        subject_bs4 = bs4.BeautifulSoup(subject_req.text, "html.parser")
        course_tags = subject_bs4.find_all("div", class_="node")
        if len(course_tags) == 0:
            continue
        course_tags.pop(0)

        # Iterate through each course
        for tag in course_tags:
            section_tags = tag.find_all("ul", class_="section")

            # Iterate through each section
            for section_tag in section_tags:
                catalog_tag = section_tag.find_all("strong", class_="tooltip-iws")[0]
                catalog_num = int(catalog_tag.getText().strip())

                open_status = section_tag.find_all("li", class_="open-status")[0].find_all("span")[0].contents[0]["class"][-1]
                status = INVALID
                if "open-status-open" in open_status:
                    status = OPEN
                if "open-status-closed" in open_status:
                    status = CLOSED
                if "open-status-warning" in open_status:
                    status = WAITLISTED
                if "open-status-archive" in open_status:
                    status = ARCHIVED
                updated_section = sections_dao.update_status_by_catalog_num(catalog_num, status)
                if updated_section and status == OPEN:
                    updated_sections.append(updated_section)
    return updated_sections
