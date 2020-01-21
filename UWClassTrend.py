import requests
from bs4 import BeautifulSoup

FALL_2010 = 1109
FALL_2013 = 1139
FALL_2019 = 1199
WINTER_2020 = 1201
UNI = 'University of Waterloo'

def extract_info(university_name, professor_name):
    url = requests.get('https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName={}&schoolID=&query={}'.format(university_name.replace(' ', '+'), professor_name.replace(' ','+')))
    html = url.text
    tid_url = ''
    soup = BeautifulSoup(html, features='lxml')
    line = soup.find_all('li', class_="listing PROFESSOR")
    if len(line) == 0:
        return 'No score found'
    line = line[0].find_all('a', href=True)
    tid_url = line[0]['href']
    if tid_url is '':
        return 'No score found'
    #print(tid_url)
    url = requests.get('https://www.ratemyprofessors.com' + str(tid_url))
    html = url.text
    soup = BeautifulSoup(html, features='lxml')
    line = soup.find_all('div', class_="RatingValue__Numerator-qw8sqy-2 gxuTRq")
    if len(line) == 0:
        return 'No score found'
    return line[0].text

def generate_terms(start, end):
    term_to_generate = start
    list_of_terms = []
    while term_to_generate <= end:
        list_of_terms.append(term_to_generate)
        term_to_generate_str = str(term_to_generate)
        if term_to_generate_str[-1] is '9':
            term_to_generate = term_to_generate + 2
        else:
            term_to_generate = term_to_generate + 4
    return list_of_terms

def read_inputs():
    level = ''
    subject = ''
    coursenum = ''
    while (level != 'U' and level != 'G'):
        print("Please enter either U for Undergradute course schedule or G for Graduate course schedule")
        level = input()
    if level is 'U':
        level = 'under'
    else:
        level = 'grad'
    print("Please enter the subject code for the course you wish to search (e.g. CS, ECON, MATH... etc)")
    subject = input()
    subject = subject.upper()
    print("Please enter the course number for the course you wish to search (e.g. 135, 101, 245, ... etc)")
    coursenum = input()
    return level, subject, coursenum

def process_requests(level, subject, coursenum):
    fall = {}
    winter = {}
    spring = {}
    term = 0
    base_url = 'https://info.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?sess='
    other_url = '&level=%s&subject=%s&cournum=%s' % (level, subject, coursenum)
    list_of_terms = generate_terms(FALL_2013, WINTER_2020)
    for sess in list_of_terms:
        url = requests.get(base_url + str(sess) + other_url)
        html = url.text
        soup = BeautifulSoup(html, features='lxml')
        line = soup.find_all('tr')
        list_of_profs = []
        for each in line:
            line2 = each.find_all('td')
            if 'LEC' in str(line2) and 'TST' not in str(line2):
                line3 = ''
                for each2 in line2:
                    line3 = each2.text
                if ',' in str(line3):
                    prof = str(line3)
                    if prof not in list_of_profs:
                        list_of_profs.append(prof)
        if term is 0:
            for prof in list_of_profs:
                if prof in fall:
                    fall[prof] = fall[prof] + 1
                else:
                    fall[prof] = 1
        elif term is 1:
            for prof in list_of_profs:
                if prof in winter:
                    winter[prof] = winter[prof] + 1
                else:
                    winter[prof] = 1
        elif term is 2:
            for prof in list_of_profs:
                if prof in spring:
                    spring[prof] = spring[prof] + 1
                else:
                    spring[prof] = 1
        else:
            print("NO")
        term = (term + 1) % 3

    print('Here\'s the trend of ' + subject + coursenum + ' from Fall 2013 to Winter 2020')
    print('\n' + 'FALL: ' + '\n')
    for prof in sorted(fall, key=fall.get, reverse=True):
        prof_split = prof.split(',')
        score = extract_info(UNI, prof_split[1] + ' ' + prof_split[0])
        print(prof + ' : ' + str(fall[prof]) + '(' + str(score) + ')')
    print('\n' + 'WINTER: ' + '\n')
    for prof in sorted(winter, key=winter.get, reverse=True):
        prof_split = prof.split(',')
        score = extract_info(UNI, prof_split[1] + ' ' + prof_split[0])
        print(prof + ' : ' + str(winter[prof]) + '(' + str(score) + ')')
    print('\n' + 'SPRING: ' + '\n')
    for prof in sorted(spring, key=spring.get, reverse=True):
        prof_split = prof.split(',')
        score = extract_info(UNI, prof_split[1] + ' ' + prof_split[0])
        print(prof + ' : ' + str(spring[prof]) + '(' + str(score) + ')')
    
def main():
    level, subject, coursenum = read_inputs()
    process_requests(level, subject, coursenum)

if __name__ == "__main__":
    main()
