"""
create table public.vacancies
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        # Накат миграции
        """
        CREATE TABLE IF NOT EXISTS public.vacancies (
            id BIGSERIAL PRIMARY KEY,
            vacancy_id INTEGER NOT NULL UNIQUE,
	        title VARCHAR(255) NOT NULL,
	        url VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # Откат миграции
        "DROP TABLE public.vacancies;"
    )
]
