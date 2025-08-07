import requests
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv


class MoodleAPI:
    def __init__(self, domain: str, token: str, logger: object = None):
        load_dotenv()
        self.domain: str = os.getenv('MOODLE_DOMAIN')
        self.token: str = os.getenv('MOODLE_TOKEN')
        self.logger: object = logger

    def _create_url(self, function: str, parameters: str) -> str:
        main_url: str = f'{self.domain}/webservice/rest/server.php?wstoken={self.token}&wsfunction='
        response_format: str = 'moodlewsrestformat=json'
        if parameters:
            return f'{main_url}{function}&{parameters}&{response_format}'
        else:
            return f'{main_url}{function}&{response_format}'

    def _make_request(self, url: str) -> dict:
        try:
            response = requests.post(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            if self.logger:
                self.logger.error(f"⛔ Нет соединения с интернетом: {e}")
        except requests.exceptions.Timeout as e:
            if self.logger:
                self.logger.error(f"⛔ Превышено время ожидания запроса: {e}")
        except requests.exceptions.HTTPError as e:
            if self.logger:
                self.logger.error(f"⛔ HTTP‑ошибка при запросе: {e}")
        except ValueError as e:
            if self.logger:
                self.logger.error(f"⛔ Не удалось разобрать ответ как JSON: {e}")
        return {}

    # --- Cohort methods ---
    def get_cohorts(self) -> list:
        url: str = self._create_url('core_cohort_get_cohorts', '')
        return self._make_request(url)

    def get_cohort(self, cohort_id: int) -> dict:
        params: str = f'cohortids[0]={cohort_id}'
        url: str = self._create_url('core_cohort_get_cohorts', params)
        return self._make_request(url)

    def get_cohort_members(self, cohort_id: int) -> dict:
        params: str = f'cohortids[0]={cohort_id}'
        url: str = self._create_url('core_cohort_get_cohort_members', params)
        response = self._make_request(url)
        return response[0] if isinstance(response, list) and response else {}

    def get_cohort_teachers(self, cohort_id: int, get_cohort_members) -> List[Dict]:
        """
        Возвращает список преподавателей в когорте.
        Требует функцию get_cohort_members из MoodleAPI.
        """
        cohort_teachers = []
        cohort_members = get_cohort_members(cohort_id)
        for user in cohort_members:
            if any(role['shortname'] in ['editingteacher', 'teacher', 'manager', 'coursecreator'] for role in user.get('roles', [])):
                cohort_teachers.append(user)
        if self.logger:
            self.logger.info(f"В когорте {cohort_id} найдено преподавателей: {len(cohort_teachers)}")
        return cohort_teachers

    def update_cohort(self, cohort_id: int) -> dict:
        params: str = f'cohortids[0]={cohort_id}'
        url: str = self._create_url('core_cohort_update_cohorts', params)
        response = self._make_request(url)
        return response[0] if isinstance(response, list) and response else {}

    def search_cohorts(self, name: str) -> dict:
        params: str = f'query={name}&context[contextid]=3'
        url: str = self._create_url('core_cohort_search_cohorts', params)
        return self._make_request(url)

    def create_cohort(self, name: str, idnumber: str, description: str) -> dict:
        parameter1: str = f'cohorts[0][categorytype][type]=id'
        parameter2: str = f'&cohorts[0][categorytype][value]=1'
        parameter3: str = f'&cohorts[0][name]={name}'
        parameter4: str = f'&cohorts[0][idnumber]={idnumber}'
        parameter5: str = f'&cohorts[0][description]={description}'
        parameter6: str = f'&cohorts[0][descriptionformat]=1'
        parameters: str = parameter1 + parameter2 + parameter3 + parameter4 + parameter5 + parameter6
        url: str = self._create_url('core_cohort_create_cohorts', parameters)
        return self._make_request(url)

    def add_cohort_member(self, cohort_id: int, user_id: int) -> dict:
        parameters: str = (f'members[0][cohorttype][type]=id'
                      f'&members[0][cohorttype][value]={cohort_id}'
                      f'&members[0][usertype][type]=id'
                      f'&members[0][usertype][value]={user_id}')
        url: str = self._create_url('core_cohort_add_cohort_members', parameters)
        return self._make_request(url)

    def delete_cohort_member(self, cohort_id: int, user_id: int) -> dict:
        parameters: str = f'members[0][cohortid]={cohort_id}&members[0][userid]={user_id}'
        url: str = self._create_url('core_cohort_delete_cohort_members', parameters)
        return self._make_request(url)

    # --- Course methods ---
    def get_course_contents(self, course_id: int) -> list:
        params: str = f'courseid={course_id}'
        url: str = self._create_url('core_course_get_contents', params)
        return self._make_request(url)

    def get_course_by_id(self, course_id: int) -> Optional[dict]:
        params: str = f'options[ids][0]={course_id}'
        url: str = self._create_url('core_course_get_courses', params)
        result: str = self._make_request(url)
        return result[0] if result else None

    # --- Enrolment and User methods ---
    def get_user_courses(self, user_id: int) -> list:
        params: str = f'userid={user_id}'
        url: str = self._create_url('core_enrol_get_users_courses', params)
        return self._make_request(url)

    def get_teacher_courses(self, courses: List[Dict], user_id: int, get_enrolled_users_of_course) -> List[Dict]:
        """
        Возвращает список курсов, в которых пользователь является преподавателем/менеджером.
        Требует функцию get_enrolled_users_of_course из MoodleAPI.
        """
        teacher_courses = []
        for course in courses:
            enrolled_users = get_enrolled_users_of_course(course['id'])
            for user in enrolled_users:
                if (int(user['id']) == int(user_id) and
                    any(role['shortname'] in ['editingteacher', 'teacher', 'manager', 'coursecreator'] for role in user.get('roles', []))):
                    teacher_courses.append(course)
        if self.logger:
            self.logger.info(f"Пользователь {user_id} — преподаватель в {len(teacher_courses)} курсах.")
        return teacher_courses

    def get_enrolled_users_of_course(self, course_id: int) -> list:
        params: str = f'courseid={course_id}'
        url: str = self._create_url('core_enrol_get_enrolled_users', params)
        return self._make_request(url)

    def get_all_users(self) -> list:
        params: str = 'criteria[0][key]=lastname&criteria[0][value]=%'
        url: str = self._create_url('core_user_get_users', params)
        return self._make_request(url)

    def get_user_by_id(self, user_id: int) -> list:
        params: str = f'field=id&values[0]={user_id}'
        url: str = self._create_url('core_user_get_users_by_field', params)
        return self._make_request(url)

    # --- Quiz methods ---
    def get_tests_in_course(self, course_id: int) -> list:
        params: str = f'courseids[0]={course_id}'
        url: str = self._create_url('mod_quiz_get_quizzes_by_courses', params)
        response = self._make_request(url)
        return response.get("quizzes", []) if isinstance(response, dict) else []

    def get_attempts_by_users(self, test_id: int, course_id: int, log=None) -> list:
        logger: object = log if log else self.logger
        if logger:
            logger.info(f"🧪 Получение результатов тестирования")
        users = self.get_enrolled_users_of_course(course_id)
        attempts = []

        for user in users:
            user_id = user['id']
            fullname = user.get('fullname', f"User {user_id}")
            if logger:
                logger.info(f"🧪 Получение результатов тестирования пользователя {fullname}")

            params: str = f'quizid={test_id}&userid={user_id}'
            url: str = self._create_url('mod_quiz_get_user_attempts', params)
            response = self._make_request(url)

            if isinstance(response, dict):
                for attempt in response.get("attempts", []):
                    if attempt['state'] != 'finished':
                        if logger:
                            logger.info(f"❌ пропускаем незавершённые попытки пользователя {fullname}")
                        continue
                    from datetime import datetime
                    dt: datetime = datetime.fromtimestamp(attempt['timefinish'])
                    attempts.append({
                        'user_fullname': fullname,
                        'sumgrades': attempt.get('sumgrades'),
                        'date': dt
                    })

        return attempts

    def collect_exams_results(self, courses: list, log=None) -> list:
        logger: object = log if log else self.logger
        if logger:
            logger.info(f"📚 Получено для обработки курсов: {len(courses)}")
        for course in courses:
            tests = self.get_tests_in_course(course['id'])
            if logger:
                logger.info(f"🧪 Курс {course['fullname']} ({course['fullname']}): найдено тестов: {len(tests)}")
            test_results = []
            for test in tests:
                if logger:
                    logger.info(f"🧪 Получение результатов тестирования: Курс {course['fullname']}")
                attempts: list = self.get_attempts_by_users(test['id'], course['id'], course['fullname'], logger)
                test_results.extend(attempts)
            
        return test_results

    def extract_lectures_and_practices(self, course_contents: List[Dict]) -> List[Dict]:
        """
        Возвращает список лекций и практик из структуры курса.
        """
        results = []
        for section in course_contents:
            for module in section.get('modules', []):
                name = module.get('name', '').lower()
                if 'лекц' in name or 'практ' in name:
                    results.append({
                        'section': section.get('name'),
                        'type': module.get('modname'),
                        'name': module.get('name'),
                        'url': module.get('url'),
                    })
        if self.logger:
            self.logger.info(f"Извлечено {len(results)} лекций/практик.")
        return results







