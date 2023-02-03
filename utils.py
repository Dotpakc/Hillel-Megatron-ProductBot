import os
import json

def get_courses() -> dict:
    courses = {}
    try:
        for file in os.listdir('courses'):
            print(file)
            with open(f'courses/{file}/course.json', 'r', encoding="utf-8") as f:
                courses[file] = json.load(f)
    except FileNotFoundError:
        сourses = {"error": {"name":"ERROR FILES"}}
        print("ERROR FILES")
    return courses


#Cчитуємо фото з курса 
# Наприклад: 
# courses/python/course.jpg
# courses/python/course.png
# Зробити перевірку на розширення файлу
def get_photo(course):
    for file in os.listdir(f'courses/{course}'):
        if file.endswith('.jpg') or file.endswith('.png'):
            with open(f'courses/{course}/{file}', 'rb') as f:
                return f.read()