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


def scrape_classes():
    semester = current_semester()
    catalog_tuples = []
    # Iterate through each subject
    for subject_code in all_subject_codes():
        subject_req = requests.get(ROOT_URL + "/browse/roster/" + semester + "/subject/" + subject_code)
        subject_bs4 = bs4.BeautifulSoup(subject_req.text, "html.parser")
        course_tags = subject_bs4.find_all("div", class_="node")
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
                schedule = []
                if days_tag:
                    schedule.append(days_tag[0].getText().strip())
                if time_tag:
                    schedule.append(time_tag[0].getText().strip())
                section += " / " + (" ".join(schedule) if time_tag else "TBA")  # section type + section number + time

                catalog_tag = section_tag.find_all("strong", class_="tooltip-iws")[0]
                catalog_num = int(catalog_tag.getText().strip())

                open_status = section_tag.find_all("li", class_="open-status")[0].contents[0].contents[0]["class"][-1]
                status = INVALID
                if "open-status-open" in open_status:
                    status = OPEN
                if "open-status-closed" in open_status:
                    status = CLOSED
                if "open-status-warning" in open_status:
                    status = WAITLISTED
                if "open-status-archive" in open_status:
                    status = ARCHIVED

                sections_arr.append((catalog_num, section, status))
            catalog_tuples.append((course, sections_arr))
    return catalog_tuples


if __name__ == "__main__":
    print(scrape_classes())
