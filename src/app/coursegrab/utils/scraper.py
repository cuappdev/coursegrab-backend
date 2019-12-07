import requests
import bs4
from app.coursegrab.utils.constants import OPEN, CLOSED, WAITLISTED, ARCHIVED, INVALID, ROOT_URL


def current_semester():
    req = requests.get(ROOT_URL)
    req.raise_for_status()
    return req.url.strip("/").split("/")[-1]


def all_subject_codes():
    req = requests.get(ROOT_URL)
    roster_bs4 = bs4.BeautifulSoup(req.text, "html.parser")
    subject_tags = roster_bs4.select(".browse-subjectcode")
    return [str(tag.getText()) for tag in subject_tags]


def get_course_status(subject_code, catalog_num):
    semester = current_semester()
    subject_req = requests.get(ROOT_URL + "/browse/roster/" + semester + "/subject/" + subject_code)
    subject_req.raise_for_status()
    subject_bs4 = bs4.BeautifulSoup(subject_req.text, "html.parser")
    catalog_tags = subject_bs4.find_all("strong", class_="tooltip-iws")
    for tag in catalog_tags:
        catalog_code = int(tag.getText().strip())
        if catalog_code == catalog_num:
            section = tag.parent.parent.parent
            status = section.find_all("li", class_="open-status")[0].contents[0].contents[0]["class"][-1]
            if "open-status-open" in status:
                return OPEN
            if "open-status-closed" in status:
                return CLOSED
            if "open-status-warning" in status:
                return WAITLISTED
            if "open-status-archive" in status:
                return ARCHIVED
    return INVALID


def scrape_classes():
    semester = current_semester()
    catalog_tuples = []
    for subject_code in all_subject_codes():
        subject_req = requests.get(ROOT_URL + "/browse/roster/" + semester + "/subject/" + subject_code)
        subject_bs4 = bs4.BeautifulSoup(subject_req.text, "html.parser")
        catalog_tags = subject_bs4.find_all("strong", class_="tooltip-iws")
        for tag in catalog_tags:
            catalog_num = int(tag.getText().strip())
            course_num = int("".join([x for x in tag.next_sibling.getText() if x.isdigit()]))
            title = tag.parent.parent.parent.parent.parent.parent.find_all("div", class_="title-coursedescr")[
                0
            ].getText()
            section = str(tag.parent.parent.parent["aria-label"]).replace("Class Section ", "")

            pattern = tag.parent.parent.parent.find_all("li", class_="meeting-pattern")[0]
            days_tag = pattern.find_all("span", class_="pattern-only")
            time_tag = pattern.find_all("time", class_="time")
            schedule = []
            if days_tag:
                schedule.append(days_tag[0].getText().strip())
            if time_tag:
                schedule.append(time_tag[0].getText().strip())
            section += " / " + (" ".join(schedule) if time_tag else "TBA")

            catalog_tuples.append((subject_code, course_num, title, catalog_num, section))
    return catalog_tuples


if __name__ == "__main__":
    print(scrape_classes())
