import requests
import bs4

ROOT_URL = "https://classes.cornell.edu"


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
            section = str(tag.parent.parent.parent["aria-label"]).strip("Class Section ")
            catalog_tuples.append((subject_code, course_num, title, catalog_num, section))
    return catalog_tuples()


if __name__ == "__main__":
    scrape_classes()
